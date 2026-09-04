# -*- coding: utf-8 -*-
"""
analysis/analysis.py —— 描述统计与时空分析模块（成员3）
=======================================================
输入：清洗后标准表（preprocess.run() 的返回值 或 data/clean_citibike.csv）
输出：output/统计结果.txt、output/station_summary.csv
"""

import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


# ----------------------------------------------------------------------
# 供 main.py / visualization 调用的接口
# ----------------------------------------------------------------------
def hot_stations(df, topn=10):
    """返回 (热门起点站TOP N系列, 热门终点站TOP N系列)。"""
    top_start = df["start_station"].value_counts().head(topn)
    top_end = df["end_station"].value_counts().head(topn)
    return top_start, top_end


def station_summary(df):
    """按起点站聚合：骑行量、平均时长（分钟）、会员占比、经纬度 -> DataFrame。"""
    g = df.groupby("start_station").agg(
        trips=("ride_duration", "size"),
        avg_duration_min=("ride_duration", lambda s: s.mean() / 60),
        lat=("start_lat", "mean"),
        lng=("start_lng", "mean"),
        members=("user_type", lambda s: (s == "Subscriber").mean()),
    ).reset_index()
    g.columns = ["station", "trips", "avg_duration_min", "lat", "lng", "member_ratio"]
    return g.sort_values("trips", ascending=False).reset_index(drop=True)


def run(df=None):
    """完整统计分析并写入 output/统计结果.txt。"""
    if df is None:
        df = pd.read_csv(config.CLEAN_DATA_FILE, encoding="utf-8-sig",
                         parse_dates=["start_time", "end_time"])

    lines = []
    add = lines.append
    bar = "=" * 50
    add(bar)
    add("纽约Citi Bike 骑行数据分析报告（真实数据）")
    add(bar)
    add("")
    add("【一、描述性统计】")
    dur_min = df["ride_duration"] / 60
    add(f"样本总量：{len(df):,} 条骑行记录")
    add(f"平均骑行时长：{dur_min.mean():.1f} 分钟")
    add(f"中位骑行时长：{dur_min.median():.1f} 分钟")
    add(f"最长骑行时长：{dur_min.max():.1f} 分钟")
    member = (df["user_type"] == "Subscriber").sum()
    add(f"会员(Subscriber)骑行占比：{member / len(df):.1%}（{member:,} 次）")
    add(f"游客/单次(Customer)占比：{(len(df) - member) / len(df):.1%}"
        f"（{len(df) - member:,} 次）")
    add(f"数据日期范围：{df['start_time'].min():%Y-%m-%d} ~ "
        f"{df['start_time'].max():%Y-%m-%d}")
    if "rideable_type" in df.columns and df["rideable_type"].notna().any():
        add(f"车型分布：{df['rideable_type'].value_counts().to_dict()}")

    add("")
    add("【二、热门起点站 TOP10】")
    for name, n in df["start_station"].value_counts().head(10).items():
        add(f"  {name}: {n:,}次")

    add("")
    add("【三、热门终点站 TOP10】")
    for name, n in df["end_station"].value_counts().head(10).items():
        add(f"  {name}: {n:,}次")

    add("")
    add("【四、各时段骑行量(每小时)】")
    hourly = df["hour"].value_counts().sort_index()
    for h, n in hourly.items():
        add(f"  {h}时: {n:,}次")
    peak = hourly.idxmax()
    add(f"  -> 早/晚高峰判断：{peak} 时为峰值小时")

    add("")
    add("【五、工作日 vs 周末】")
    wd = (df["is_weekend"] == 0).sum()
    we = (df["is_weekend"] == 1).sum()
    add(f"  工作日: {wd:,} 次（日均 {wd / 5:,.0f}）")
    add(f"  周末:   {we:,} 次（日均 {we / 2:,.0f}）")

    add("")
    add("【六、各星期骑行量】")
    names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    for d, n in df["weekday"].value_counts().sort_index().items():
        add(f"  {names[d]}: {n:,}次")

    add("")
    add("【七、站点概况】")
    n_station = df["start_station"].nunique()
    add(f"  涉及起点站数量：{n_station}")
    add(f"  单站平均骑行量：{len(df) / n_station:,.0f} 次")

    text = "\n".join(lines)
    with open(os.path.join(config.OUTPUT_DIR, "统计结果.txt"), "w",
              encoding="utf-8") as f:
        f.write(text)
    print(text)

    ss = station_summary(df)
    ss.to_csv(os.path.join(config.OUTPUT_DIR, "station_summary.csv"),
              index=False, encoding="utf-8-sig")
    print(f"\n[analysis] 站点汇总表已保存: output/station_summary.csv"
          f"（{len(ss)} 个站点）")
    return ss


if __name__ == "__main__":
    run()
