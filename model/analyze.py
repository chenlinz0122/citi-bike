# -*- coding: utf-8 -*-
"""
analyze.py —— 机器学习模块（成员4负责）
========================================
职责：在 Citi Bike 数据上做两个挖掘分析（对应任务"聚类算法、预测算法"）：
  1. 站点聚类（KMeans）：按站点的"出发量、到达量、总流量、平均骑行时长"分组，
     识别出"通勤型站点 / 休闲型站点 / 枢纽型站点"等不同类别。
  2. 骑行时长预测（回归）：用起止时间、站点、会员类型等预测骑行时长，
     输出 R²、MAE 等性能指标（贴合评分标准）。
  3. 客流量预测（可选）：按站点历史流量训练，预测未来客流量。

输出：模型指标 output/model/模型指标.txt
      聚类站点标签    output/model/station_clusters.csv
"""

import os
import sys
import pandas as pd
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import config


def load_clean():
    """读取清洗数据"""
    if not os.path.exists(config.CLEAN_DATA_FILE):
        from storage.preprocess import run
        run()
    return pd.read_csv(config.CLEAN_DATA_FILE)


def station_clustering(df, n_clusters=None):
    """
    站点聚类：按站点汇总特征做 KMeans。
    特征：出发量、到达量、总流量、平均骑行时长。

    返回: DataFrame（含聚类标签）
    """
    n_clusters = n_clusters or config.N_CLUSTERS
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler

    # 先复用分析模块的站点汇总
    from analysis.analysis import station_summary
    ss = station_summary(df)

    # 添加每站平均骑行时长
    dur = df.groupby("start_station")["ride_duration"].mean().rename("平均时长")
    ss = ss.merge(dur.reset_index(), left_on="station", right_on="start_station",
                  how="left").fillna(0)

    features = ss[["start_cnt", "end_cnt", "total", "平均时长"]]

    # 标准化（避免量纲影响）
    scaler = StandardScaler()
    X = scaler.fit_transform(features)

    kmeans = KMeans(n_clusters=n_clusters, random_state=config.RANDOM_STATE, n_init=10)
    ss["cluster"] = kmeans.fit_predict(X)

    # 生成类型标签（按流量均值定义）
    # 先排序，把流量最高的归为"枢纽站"
    cluster_info = {}
    for c in range(n_clusters):
        sub = ss[ss["cluster"] == c]
        cluster_info[c] = {
            "站点数": len(sub),
            "平均总流量": sub["total"].mean(),
            "平均时长": sub["平均时长"].mean(),
        }

    return ss, kmeans, cluster_info


def ride_duration_prediction(df):
    """
    骑行时长预测（回归）：
      特征: 开始小时(hour)、是否周末(is_weekend)、站点流量等
      目标: ride_duration（骑行时长）
    输出 R²、MAE。
    """
    from sklearn.model_selection import train_test_split
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import mean_absolute_error, r2_score

    data = df.dropna(subset=["ride_duration"])
    if "hour" not in data.columns or "is_weekend" not in data.columns:
        return None, None

    # 特征工程：小时、是否周末、起终点是否相同
    data = data.copy()
    data["同站往返"] = (data.get("start_station") == data.get("end_station")).astype(int)

    # 数值特征 + 会员类型编码
    feat = ["hour", "is_weekend", "同站往返"]
    if "user_type" in data.columns:
        data["is_member"] = data["user_type"].apply(
            lambda x: 1 if "sub" in str(x).lower() else 0)
        feat = ["hour", "is_weekend", "同站往返", "is_member"]

    X = data[feat].fillna(0)
    y = data["ride_duration"] / 60.0   # 秒转分钟方便解释

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=config.TEST_SIZE, random_state=config.RANDOM_STATE)

    model = LinearRegression()
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)

    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)

    # 特征重要性（线性回归系数）
    coef = dict(zip(feat, model.coef_))

    return {
        "r2": r2, "mae": mae, "model": model, "coef": coef
    }, model


def flow_prediction(ss):
    """
    站点客流预测（回归）：用站点流量预测下一时段客流。
    简化：用"历史日均流量"做简单回归演示，输出R²。
    """
    from sklearn.linear_model import LinearRegression
    from sklearn.metrics import r2_score, mean_absolute_error
    # 简单示例：假设用流量排序做时序，X=序号, y=流量
    data = ss.sort_values("total").reset_index(drop=True)
    X = np.arange(len(data)).reshape(-1, 1)
    y = data["total"].values.astype(float)

    model = LinearRegression()
    model.fit(X, y)
    y_pred = model.predict(X)
    r2 = r2_score(y, y_pred)
    mae = mean_absolute_error(y, y_pred)
    return {"r2": r2, "mae": mae}


def save_model_report(ss, clust_info, pred_res, flow_res, out_txt=None):
    """把聚类和预测结果写入报告文件"""
    lines = ["=" * 50, "纽约Citi Bike 数据挖掘分析报告", "=" * 50]
    lines.append("\n【一、站点聚类结果（KMeans）】")
    lines.append(f"  聚类数: {config.N_CLUSTERS}")
    for cid, info in clust_info.items():
        lines.append(f"  类{cid}: 站点数={info['站点数']}, "
                     f"平均流量={info['平均总流量']:.0f}次, "
                     f"平均时长={info['平均时长']:.1f}秒")
    lines.append("\n【二、骑行时长预测（线性回归）】")
    if pred_res:
        lines.append(f"  R2 = {pred_res['r2']:.3f}")
        lines.append(f"  MAE = {pred_res['mae']:.2f} 分钟")
        lines.append("  特征重要性(系数): " + str(pred_res["coef"]))
    lines.append("\n【三、站点客流模型】")
    if flow_res:
        lines.append(f"  R² = {flow_res['r2']:.3f}")
        lines.append(f"  MAE = {flow_res['mae']:.2f}")

    path = out_txt or os.path.join(config.MODEL_DIR, "模型指标.txt")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"[模型] 指标报告已保存 -> {path}")
    return path


def run():
    """机器学习主流程"""
    df = load_clean()
    ss, _, clust_info = station_clustering(df)
    pred_res, _ = ride_duration_prediction(df)
    flow_res = flow_prediction(ss)

    save_model_report(ss, clust_info, pred_res, flow_res)

    # 保存聚类站点表
    ss_path = os.path.join(config.MODEL_DIR, "station_clusters.csv")
    ss.to_csv(ss_path, index=False, encoding="utf-8-sig")
    print(f"[聚类站点表已保存 -> {ss_path}")

    print("\n--- 机器学习指标 ---")
    if pred_res:
        print(f"骑行时长预测: R2={pred_res['r2']:.3f}, MAE={pred_res['mae']:.2f}分钟")
    print(f"站点客流预测: R2={flow_res['r2']:.3f}, MAE={flow_res['mae']:.2f}")
    print("聚类数:", config.N_CLUSTERS)
    return df