# -*- coding: utf-8 -*-
"""
preprocess.py —— 数据预处理模块（成员2负责）
==============================================
职责：
  1. 读取原始 Citi Bike CSV（自动兼容新旧字段名）
  2. 处理缺失值、将时间转为 datetime
  3. 过滤异常（时长<60秒、>24小时）
  4. 按需抽样（控制数据规模）
  5. 构造新特征：日期、小时、是否工作日等
  6. 输出清洗后的干净数据 clean_citibike.csv

若 data/ 下没有真实数据且启用了兜底，则自动用示例数据。
"""

import os
import sys
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def _normalize_columns(df):
    """
    把不同版本的 Citi Bike 字段名统一成标准列名。
    返回: 统一列名后的 DataFrame
    """
    # 建一个 原始列名->标准名 的映射
    mapping = {}
    for std, aliases in config.RAW_ALIASES.items():
        for alias in aliases:
            if alias in df.columns:
                mapping[alias] = std
    return df.rename(columns=mapping)


def load_raw():
    """
    加载原始数据。优先真实文件；不存在或为空时，用示例数据兜底。

    返回:
        (df, source)  df 是数据表，source 是 'real' 或 'sample'
    """
    if os.path.exists(config.RAW_DATA_FILE):
        try:
            df = pd.read_csv(config.RAW_DATA_FILE)
            df = _normalize_columns(df)
            if len(df) > 0:
                return df, "real"
        except Exception as e:
            print(f"[预处理] 读取真实数据失败：{e}")

    if config.USE_SAMPLE_FALLBACK:
        from storage.sample_data import gen_sample_data
        df = gen_sample_data()
        df = _normalize_columns(df)
        print("[预处理] 未找到真实数据，使用示例数据(演示全流程)")
        return df, "sample"

    raise FileNotFoundError("未找到数据文件，且已禁用示例兜底")


def _clean(df):
    """
    数据清洗核心：
      - 时间字符串 -> datetime
      - 过滤异常时长
      - 构造新特征(小时/日期/是否工作日/是否周末)
    """
    # 统一或补全骑行时长：若非数值，则用起止时间差
    if "ride_duration" not in df.columns:
        df["ride_duration"] = np.nan
    df["ride_duration"] = pd.to_numeric(df["ride_duration"], errors="coerce")

    # 时间字符串转为 datetime
    for col in ("start_time", "end_time"):
        if col not in df.columns:
            df[col] = pd.NaT
        df[col] = pd.to_datetime(df[col], errors="coerce")

    # 若时长缺失但起止时间都有，用时间差(秒)补
    mask = df["ride_duration"].isna()
    if mask.any():
        try:
            delta = (df.loc[mask, "end_time"] - df.loc[mask, "start_time"]).dt.total_seconds()
            df.loc[mask, "ride_duration"] = delta
        except Exception:
            pass

    # 过滤异常时长
    df = df[(df["ride_duration"] >= config.MIN_DURATION)
            & (df["ride_duration"] <= config.MAX_DURATION)]

    # ---- 构造新特征 ----
    df["start_date"] = df["start_time"].dt.date
    df["hour"] = df["start_time"].dt.hour
    df["weekday"] = df["start_time"].dt.weekday            # 0=周一
    df["is_weekend"] = df["weekday"].apply(lambda w: 1 if w >= 5 else 0)

    # 会员类型标准化（统一为 Subscriber/Customer 的规则见 docs/data_dict.md）
    if "user_type" in df.columns:
        df["user_type"] = df["user_type"].astype(str).str.strip()

    return df


def _sample(df):
    """按配置抽样控制规模；SAMPLE_SIZE=0 表示不抽样"""
    if config.SAMPLE_SIZE and len(df) > config.SAMPLE_SIZE:
        df = df.sample(n=config.SAMPLE_SIZE, random_state=config.RANDOM_STATE)
    return df


def run(output_path=None):
    """
    预处理主流程：加载 -> 清洗 -> 抽样 -> 保存。
    返回: 清洗后的 DataFrame
    """
    df, source = load_raw()
    df = _clean(df)
    df = _sample(df)

    out = output_path or config.CLEAN_DATA_FILE
    df.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"[预处理] 清洗完成：{len(df)} 条有效记录 -> {out}（来源: {source}）")
    return df


if __name__ == "__main__":
    d = run()
    print("\n数据预览（前5行）：")
    print(d.head())
    print("\n字段：", list(d.columns))