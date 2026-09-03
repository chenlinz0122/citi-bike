# -*- coding: utf-8 -*-
"""
plots.py —— 可视化模块（成员5负责）
====================================
职责：把分析结果画成图表并保存到 output/figures/
  1. hour_bar.png        各小时骑行量条形图
  2. weekday_bar.png     各星期骑行量条形图
  3. weekend_pie.png     工作日/周末占比饼图
  4. hot_start_bar.png   热门起点站条形图
  5. station_scatter.png 站点流量散点图(按经纬度,大小=流量)
  6. station_map.html    站点地图(热力图, folium, 可选)

依赖：matplotlib（已装）、folium（地图，需安装）
"""

import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

WEEKDAY_NAMES = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def _style():
    """统一图表样式"""
    plt.rcParams["font.sans-serif"] = [config.CHINESE_FONT] if config.CHINESE_FONT else []
    plt.rcParams["axes.unicode_minus"] = False
    plt.rcParams["figure.dpi"] = 100


def savefig(fig, name):
    """保存图片到 output/figures/"""
    path = os.path.join(config.FIG_DIR, name)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"[可视化] 已保存 -> {path}")
    return path


def hour_distribution(df):
    """图1：各小时骑行量折线/条形图"""
    _style()
    cnt = df.groupby("hour").size()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(cnt.index, cnt.values, color="#4C9BD9")
    ax.set_title("各时段骑行量分布（早晚高峰特征）", fontsize=14)
    ax.set_xlabel("小时（0-23）")
    ax.set_ylabel("骑行次数 (条)")
    ax.set_xticks(range(0, 24))
    ax.grid(axis="y", alpha=0.3)
    return savefig(fig, "hour_distribution.png")


def weekday_distribution(df):
    """图2各星期骑行量"""
    _style()
    cnt = df.groupby("weekday").size()
    fig, ax = plt.subplots(figsize=(9, 5))
    colors = ["#7CCCA0"] * 5 + ["#F5B041"] * 2
    ax.bar(WEEKDAY_NAMES, cnt.values, color=colors)
    ax.set_title("各星期骑行量分布（工作日 vs 周末）", fontsize=14)
    ax.set_ylabel("骑行次数 (次)")
    for i, v in enumerate(cnt.values):
        ax.text(i, v, f"{int(v):,}", ha="center", va="bottom", fontsize=10)
    return savefig(fig, "weekday_distribution.png")


def weekend_pie(df):
    """图3：工作日/周末占比饼图"""
    _style()
    cnt = df.groupby("is_weekend").size()
    labels = ["工作日", "周末"]
    sizes = [cnt.get(0, 0), cnt.get(1, 0)]
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(sizes, labels=labels, autopct="%.1f%%", startangle=90,
           colors=["#4C9BD9", "#F5B041"], wedgeprops=dict(edgecolor="w"))
    ax.set_title("工作日与周末骑行占比", fontsize=14)
    return savefig(fig, "weekend_pie.png")


def hot_station_bar(start_df, end_df, top=10):
    """图4：热门起点站/终点站条形图"""
    _style()
    s = start_df.head(top).iloc[::-1]
    e = end_df.head(top).iloc[::-1]
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    axes[0].barh(s["start_station"], s["出发次数"], color="#4C9BD9")
    axes[0].set_title("热门出发站 TOP%d" % top)
    axes[0].set_xlabel("出发次数")
    axes[1].barh(e["end_station"], e["到达次数"], color="#7C38A8")
    axes[1].set_title("热门到达站 TOP%d" % top)
    axes[1].set_xlabel("到达次数")
    fig.suptitle("纽约Citi Bike 热门站点", fontsize=15)
    return savefig(fig, "hot_stations.png")


def station_scatter(ss_df):
    """站点地图：按经纬度画散点，点越大流量越大"""
    _style()
    fig, ax = plt.subplots(figsize=(10, 8))
    x = ss_df["start_lng"]
    y = ss_df["start_lat"]
    sizes = (ss_df["total"] - ss_df["total"].min()) / \
            (ss_df["total"].max() - ss_df["total"].min() + 1) * 800 + 30
    sc = ax.scatter(x, y, s=sizes, c=ss_df["total"], cmap="YlOrRd", alpha=0.7)
    fig.colorbar(sc, ax=ax, label="站点流量")
    ax.set_xlabel("经度")  # 英文：Longitude
    ax.set_ylabel("纬度")  # 英文：Latitude
    ax.set_title("站点空间分布(散点大小代表使用量)")
    ax.grid(alpha=0.3)
    return savefig(fig, "station_scatter.png")


def station_folium_map(ss_df, out_html=None):
    """
    站点热力地图（folium，可选）。若未安装 folium 则提示。
    返回: html 路径 或 None
    """
    try:
        import folium
    except ImportError:
        print("[可视化] 未安装 folium，跳过地图。执行 pip install folium")
        return None
    _style()
    center = [ss_df["start_lat"].mean(), ss_df["start_lng"].mean()]
    m = folium.Map(location=center, zoom_start=13, tiles="OpenStreetMap")

    # 添加城市热力图或站点圆圈
    for _, r in ss_df.iterrows():
        folium.CircleMarker(
            location=[r["start_lat"], r["start_lng"]],
            radius=5,
            popup=f"{r['station']}: {int(r['total'])}次",
            color="crimson", fill=True, fillOpacity=0.6,
        ).add_to(m)
    path = out_html or out_txt or os.path.join(config.OUTPUT_DIR, "station_map.html")
    m.save(path)
    print(f"[可视化] 站点地图已保存 -> {path}")
    return path


if __name__ == "__main__":
    # 加载清洗数据 + 分析模块结果
    from storage.preprocess import run as preprocess
    from analysis.analysis import load_clean, hot_stations, station_summary, time_pattern
    df = load_clean()
    start, end = hot_stations(df)
    ss = station_summary(df)
    hour_distribution(df)
    weekday_distribution(df)
    weekend_pie(df)
    hot_station_bar(start, end)
    station_scatter(ss)
    station_folium_map(ss)