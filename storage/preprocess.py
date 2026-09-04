# -*- coding: utf-8 -*-
"""
storage/preprocess.py —— 数据预处理模块（成员2）
=================================================
输入：data/raw/202607-citibike-tripdata.csv（download_data.py 的合并输出）
输出：data/clean_citibike.csv（docs/data_dict.md 第四节的统一标准表）

清洗规则（与 docs/data_dict.md 第五节一致）：
  1. 字段归一（config.RAW_ALIASES）
  2. 会员值归一（config.USER_TYPE_MAP）
  3. 时间解析，失败置 NaT 后剔除
  4. 时长补算：ended_at - started_at（2026 新格式无 tripduration）
  5. 异常过滤：60s <= 时长 <= 24h，剔除起讫站缺失/经纬度越界的行
  6. 抽样：SAMPLE_SIZE 条，random_state=42 可复现
  7. 派生特征：start_date / hour / weekday / is_weekend
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def _normalize_columns(df):
    """按 config.RAW_ALIASES 把原始表头归一为标准列名。"""
    rename = {}
    for canon, aliases in config.RAW_ALIASES.items():
        for a in aliases:
            if a in df.columns:
                rename[a] = canon
                break
    return df.rename(columns=rename)


def _clean_chunk(df):
    """对一个数据块执行完整清洗，返回清洗后的块（可能为空）。"""
    df = _normalize_columns(df)

    # 必需列检查（起讫时间、起讫站）
    required = ["start_time", "end_time", "start_station", "end_station"]
    for c in required:
        if c not in df.columns:
            raise RuntimeError(f"[preprocess] 原始数据缺少必需字段: {c}")

    # 3. 时间解析
    df["start_time"] = pd.to_datetime(df["start_time"], errors="coerce")
    df["end_time"] = pd.to_datetime(df["end_time"], errors="coerce")

    # 4. 时长补算（秒）
    if "ride_duration" not in df.columns or df["ride_duration"].isna().all():
        df["ride_duration"] = (df["end_time"] - df["start_time"]).dt.total_seconds()
    else:
        df["ride_duration"] = pd.to_numeric(df["ride_duration"], errors="coerce")
        df["ride_duration"] = df["ride_duration"].fillna(
            (df["end_time"] - df["start_time"]).dt.total_seconds())

    # 2. 会员值归一（member/casual -> Subscriber/Customer）
    if "user_type" in df.columns:
        df["user_type"] = (df["user_type"].astype(str).str.strip().str.lower()
                           .map(config.USER_TYPE_MAP).fillna("Unknown"))
    else:
        df["user_type"] = "Unknown"

    # 车辆类型归一（对齐成员2 cleaning/preprocess.py 规则）
    if "rideable_type" in df.columns:
        df["rideable_type"] = (df["rideable_type"].astype(str).str.strip()
                               .str.lower()
                               .replace({"classic_bike": "classic",
                                         "electric_bike": "electric",
                                         "docked_bike": "docked"}))

    # 5. 异常过滤
    mask = (
        df["start_time"].notna() & df["end_time"].notna()
        & df["ride_duration"].between(config.MIN_DURATION, config.MAX_DURATION)
        & df["start_station"].notna() & df["end_station"].notna()
        & (df["start_station"].str.strip() != "")
        & df["start_lat"].notna() & df["start_lng"].notna()
    )
    # 经纬度合理范围（纽约附近，宽松起见 0<lat<90, -180<lng<180）
    mask &= df["start_lat"].between(0, 90) & df["start_lng"].between(-180, 180)

    df = df.loc[mask].copy()

    # 7. 派生特征
    df["start_date"] = df["start_time"].dt.date
    df["hour"] = df["start_time"].dt.hour
    df["weekday"] = df["start_time"].dt.weekday
    df["is_weekend"] = (df["weekday"] >= 5).astype(int)

    # 只保留标准表列
    keep = ["ride_duration", "start_time", "end_time", "start_station",
            "end_station", "start_lat", "start_lng", "end_lat", "end_lng",
            "user_type", "rideable_type", "start_date", "hour", "weekday",
            "is_weekend"]
    keep = [c for c in keep if c in df.columns]
    return df[keep]


def run(sample_size=None):
    """分块读取原始大文件 -> 清洗 -> 抽样 -> 落盘。返回抽样后的 DataFrame。"""
    sample_size = sample_size or config.SAMPLE_SIZE
    raw_file = config.RAW_DATA_FILE
    if not os.path.exists(raw_file):
        raise RuntimeError(
            f"[preprocess] 找不到原始数据 {raw_file}，请先运行 python download_data.py")

    print(f"[preprocess] 读取原始数据: {raw_file}")
    chunks, total_rows, kept_rows = [], 0, 0
    reader = pd.read_csv(raw_file, chunksize=500_000, encoding="utf-8-sig",
                         low_memory=False)
    for chunk in reader:
        total_rows += len(chunk)
        cleaned = _clean_chunk(chunk)
        kept_rows += len(cleaned)
        chunks.append(cleaned)
        print(f"[preprocess] 已处理 {total_rows:,} 行，有效 {kept_rows:,} 行")

    full = pd.concat(chunks, ignore_index=True)
    del chunks
    print(f"[preprocess] 原始 {total_rows:,} 行 -> 有效 {kept_rows:,} 行"
          f"（剔除率 {1 - kept_rows / max(total_rows, 1):.1%}）")

    # 6. 抽样（固定种子可复现）
    if sample_size and len(full) > sample_size:
        full = full.sample(n=sample_size, random_state=config.RANDOM_STATE)
        full = full.sort_values("start_time").reset_index(drop=True)
        print(f"[preprocess] 抽样 {sample_size:,} 条用于分析")

    # 8. 落盘
    out = full.copy()
    out["start_date"] = out["start_date"].astype(str)
    out.to_csv(config.CLEAN_DATA_FILE, index=False, encoding="utf-8-sig")
    print(f"[preprocess] 清洗后标准表已保存: {config.CLEAN_DATA_FILE}")
    return full


if __name__ == "__main__":
    run()
