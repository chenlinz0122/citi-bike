# -*- coding: utf-8 -*-
"""
visualization/plots.py —— 可视化模块（成员5）
=============================================
输入：清洗后标准表 df（由 main.py 经 analysis 模块传入）
输出：output/figures/ 下的标准图表
  - hour_distribution.png         各小时骑行量分布（早晚双峰）
  - weekday_distribution.png      星期分布（工作日 vs 周末）
  - weekend_pie.png               工作日/周末占比饼图
  - hot_station_bar.png           热门起讫站点 TOP10
  - station_scatter.png           站点空间散点（点大小=骑行量）
  - nyc_bike_interactive_map.html folium 交互地图

运行：main.py 步骤3 调用本模块
"""

import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config

_WEEKDAY_NAMES = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]


def _savefig(fig, name):
    fig.savefig(os.path.join(config.FIG_DIR, name), dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  [plots] 已保存: {name}")


def hour_distribution(df):
    """各小时骑行量柱状图（早晚双峰）。"""
    counts = df["hour"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.bar(counts.index, counts.values, color="#2e86de")
    ax.set_xticks(range(0, 24))
    ax.set_xticklabels([f"{h}:00" for h in range(24)], rotation=45)
    ax.set_title("各小时骑行量分布（早晚双峰）")
    ax.set_xlabel("小时")
    ax.set_ylabel("骑行次数")
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    _savefig(fig, "hour_distribution.png")


def weekday_distribution(df):
    """星期分布柱状图（工作日 vs 周末）。"""
    counts = df["weekday"].value_counts().sort_index()
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(range(7), counts.values, color="#16a085")
    ax.set_xticks(range(7))
    ax.set_xticklabels(_WEEKDAY_NAMES)
    ax.set_title("星期骑行量分布（工作日 vs 周末）")
    ax.set_ylabel("骑行次数")
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    _savefig(fig, "weekday_distribution.png")


def weekend_pie(df):
    """工作日 vs 周末骑行占比饼图。"""
    cnt = df["is_weekend"].value_counts()
    values = [cnt.get(0, 0), cnt.get(1, 0)]
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.pie(values, labels=["工作日", "周末"], autopct="%.1f%%", startangle=90,
           colors=["#3498db", "#e67e22"], explode=(0.03, 0.03), shadow=True)
    ax.set_title("工作日 vs 周末骑行占比")
    fig.tight_layout()
    _savefig(fig, "weekend_pie.png")


def hot_station_bar(start, end, top_n=10):
    """热门借/还车站点 TOP10 水平柱状图。"""
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    for ax, series, title in [
        (axes[0], start, "热门借车站点 TOP10"),
        (axes[1], end, "热门还车站点 TOP10"),
    ]:
        s = series.sort_values(ascending=False).head(top_n)
        ax.barh(s.index, s.values, color="#2e86de")
        ax.set_title(title)
        ax.set_xlabel("骑行次数")
        ax.grid(True, alpha=0.3, axis="x")
        ax.invert_yaxis()
    fig.tight_layout()
    _savefig(fig, "hot_station_bar.png")


def station_scatter(ss):
    """站点空间散点图（点大小=骑行量）。"""
    fig, ax = plt.subplots(figsize=(10, 8))
    sizes = (ss["total_trips"] / ss["total_trips"].max() * 80 + 8)
    ax.scatter(ss["start_lng"], ss["start_lat"], s=sizes, alpha=0.5, c="#e74c3c")
    ax.set_title("站点空间分布（点大小=骑行量）")
    ax.set_xlabel("经度")
    ax.set_ylabel("纬度")
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    _savefig(fig, "station_scatter.png")


def station_folium_map(ss):
    """folium 站点交互地图（前50热门站点，可选依赖）。"""
    try:
        import folium
    except ImportError:
        print("  [plots] 未安装 folium，跳过交互地图")
        return
    m = folium.Map(location=[40.73, -73.98], zoom_start=12)
    top = ss.sort_values("total_trips", ascending=False).head(50)
    for _, row in top.iterrows():
        folium.CircleMarker(
            location=[row["start_lat"], row["start_lng"]],
            radius=3 + 6 * row["total_trips"] / top["total_trips"].max(),
            popup=f"{row['station_name']}：{int(row['total_trips'])} 次",
            color="#e74c3c", fill=True, fill_opacity=0.6,
        ).add_to(m)
    out = os.path.join(config.FIG_DIR, "nyc_bike_interactive_map.html")
    m.save(out)
    print(f"  [plots] 已保存: nyc_bike_interactive_map.html")
