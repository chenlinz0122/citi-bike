# -*- coding: utf-8 -*-
"""
visualization/plots.py —— 可视化模块（成员5）
=============================================
所有图保存到 output/figures/，中文使用 config.CHINESE_FONT。
"""

import os
import sys

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

DPI = 150


def _save(fig, name):
    path = os.path.join(config.FIG_DIR, name)
    fig.tight_layout()
    fig.savefig(path, dpi=DPI)
    plt.close(fig)
    print(f"[plot] 已保存: output/figures/{name}")


def hour_distribution(df):
    fig, ax = plt.subplots(figsize=(9, 4.5))
    counts = df["hour"].value_counts().sort_index()
    colors = ["#d62728" if h in (8, 9, 17, 18) else "#4c72b0"
              for h in counts.index]
    ax.bar(counts.index, counts.values, color=colors)
    ax.set_xticks(range(24))
    ax.set_xlabel("小时")
    ax.set_ylabel("骑行次数")
    ax.set_title("各时段骑行量分布（红=通勤高峰）")
    ax.grid(axis="y", alpha=0.3)
    _save(fig, "hour_distribution.png")


def weekday_distribution(df):
    names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    counts = df["weekday"].value_counts().sort_index()
    ax.bar([names[i] for i in counts.index], counts.values,
           color=["#4c72b0"] * 5 + ["#dd8452"] * 2)
    ax.set_ylabel("骑行次数")
    ax.set_title("一周各日骑行量（橙=周末）")
    ax.grid(axis="y", alpha=0.3)
    _save(fig, "weekday_distribution.png")


def weekend_pie(df):
    wd = (df["is_weekend"] == 0).sum()
    we = (df["is_weekend"] == 1).sum()
    fig, ax = plt.subplots(figsize=(5.5, 5.5))
    ax.pie([wd, we], labels=["工作日", "周末"], autopct="%1.1f%%",
           colors=["#4c72b0", "#dd8452"], startangle=90)
    ax.set_title("工作日与周末骑行量占比")
    _save(fig, "weekend_pie.png")


def hot_station_bar(top_start, top_end, topn=10):
    """top_start/top_end: value_counts() 系列，或站点名字符串（自动取 TOP10）。"""
    if isinstance(top_start, str):
        top_start = pd.Series({top_start: 1})
    if isinstance(top_end, str):
        top_end = pd.Series({top_end: 1})
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.5))
    for ax, (ser, title) in zip(
            axes, [(top_start, "热门起点站 TOP10"), (top_end, "热门终点站 TOP10")]):
        ser = ser.sort_values()
        ax.barh(list(ser.index), ser.values, color="#55a868")
        ax.set_xlabel("骑行次数")
        ax.set_title(title)
        ax.tick_params(axis="y", labelsize=8)
        ax.grid(axis="x", alpha=0.3)
    _save(fig, "hot_stations.png")


def station_scatter(ss):
    """站点气泡图：x=经度 y=纬度 大小=骑行量。ss: station_summary DataFrame。"""
    fig, ax = plt.subplots(figsize=(7, 7))
    sc = ax.scatter(ss["lng"], ss["lat"], s=ss["trips"] / ss["trips"].max() * 300,
                    c=ss["avg_duration_min"], cmap="viridis", alpha=0.7)
    fig.colorbar(sc, ax=ax, label="平均骑行时长(分钟)")
    ax.set_xlabel("经度")
    ax.set_ylabel("纬度")
    ax.set_title("站点骑行量空间分布（大小=流量，颜色=平均时长）")
    ax.set_aspect("equal")
    _save(fig, "station_scatter.png")


def station_folium_map(ss):
    """可选：folium 交互式站点地图，未安装则跳过。"""
    try:
        import folium
    except ImportError:
        print("[plot] 未安装 folium，跳过交互地图（pip install folium 可启用）")
        return
    m = folium.Map(location=[ss["lat"].mean(), ss["lng"].mean()], zoom_start=12)
    max_t = ss["trips"].max()
    for _, r in ss.iterrows():
        folium.CircleMarker(
            [r["lat"], r["lng"]], radius=3 + 8 * r["trips"] / max_t,
            popup=f"{r['station']}<br>骑行量: {r['trips']:,}",
            color="#3186cc", fill=True, fill_opacity=0.6).add_to(m)
    path = os.path.join(config.FIG_DIR, "station_map.html")
    m.save(path)
    print(f"[plot] 已保存: output/figures/station_map.html")
