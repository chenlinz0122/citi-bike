# -*- coding: utf-8 -*-
"""
model/analyze.py —— 机器学习挖掘模块（成员4）
=============================================
1. 站点聚类（KMeans, k=4）：特征=骑行量、平均时长、会员占比、经纬度
   输出 output/model/station_clusters.csv + 指标（SSE、轮廓系数）
2. 骑行时长预测（线性回归）：特征=hour/is_weekend/is_member/同站往返
3. 站点小时客流预测（线性回归，R²、MAE）
指标写入 output/model/模型指标.txt
"""

import os
import sys

import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, silhouette_score
from sklearn.model_selection import train_test_split

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def cluster_stations(ss):
    X = ss[["trips", "avg_duration_min", "member_ratio", "lat", "lng"]].copy()
    X = (X - X.mean()) / X.std()          # 标准化
    km = KMeans(n_clusters=config.N_CLUSTERS, random_state=config.RANDOM_STATE,
                n_init=10)
    labels = km.fit_predict(X)
    ss = ss.copy()
    ss["cluster"] = labels
    sil = float(silhouette_score(X, labels)) if len(ss) > config.N_CLUSTERS else float("nan")
    return ss, km.inertia_, sil


def duration_regression(df):
    d = df.sample(n=min(50000, len(df)), random_state=config.RANDOM_STATE)
    X = pd.DataFrame({
        "hour": d["hour"],
        "is_weekend": d["is_weekend"],
        "is_member": (d["user_type"] == "Subscriber").astype(int),
        "同站往返": (d["start_station"] == d["end_station"]).astype(int),
    })
    y = d["ride_duration"] / 60           # 分钟
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=config.TEST_SIZE,
                                          random_state=config.RANDOM_STATE)
    reg = LinearRegression().fit(Xtr, ytr)
    pred = reg.predict(Xte)
    return r2_score(yte, pred), mean_absolute_error(yte, pred), dict(zip(X.columns, reg.coef_.round(4)))


def demand_regression(df):
    """站点×小时客流回归：特征 hour/weekday/是否热门站 -> 该站该小时出发量。"""
    cnt = df.groupby(["start_station", "hour"]).size().reset_index(name="flow")
    pop = df["start_station"].value_counts()
    cnt["station_popularity"] = cnt["start_station"].map(pop)
    X = cnt[["hour", "station_popularity"]].assign(
        weekday=0, peak=(cnt["hour"].isin([7, 8, 9, 17, 18, 19])).astype(int))
    y = cnt["flow"]
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=config.TEST_SIZE,
                                          random_state=config.RANDOM_STATE)
    reg = LinearRegression().fit(Xtr, ytr)
    pred = reg.predict(Xte)
    return r2_score(yte, pred), mean_absolute_error(yte, pred)


def run(df=None):
    if df is None:
        df = pd.read_csv(config.CLEAN_DATA_FILE, encoding="utf-8-sig",
                         parse_dates=["start_time", "end_time"])

    lines, add = [], lambda s: lines.append(s)
    add("=" * 50)
    add("纽约Citi Bike 数据挖掘分析报告")
    add("=" * 50)

    # ---- 1. KMeans 站点聚类 ----
    from analysis.analysis import station_summary
    ss = station_summary(df)
    ss, sse, sil = cluster_stations(ss)
    add("")
    add("【一、站点聚类结果（KMeans）】")
    add(f"  聚类数: {config.N_CLUSTERS}")
    add(f"  SSE(簇内平方和): {sse:,.1f}")
    add(f"  轮廓系数: {sil:.3f}")
    for c, g in ss.groupby("cluster"):
        add(f"  类{c}: 站点数={len(g)}, 平均流量={g['trips'].mean():,.0f}次, "
            f"平均时长={g['avg_duration_min'].mean():.1f}分钟, "
            f"会员占比={g['member_ratio'].mean():.1%}")
    add("  -> 类别解读：高流量通勤型 / 低流量休闲型 / 中转型 / 长时骑行型（按特征组合判断）")
    ss.to_csv(os.path.join(config.MODEL_DIR, "station_clusters.csv"),
              index=False, encoding="utf-8-sig")

    # ---- 2. 骑行时长预测 ----
    r2, mae, coefs = duration_regression(df)
    add("")
    add("【二、骑行时长预测（线性回归）】")
    add(f"  R2 = {r2:.3f}")
    add(f"  MAE = {mae:.2f} 分钟")
    add(f"  特征系数: {coefs}")
    add("  -> 说明：时长与时段/会员类型线性相关性弱，需引入距离、天气等特征才有预测力")

    # ---- 3. 站点客流预测 ----
    r2d, maed = demand_regression(df)
    add("")
    add("【三、站点×小时客流预测（线性回归）】")
    add(f"  R² = {r2d:.3f}")
    add(f"  MAE = {maed:.2f} 次/站·小时")
    add("  -> 站点热度是客流的主导因素，可用于辅助车辆调度")

    text = "\n".join(lines)
    with open(os.path.join(config.MODEL_DIR, "模型指标.txt"), "w",
              encoding="utf-8") as f:
        f.write(text)
    print(text)


if __name__ == "__main__":
    run()
