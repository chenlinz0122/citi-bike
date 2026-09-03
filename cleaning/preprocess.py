# -*- coding: utf-8 -*-
"""
cleaning/preprocess.py —— 数据清洗模块
========================================
把 raw/ 目录下的 Citi Bike 官方原始分片数据清洗为统一标准表。

输  入：raw/*.csv（2026 新格式，5 个分片，字段含 ride_id / member_casual 等）
输  出：cleaned/clean_citibike.csv（统一列名、统一类型、统一取值）

清洗规则（严格对齐 docs/data_dict.md 第五节）：
  1. 字段归一：原始表头 -> 标准列名
  2. 会员值归一：member->Subscriber，casual->Customer
  3. 车辆类型归一：classic_bike->classic，electric_bike->electric
  4. 时间解析：started_at/ended_at -> datetime64，无法解析置 NaT
  5. 时长补算：2026 新格式无 tripduration，用 ended_at - started_at 计算（秒）
  6. 异常过滤：仅保留 60 秒 <= 时长 <= 24 小时
  7. 抽样：默认 200000 条，固定 random_state=42（--sample 0 表示不抽样）
  8. 派生特征：start_date / hour / weekday / is_weekend
  9. 落盘：cleaned/clean_citibike.csv，utf-8-sig，index=False

用  法：
    python cleaning/preprocess.py                # 默认抽样 20 万条
    python cleaning/preprocess.py --sample 0     # 不抽样，输出全量
"""

import argparse
import glob
import os

import pandas as pd

# ----------------------------------------------------------------------
# 路径配置（项目根目录 = 本文件上两级）
# ----------------------------------------------------------------------
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DIR = os.path.join(BASE_DIR, "raw")          # 原始分片数据目录
CLEANED_DIR = os.path.join(BASE_DIR, "cleaned")  # 清洗结果目录
CLEAN_FILE = os.path.join(CLEANED_DIR, "clean_citibike.csv")

# ----------------------------------------------------------------------
# 清洗参数
# ----------------------------------------------------------------------
# 原始表头 -> 标准列名（2026 新格式）
RENAME_MAP = {
    "ride_id":             "bikeid",
    "rideable_type":       "rideable_type",
    "started_at":          "start_time",
    "ended_at":            "end_time",
    "start_station_name":  "start_station",
    "end_station_name":    "end_station",
    "start_lat":           "start_lat",
    "start_lng":           "start_lng",
    "end_lat":             "end_lat",
    "end_lng":             "end_lng",
    "member_casual":       "user_type",
}

USER_TYPE_MAP = {"member": "Subscriber", "casual": "Customer"}

RIDEABLE_TYPE_MAP = {"classic_bike": "classic", "electric_bike": "electric"}

MIN_DURATION = 60                 # 最小有效时长（秒），剔除假启动
MAX_DURATION = 24 * 3600          # 最大有效时长（秒），剔除异常长骑行
SAMPLE_SIZE = 200000              # 抽样条数（0 = 不抽样）
RANDOM_STATE = 42                 # 固定随机种子，保证可复现

# 清洗后统一表的标准列（顺序对齐 docs/data_dict.md 第四节）
CANONICAL_COLUMNS = [
    "ride_duration", "start_time", "end_time",
    "start_station", "end_station",
    "start_lat", "start_lng", "end_lat", "end_lng",
    "user_type", "bikeid", "rideable_type",
    "start_date", "hour", "weekday", "is_weekend",
]


def _clean_shard(path):
    """读取并清洗单个原始分片，返回清洗后的 DataFrame。"""
    df = pd.read_csv(path, low_memory=False)

    # 1) 字段归一：只保留标准列（丢弃 station_id 等契约外字段）
    df = df.rename(columns=RENAME_MAP)
    df = df[[c for c in RENAME_MAP.values()]]

    # 2) 时间解析
    df["start_time"] = pd.to_datetime(df["start_time"], errors="coerce")
    df["end_time"] = pd.to_datetime(df["end_time"], errors="coerce")

    # 3) 时长补算（秒）
    df["ride_duration"] = (df["end_time"] - df["start_time"]).dt.total_seconds()

    # 4) 枚举字段归一
    df["user_type"] = df["user_type"].map(USER_TYPE_MAP)
    df["rideable_type"] = (
        df["rideable_type"].map(RIDEABLE_TYPE_MAP).fillna(df["rideable_type"])
    )

    # 5) 经纬度数值化
    for c in ("start_lat", "start_lng", "end_lat", "end_lng"):
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # 6) 异常过滤：时长范围 + 时间/经纬度有效
    df = df[(df["ride_duration"] >= MIN_DURATION)
            & (df["ride_duration"] <= MAX_DURATION)]
    df = df.dropna(subset=["start_time", "end_time"])

    return df


def run(sample_size=SAMPLE_SIZE):
    """执行全流程清洗，返回清洗后的 DataFrame。"""
    files = sorted(glob.glob(os.path.join(RAW_DIR, "*.csv")))
    if not files:
        raise FileNotFoundError(f"raw/ 目录下未找到任何 .csv 文件：{RAW_DIR}")

    print(f"[清洗] 发现 {len(files)} 个原始分片：")
    for f in files:
        print(f"       {os.path.basename(f)}")

    # 逐个分片清洗后合并
    frames = [_clean_shard(f) for f in files]
    df = pd.concat(frames, ignore_index=True)
    raw_rows = len(df)
    print(f"[清洗] 分片合并 + 异常过滤后：{raw_rows:,} 条")

    # 7) 抽样（固定随机种子，可复现）
    if sample_size and len(df) > sample_size:
        df = df.sample(n=sample_size, random_state=RANDOM_STATE)
        print(f"[清洗] 抽样 {sample_size:,} 条（random_state={RANDOM_STATE}）")

    # 8) 派生特征
    df["start_date"] = df["start_time"].dt.normalize()      # 出发日期（零点）
    df["hour"] = df["start_time"].dt.hour                   # 出发小时 0-23
    df["weekday"] = df["start_time"].dt.weekday             # 0=周一 … 6=周日
    df["is_weekend"] = (df["weekday"] >= 5).astype(int)     # 0=工作日 1=周末

    # 统一列顺序
    df = df[CANONICAL_COLUMNS]

    # 9) 落盘
    os.makedirs(CLEANED_DIR, exist_ok=True)
    df.to_csv(CLEAN_FILE, index=False, encoding="utf-8-sig")

    print(f"[清洗] 已输出干净表：{CLEAN_FILE}")
    print(f"[清洗] 最终记录数：{len(df):,} 条")
    return df


def main():
    p = argparse.ArgumentParser(description="Citi Bike 数据清洗脚本")
    p.add_argument("--sample", type=int, default=SAMPLE_SIZE,
                   help=f"抽样条数，0 表示不抽样（默认 {SAMPLE_SIZE}）")
    args = p.parse_args()

    df = run(sample_size=args.sample)

    print("\n" + "=" * 60)
    print("[完成] 清洗结果概览")
    print("=" * 60)
    print(df.dtypes.to_string())
    print("\n前 3 行预览：")
    print(df.head(3).to_string())


if __name__ == "__main__":
    main()
