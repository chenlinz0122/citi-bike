# -*- coding: utf-8 -*-
"""
analysis/analysis.py —— 描述统计与时空分析模块（成员3）
=========================================================
输入：data/clean_citibike.csv（成员2预处理输出的统一标准表）
输出：
  - output/统计结果.txt              描述统计与时空规律文本报告
  - output/station_summary.csv       站点级汇总表（供可视化/聚类使用）
  - output/统计结果汇总表.csv / 热门借车站点.csv / 热门还车站点.csv /
    每小时骑行量.csv / 月度骑行趋势.csv   各统计表

运行：main.py 步骤2 调用本模块；也可单独执行 python -m analysis.analysis
"""

import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def _load():
    if not os.path.exists(config.CLEAN_DATA_FILE):
        raise RuntimeError(
            f"[analysis] 找不到清洗数据 {config.CLEAN_DATA_FILE}，请先运行 storage/preprocess.py")
    return pd.read_csv(config.CLEAN_DATA_FILE, encoding="utf-8-sig")


def hot_stations(df, top_n=10):
    """热门借/还车站点 TopN，返回 (start_series, end_series)。"""
    start = df["start_station"].value_counts().head(top_n)
    end = df["end_station"].value_counts().head(top_n)
    return start, end


def station_summary(df):
    """站点级汇总（次数/平均时长/经纬度），供可视化与聚类使用。"""
    g = df.groupby("start_station").agg(
        total_trips=("start_station", "count"),
        avg_duration=("ride_duration", "mean"),
        start_lat=("start_lat", "first"),
        start_lng=("start_lng", "first"),
    ).reset_index()
    g.columns = ["station_name", "total_trips", "avg_duration", "start_lat", "start_lng"]
    g = g.sort_values("total_trips", ascending=False).reset_index(drop=True)
    out = os.path.join(config.OUTPUT_DIR, "station_summary.csv")
    g.to_csv(out, index=False, encoding="utf-8-sig")
    print(f"[analysis] 站点汇总表已保存: {out}")
    return g


def run():
    """完整统计分析：描述统计 + 时空规律 + 统计表输出。"""
    df = _load()
    df_clean = df[df["ride_duration"] >= 60].copy()
    total = len(df_clean)

    # ---- 1. 描述统计 ----
    duration_mean = df_clean["ride_duration"].mean() / 60.0        # 分钟
    duration_median = df_clean["ride_duration"].median() / 60.0    # 分钟
    user_pct = df_clean["user_type"].value_counts(normalize=True) * 100
    weekday_rides = int((df_clean["is_weekend"] == 0).sum())
    weekend_rides = int((df_clean["is_weekend"] == 1).sum())
    hourly = df_clean["hour"].value_counts().sort_index()
    hourly_sorted = hourly.sort_values(ascending=False)
    top_start, top_end = hot_stations(df_clean)
    monthly = (pd.to_datetime(df_clean["start_time"]).dt.strftime("%Y-%m")
               .value_counts().sort_index())

    # ---- 2. 写 统计结果.txt ----
    lines = [
        "纽约公共自行车数据分析 —— 统计分析结果",
        "=" * 46,
        f"数据文件：{config.CLEAN_DATA_FILE}",
        f"样本量：{total:,} 条",
        "",
        "【骑行时长】",
        f"  平均时长：{duration_mean:.1f} 分钟（{duration_mean * 60:.0f} 秒）",
        f"  中位数：{duration_median:.1f} 分钟",
        "",
        "【用户类型占比】",
    ]
    for user, pct in user_pct.items():
        lines.append(f"  {user}：{pct:.1f}%")
    lines += [
        "",
        "【工作日 vs 周末】",
        f"  工作日骑行量：{weekday_rides:,} 条",
        f"  周末骑行量：{weekend_rides:,} 条（{weekend_rides / total * 100:.1f}%）",
        "",
        "【高峰时段 TOP5】",
    ]
    for hour, count in hourly_sorted.head(5).items():
        lines.append(f"  {hour:02d}:00 —— {count:,} 次")
    lines += ["", "【热门借车站点 TOP5】"]
    for i, (st, c) in enumerate(top_start.head(5).items(), 1):
        lines.append(f"  {i}. {st}：{c:,} 次")
    lines += ["", "【热门还车站点 TOP5】"]
    for i, (st, c) in enumerate(top_end.head(5).items(), 1):
        lines.append(f"  {i}. {st}：{c:,} 次")
    lines += ["", "【月度骑行趋势】"]
    for m, c in monthly.items():
        lines.append(f"  {m}：{c:,} 次")

    stats_path = os.path.join(config.OUTPUT_DIR, "统计结果.txt")
    with open(stats_path, "w", encoding="utf-8-sig") as f:
        f.write("\n".join(lines))
    print(f"[analysis] 统计结果已保存: {stats_path}")

    # ---- 3. 统计表（CSV） ----
    pd.DataFrame({
        "指标": ["总骑行次数", "平均时长(分钟)", "中位数时长(分钟)",
                 "工作日骑行量", "周末骑行量"],
        "数值": [total, round(duration_mean, 1), round(duration_median, 1),
                weekday_rides, weekend_rides],
    }).to_csv(os.path.join(config.OUTPUT_DIR, "统计结果汇总表.csv"),
              index=False, encoding="utf-8-sig")
    top_start.to_csv(os.path.join(config.OUTPUT_DIR, "热门借车站点.csv"), encoding="utf-8-sig")
    top_end.to_csv(os.path.join(config.OUTPUT_DIR, "热门还车站点.csv"), encoding="utf-8-sig")
    hourly.to_csv(os.path.join(config.OUTPUT_DIR, "每小时骑行量.csv"), encoding="utf-8-sig")
    monthly.to_csv(os.path.join(config.OUTPUT_DIR, "月度骑行趋势.csv"), encoding="utf-8-sig")

    # ---- 4. 站点汇总 ----
    station_summary(df_clean)

    print(f"[analysis] 完成：{total:,} 条记录，平均 {duration_mean:.1f} 分钟，"
          f"高峰时段 {int(hourly_sorted.index[0]):02d}:00")
    return df


if __name__ == "__main__":
    run()
