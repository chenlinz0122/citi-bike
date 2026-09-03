# -*- coding: utf-8 -*-
"""
analysis.py —— 统计与分析模块（成员3负责）
============================================
职责：对清洗后的 Citi Bike 数据做
  1. 描述性统计（总骑行量、平均时长、会员占比等）
  2. 热门站点排名（起点站、终点站）
  3. 时间段分析（早晚高峰、工作日vs周末、各小时分布）
  4. 站点维度汇总（供聚类/地图使用）

输出：统计结果文本 output/统计结果.txt
     站点汇总表  output/station_summary.csv
"""

import os
import sys
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

# 星期名映射
WEEKDAY_NAMES = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def load_clean():
    """读取清洗后的数据；不存在则运行预处理"""
    if not os.path.exists(config.CLEAN_DATA_FILE):
        from storage.preprocess import run
        run()
    return pd.read_csv(config.CLEAN_DATA_FILE)


def descriptive_stats(df):
    """
    计算描述性统计特征，返回 (统计条目列表, 关键词频字典)
    """
    stats = []
    total = len(df)
    stats.append(f"样本总量：{total:,} 条骑行记录")

    # 平均/中位骑行时长（秒->分钟）
    dur = df["ride_duration"]
    stats.append(f"平均骑行时长：{dur.mean()/60:.1f} 分钟")
    stats.append(f"中位骑行时长：{dur.median()/60:.1f} 分钟")
    stats.append(f"最长骑行时长：{dur.max()/60:.1f} 分钟")

    # 会员类型占比
    if "user_type" in df.columns:
        vc = df["user_type"].value_counts()
        member = vc.get("Subscriber", vc.get("subscriber", 0))
        casual = vc.get("Customer", vc.get("customer", 0))
        stats.append(f"会员骑行占比：{member/total*100:.1f}%（{member}次）")
        stats.append(f"游客/单次骑行占比：{casual/total*100:.1f}%（{casual}次）")

    # 日期范围
    if "start_date" in df.columns:
        sd = pd.to_datetime(df["start_date"])
        stats.append(f"数据日期范围：{sd.min().date()} ~ {sd.max().date()}")

    return stats


def hot_stations(df, top_n=15):
    """
    热门站点：分别统计起点和终点的频次，返回排名。
    返回: start_df, end_df (DataFrame: 站名, 次数)
    """
    start = df.groupby("start_station").size().reset_index(name="出发次数") \
              .sort_values("出发次数", ascending=False).head(top_n)
    end = df.groupby("end_station").size().reset_index(name="到达次数") \
            .sort_values("到达次数", ascending=False).head(top_n)
    return start, end


def time_pattern(df):
    """
    时间规律分析：
      - 各小时骑行量
      - 工作日 vs 周末
      - 各星期骑行量
    """
    hour_cnt = df.groupby("hour").size()
    weekday_cnt = df.groupby("weekday").size()
    weekend_cnt = df.groupby("is_weekend").size()
    return hour_cnt, weekday_cnt, weekend_cnt


def station_summary(df):
    """
    按站点聚合，生成站点汇总表（供聚类和地图用）：
      站点名 | 经纬度(取均值) | 出发量 | 到达量 | 总流量
    """
    # 起点聚合
    s = df.groupby("start_station").agg(
        start_cnt=("start_station", "size"),
        start_lat=("start_lat", "mean"),
        start_lng=("start_lng", "mean"),
    ).reset_index()
    s = s.rename(columns={"start_station": "station"})

    # 终点聚合
    e = df.groupby("end_station").agg(end_cnt=("end_station", "size")).reset_index()
    e = e.rename(columns={"end_station": "station"})

    out = s.merge(e, on="station", how="outer").fillna(0)
    out["total"] = out["start_cnt"] + out["end_cnt"]
    out = out.sort_values("total", ascending=False).reset_index(drop=True)
    return out


def save_report(stats, start, end, hour_cnt, weekday_cnt, weekend_cnt, out_txt=None):
    """把统计结果写入文本文件"""
    lines = ["=" * 50, "纽约Citi Bike 骑行数据分析报告", "=" * 50]
    lines.append("\n【一、描述性统计】")
    lines.extend(stats)
    lines.append("\n【二、热门起点站 TOP10】")
    for _, r in start.head(10).iterrows():
        lines.append(f"  {r['start_station']}: {r['出发次数']}次")
    lines.append("\n【三、热门终点站 TOP10】")
    for _, r in end.head(10).iterrows():
        lines.append(f"  {r['end_station']}: {r['到达次数']}次")
    lines.append("\n【四、各时段骑行量(每小时)】")
    for h, c in hour_cnt.items():
        lines.append(f"  {h}时: {int(c)}次")
    lines.append("\n【五、工作日vs周末】")
    for k, c in weekend_cnt.items():
        name = "工作日" if k == 0 else "周末"
        lines.append(f"  {name}: {int(c)}次")
    lines.append("\n【六、各星期骑行量】")
    for w, c in weekday_cnt.items():
        lines.append(f"  {WEEKDAY_NAMES[w]}: {int(c)}次")

    path = out_txt or os.path.join(config.OUTPUT_DIR, "统计结果.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[分析] 统计报告已保存 -> {path}")
    return path


def run():
    """分析主流程：加载->统计->保存站点表"""
    df = load_clean()
    stats = descriptive_stats(df)
    start, end = hot_stations(df)
    hour_cnt, weekday_cnt, weekend_cnt = time_pattern(df)
    save_report(stats, start, end, hour_cnt, weekday_cnt, weekend_cnt)

    ss = station_summary(df)
    ss_path = os.path.join(config.OUTPUT_DIR, "station_summary.csv")
    ss.to_csv(ss_path, index=False, encoding="utf-8-sig")
    print(f"[分析] 站点汇总表({len(ss)}站)已保存 -> {ss_path}")
    print("\n--- 描述性统计预览 ---")
    for line in stats:
        print(" ", line)
    return df, ss


if __name__ == "__main__":
    run()