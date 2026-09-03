# -*- coding: utf-8 -*-
"""
sample_data.py —— 示例数据生成器（兜底用）
============================================
用途：在尚未下载 Citi Bike 真实数据，或数据规模过大时，生成一份
字段结构合理的示例骑行数据，用于跑通"预处理→统计→可视化→建模"全流程。

参数通过 config 控制。真实数据放好后，系统会优先使用真实数据。
本模块也负责：读取原始CSV（含字段别名兼容）、过滤异常、抽样。
"""

import os
import random
import sys
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


# 用若干个明星站名模拟 Citi Bike 站点（含真实经纬度示意）
STATIONS = [
    {"name": "W 34 St & 8 Ave", "lat": 40.7532, "lng": -73.9952},
    {"name": "E 20 St & Park Ave S", "lat": 40.7381, "lng": -73.9894},
    {"name": "Central Park S & 6 Ave", "lat": 40.7671, "lng": -73.9768},
    {"name": "Broadway & W 58 St", "lat": 40.7670, "lng": -73.9815},
    {"name": "Mercer St & Spring St", "lat": 40.7245, "lng": -73.9998},
    {"name": "E 47 St & 2 Ave", "lat": 40.7530, "lng": -73.9699},
    {"name": "W 21 St & 8 Ave", "lat": 40.7437, "lng": -74.0032},
    {"name": "Duffield & Fulton", "lat": 40.6910, "lng": -73.9840},
]


def gen_sample_data(n=200000, seed=42):
    """
    生成 n 条示例骑行记录（DataFrame），字段与 Citi Bike 一致。
    """
    random.seed(seed)
    rows = []
    for _ in range(n):
        s = random.choice(STATIONS)
        e = random.choice(STATIONS)
        # 骑行时长 1分钟~2小时
        dur = random.randint(60, 7200)
        # 时间：某一天内的随机时刻，靠近高峰
        hour = int(random.gauss(13, 5)) % 24
        minutes = random.randint(0, 59)
        day = random.randint(1, 28)
        start_dt = f"2025-08-{day:02d} {hour:02d}:{minutes:02d}:00"
        rows.append({
            "start_time": start_dt,
            "end_time": start_dt,
            "start_station": s["name"], "end_station": e["name"],
            "start_lat": s["lat"], "start_lng": s["lng"],
            "end_lat": e["lat"], "end_lng": e["lng"],
            "user_type": random.choice(["Subscriber", "Customer"]),
            "ride_duration": dur,
        })
    return pd.DataFrame(rows)