# -*- coding: utf-8 -*-
"""
纽约公共自行车数据分析与可视化 - 机器学习模块
成员4：KMeans 站点聚类 + 骑行时长预测 + 客流预测

输入：data/clean/clean_citibike.csv（成员2预处理输出）
输出：
  - output/model/kmeans_clustering_results.csv  站点聚类结果
  - output/model/kmeans_cluster_summary.csv      各簇特征汇总
  - output/model/duration_prediction_report.csv  骑行时长预测模型评估
  - output/model/demand_prediction_report.csv    客流预测模型评估
  - output/model/feature_importance.csv          特征重要性
  - output/fig/  各类可视化图表

依赖：pandas, numpy, scikit-learn, matplotlib, seaborn
"""

import os
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # 非交互式后端，避免GUI问题
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    silhouette_score, calinski_harabasz_score, davies_bouldin_score,
    mean_absolute_error, mean_squared_error, r2_score
)
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor

warnings.filterwarnings('ignore')

# ============================================================
# 全局配置
# ============================================================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, 'data', 'clean', 'clean_citibike.csv')
OUTPUT_MODEL = os.path.join(BASE_DIR, 'output', 'model')
OUTPUT_FIG = os.path.join(BASE_DIR, 'output', 'fig')

os.makedirs(OUTPUT_MODEL, exist_ok=True)
os.makedirs(OUTPUT_FIG, exist_ok=True)

# 中文字体设置 - 直接加载字体文件确保可靠
_FONT_PATHS = [
    r'C:\Windows\Fonts\msyh.ttc',       # Microsoft YaHei
    r'C:\Windows\Fonts\msyhbd.ttc',     # Microsoft YaHei Bold
    r'C:\Windows\Fonts\simhei.ttf',      # SimHei
    r'C:\Windows\Fonts\simsun.ttc',      # SimSun
]
for _fp in _FONT_PATHS:
    if os.path.exists(_fp):
        try:
            fm.fontManager.addfont(_fp)
        except Exception:
            pass

# 清除字体缓存并重建
_cache_dir = matplotlib.get_cachedir()
_cache_file = os.path.join(_cache_dir, 'fontlist-v330.json')
if os.path.exists(_cache_file):
    try:
        os.remove(_cache_file)
    except Exception:
        pass

# 注意：必须先设seaborn样式，再设字体，否则seaborn会覆盖字体配置
sns.set_style("whitegrid")
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei', 'SimHei', 'SimSun', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False
plt.rcParams['font.family'] = 'sans-serif'

# ============================================================
# 超参数统一配置区（如需调整模型行为，只改这里）
# ============================================================
RANDOM_STATE = 42                 # 全局随机种子，保证结果可复现
TEST_RATIO = 0.2                  # 训练/测试集比例（时长预测为随机划分，客流预测为时序划分）
MAX_DISTANCE_KM = 50              # 骑行距离异常值过滤阈值（km）
MIN_STATION_TRIPS = 20            # 站点聚类过滤阈值：总流量低于该值的站点剔除

# ---- KMeans 聚类超参数 ----
K_RANGE = range(2, 11)            # 候选聚类数 K 的扫描范围
KMEANS_N_INIT = 10                # KMeans 多次初始化次数（避免局部最优）

# ---- 骑行时长预测模型超参数（回归） ----
DURATION_MODEL_PARAMS = {
    '决策树 (Decision Tree)': {'max_depth': 15, 'min_samples_leaf': 20},
    '随机森林 (Random Forest)': {'n_estimators': 100, 'max_depth': 20, 'min_samples_leaf': 10, 'n_jobs': -1},
    '梯度提升 (Gradient Boosting)': {'n_estimators': 100, 'max_depth': 6, 'learning_rate': 0.1},
}

# ---- 站点客流预测模型超参数（回归） ----
DEMAND_MODEL_PARAMS = {
    '决策树 (Decision Tree)': {'max_depth': 12, 'min_samples_leaf': 5},
    '随机森林 (Random Forest)': {'n_estimators': 200, 'max_depth': 15, 'min_samples_leaf': 3, 'n_jobs': -1},
    '梯度提升 (Gradient Boosting)': {'n_estimators': 200, 'max_depth': 5, 'learning_rate': 0.05},
}

# ---- 数据字段校验：清洗后标准表必须包含的列 ----
REQUIRED_COLUMNS = [
    'start_time', 'end_time', 'start_date', 'ride_duration',
    'start_lat', 'start_lng', 'end_lat', 'end_lng',
    'start_station', 'end_station', 'hour', 'weekday',
    'is_weekend', 'user_type', 'rideable_type',
]


def haversine_km(lat1, lon1, lat2, lon2):
    """
    Haversine公式计算两点间球面距离（单位：公里）
    用于估算起终点直线距离，是骑行时长预测的核心特征
    """
    R = 6371.0  # 地球半径（公里）
    lat1_rad = np.radians(lat1)
    lat2_rad = np.radians(lat2)
    dlat = np.radians(lat2 - lat1)
    dlon = np.radians(lon2 - lon1)
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1_rad) * np.cos(lat2_rad) * np.sin(dlon / 2) ** 2
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return R * c


def load_data():
    """加载清洗后的骑行数据，并计算Haversine骑行距离"""
    print("[1/6] 加载数据...")
    df = pd.read_csv(DATA_PATH)

    # 字段校验：与成员2约定的标准表列名契约核对，缺失即报错并列出缺列
    missing_cols = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing_cols:
        raise ValueError(
            f"数据表缺少必需字段: {missing_cols}\n"
            f"请确认 data/clean/clean_citibike.csv 遵循标准表列名契约"
        )
    print(f"  字段校验通过: {len(REQUIRED_COLUMNS)} 个必需字段全部存在")

    # 时间解析
    df['start_time'] = pd.to_datetime(df['start_time'])
    df['end_time'] = pd.to_datetime(df['end_time'])
    df['start_date'] = pd.to_datetime(df['start_date'])
    # 骑行时长转分钟（更直观）
    df['duration_min'] = df['ride_duration'] / 60.0
    # Haversine起终点直线距离（公里）——时长预测最关键特征
    df['distance_km'] = haversine_km(
        df['start_lat'].values, df['start_lng'].values,
        df['end_lat'].values, df['end_lng'].values
    )
    # 过滤距离异常值（>50km视为数据错误）
    df = df[df['distance_km'] <= MAX_DISTANCE_KM].reset_index(drop=True)
    print(f"  数据形状: {df.shape}")
    print(f"  时间范围: {df['start_time'].min()} ~ {df['start_time'].max()}")
    print(f"  站点数: {df['start_station'].nunique()}")
    print(f"  平均骑行距离: {df['distance_km'].mean():.2f} km")
    print(f"  距离中位数: {df['distance_km'].median():.2f} km")
    return df


# ============================================================
# 模块一：KMeans 站点聚类
# ============================================================
def build_station_features(df):
    """
    构建站点级特征矩阵，用于 KMeans 聚类
    特征维度：
      - total_trips: 总骑行量（流出+流入）
      - avg_duration: 平均骑行时长（分钟）
      - peak_hour: 最活跃小时
      - morning_peak_ratio: 早高峰(7-9)占比
      - evening_peak_ratio: 晚高峰(17-19)占比
      - weekend_ratio: 周末骑行占比
      - subscriber_ratio: 会员占比
      - lat, lng: 站点经纬度
      - flow_balance: 流入流出平衡度
    """
    print("\n[2/6] 构建站点特征矩阵...")

    # 借出特征
    start_feats = df.groupby('start_station').agg(
        start_trips=('ride_duration', 'count'),
        avg_duration_start=('duration_min', 'mean'),
        start_lat=('start_lat', 'first'),
        start_lng=('start_lng', 'first'),
    ).reset_index().rename(columns={'start_station': 'station_name'})

    # 借入特征
    end_feats = df.groupby('end_station').agg(
        end_trips=('ride_duration', 'count'),
        avg_duration_end=('duration_min', 'mean'),
    ).reset_index().rename(columns={'end_station': 'station_name'})

    # 合并
    station_feats = pd.merge(start_feats, end_feats, on='station_name', how='outer')
    station_feats = station_feats.fillna(0)

    # 总流量 = 借出 + 借入
    station_feats['total_trips'] = station_feats['start_trips'] + station_feats['end_trips']
    # 平均时长
    station_feats['avg_duration'] = (
        station_feats['avg_duration_start'] * station_feats['start_trips'] +
        station_feats['avg_duration_end'] * station_feats['end_trips']
    ) / station_feats['total_trips'].replace(0, 1)

    # 经纬度（优先用start的，没有用end的）
    station_feats['lat'] = station_feats['start_lat'].replace(0, np.nan)
    station_feats['lng'] = station_feats['start_lng'].replace(0, np.nan)
    # 从end补充经纬度
    end_lat = df.groupby('end_station')['end_lat'].first().reset_index()
    end_lat.columns = ['station_name', 'end_lat_val']
    end_lng = df.groupby('end_station')['end_lng'].first().reset_index()
    end_lng.columns = ['station_name', 'end_lng_val']
    station_feats = station_feats.merge(end_lat, on='station_name', how='left')
    station_feats = station_feats.merge(end_lng, on='station_name', how='left')
    station_feats['lat'] = station_feats['lat'].fillna(station_feats['end_lat_val'])
    station_feats['lng'] = station_feats['lng'].fillna(station_feats['end_lng_val'])

    # 时间模式特征：按站点计算各时段占比
    def calc_time_pattern(group):
        total = len(group)
        if total == 0:
            return pd.Series({
                'peak_hour': 12,
                'morning_peak_ratio': 0,
                'evening_peak_ratio': 0,
                'weekend_ratio': 0,
                'subscriber_ratio': 0,
            })
        hour_counts = group['hour'].value_counts()
        peak_hour = hour_counts.idxmax()
        morning = group[(group['hour'] >= 7) & (group['hour'] <= 9)].shape[0]
        evening = group[(group['hour'] >= 17) & (group['hour'] <= 19)].shape[0]
        weekend = group[group['is_weekend'] == 1].shape[0]
        subscriber = group[group['user_type'] == 'Subscriber'].shape[0]
        return pd.Series({
            'peak_hour': peak_hour,
            'morning_peak_ratio': morning / total,
            'evening_peak_ratio': evening / total,
            'weekend_ratio': weekend / total,
            'subscriber_ratio': subscriber / total,
        })

    time_pattern = df.groupby('start_station').apply(calc_time_pattern).reset_index()
    time_pattern.columns = ['station_name'] + list(time_pattern.columns[1:])
    station_feats = station_feats.merge(time_pattern, on='station_name', how='left')

    # 流入流出平衡度：|借出-借入| / 总流量，越接近0越平衡
    station_feats['flow_balance'] = (
        np.abs(station_feats['start_trips'] - station_feats['end_trips'])
        / station_feats['total_trips'].replace(0, 1)
    )

    # 过滤掉流量过少的站点（总流量 < MIN_STATION_TRIPS 的站点视为异常/边缘站点，提升聚类质量）
    station_feats = station_feats[station_feats['total_trips'] >= MIN_STATION_TRIPS].reset_index(drop=True)

    # 最终用于聚类的特征列
    cluster_cols = [
        'total_trips', 'avg_duration', 'peak_hour',
        'morning_peak_ratio', 'evening_peak_ratio',
        'weekend_ratio', 'subscriber_ratio', 'flow_balance',
        'lat', 'lng'
    ]
    station_feats = station_feats.dropna(subset=cluster_cols)

    print(f"  有效站点数: {len(station_feats)}")
    print(f"  聚类特征维度: {len(cluster_cols)}")
    return station_feats, cluster_cols


def kmeans_clustering(station_feats, cluster_cols):
    """
    KMeans 站点聚类
    1. 肘部法则 + 轮廓系数选择最佳 K
    2. 训练最终模型
    3. 聚类结果分析与可视化
    """
    print("\n[3/6] KMeans 站点聚类...")

    X = station_feats[cluster_cols].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # --- 肘部法则：计算 K=2~10 的 SSE ---
    k_range = K_RANGE
    sse_list = []
    silhouette_list = []
    ch_list = []
    db_list = []

    for k in k_range:
        km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=KMEANS_N_INIT)
        labels = km.fit_predict(X_scaled)
        sse_list.append(km.inertia_)
        silhouette_list.append(silhouette_score(X_scaled, labels))
        ch_list.append(calinski_harabasz_score(X_scaled, labels))
        db_list.append(davies_bouldin_score(X_scaled, labels))

    # 绘制肘部法则图
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes[0, 0].plot(k_range, sse_list, 'bo-', linewidth=2, markersize=8)
    axes[0, 0].set_xlabel('聚类数 K', fontsize=12)
    axes[0, 0].set_ylabel('SSE (簇内平方和)', fontsize=12)
    axes[0, 0].set_title('肘部法则 (Elbow Method)', fontsize=14, fontweight='bold')
    axes[0, 0].set_xticks(list(k_range))

    axes[0, 1].plot(k_range, silhouette_list, 'rs-', linewidth=2, markersize=8)
    axes[0, 1].set_xlabel('聚类数 K', fontsize=12)
    axes[0, 1].set_ylabel('轮廓系数 (Silhouette)', fontsize=12)
    axes[0, 1].set_title('轮廓系数 (越高越好)', fontsize=14, fontweight='bold')
    axes[0, 1].set_xticks(list(k_range))

    axes[1, 0].plot(k_range, ch_list, 'g^-', linewidth=2, markersize=8)
    axes[1, 0].set_xlabel('聚类数 K', fontsize=12)
    axes[1, 0].set_ylabel('CH 指数', fontsize=12)
    axes[1, 0].set_title('Calinski-Harabasz 指数 (越高越好)', fontsize=14, fontweight='bold')
    axes[1, 0].set_xticks(list(k_range))

    axes[1, 1].plot(k_range, db_list, 'md-', linewidth=2, markersize=8)
    axes[1, 1].set_xlabel('聚类数 K', fontsize=12)
    axes[1, 1].set_ylabel('DB 指数', fontsize=12)
    axes[1, 1].set_title('Davies-Bouldin 指数 (越低越好)', fontsize=14, fontweight='bold')
    axes[1, 1].set_xticks(list(k_range))

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_FIG, 'ml_fig1_kmeans_elbow_method.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  肘部法则图已保存: ml_fig1_kmeans_elbow_method.png")

    # 选择最佳 K：综合肘部和轮廓系数
    # 肘部法则找拐点，轮廓系数找最大值
    best_k_sil = k_range[np.argmax(silhouette_list)]
    # 肘部拐点：SSE下降率最大的位置
    sse_diff = np.diff(sse_list)
    sse_diff2 = np.diff(sse_diff)
    elbow_k = k_range[np.argmax(sse_diff2) + 1] if len(sse_diff2) > 0 else best_k_sil

    # 综合选择：优先肘部拐点，若轮廓系数在该K处不是太差就用
    best_k = elbow_k
    print(f"  肘部拐点 K={elbow_k}, 轮廓系数最优 K={best_k_sil}")
    print(f"  最终选择 K={best_k}")

    # 训练最终模型
    final_km = KMeans(n_clusters=best_k, random_state=RANDOM_STATE, n_init=KMEANS_N_INIT)
    station_feats['cluster'] = final_km.fit_predict(X_scaled)

    # 聚类评估指标
    final_silhouette = silhouette_score(X_scaled, station_feats['cluster'])
    final_ch = calinski_harabasz_score(X_scaled, station_feats['cluster'])
    final_db = davies_bouldin_score(X_scaled, station_feats['cluster'])
    print(f"  最终聚类评估: 轮廓系数={final_silhouette:.4f}, CH={final_ch:.2f}, DB={final_db:.4f}")

    # --- 各簇特征汇总 ---
    cluster_summary = station_feats.groupby('cluster').agg(
        station_count=('station_name', 'count'),
        avg_total_trips=('total_trips', 'mean'),
        avg_duration=('avg_duration', 'mean'),
        avg_peak_hour=('peak_hour', 'mean'),
        avg_morning_ratio=('morning_peak_ratio', 'mean'),
        avg_evening_ratio=('evening_peak_ratio', 'mean'),
        avg_weekend_ratio=('weekend_ratio', 'mean'),
        avg_subscriber_ratio=('subscriber_ratio', 'mean'),
        avg_flow_balance=('flow_balance', 'mean'),
        avg_lat=('lat', 'mean'),
        avg_lng=('lng', 'mean'),
    ).round(3)

    # 给簇命名（基于特征模式，流量分高/中/低三档）
    # 阈值：>1.5×中位数=高流量，<0.9×中位数=低流量，其余=中流量（与运营建议判定统一）
    FLOW_HIGH_RATIO = 1.5
    FLOW_LOW_RATIO = 0.9
    flow_median = cluster_summary['avg_total_trips'].median()

    def classify_flow(trips):
        if trips > flow_median * FLOW_HIGH_RATIO:
            return '高流量'
        if trips < flow_median * FLOW_LOW_RATIO:
            return '低流量'
        return '中流量'

    cluster_names = {}
    for c in cluster_summary.index:
        row = cluster_summary.loc[c]
        flow = classify_flow(row['avg_total_trips'])
        tags = [flow]
        if row['avg_weekend_ratio'] > 0.3:
            tags.append('休闲型')
        elif row['avg_morning_ratio'] > 0.15 or row['avg_evening_ratio'] > 0.2:
            tags.append('通勤型')
        else:
            tags.append('综合型')
        if row['avg_subscriber_ratio'] > 0.75:
            tags.append('会员主导')
        cluster_names[c] = f"簇{c}({'·'.join(tags)})"

    cluster_summary['cluster_name'] = pd.Series(cluster_names)
    print("\n  各簇特征汇总:")
    print(cluster_summary[['station_count', 'avg_total_trips', 'avg_duration',
                            'avg_weekend_ratio', 'avg_subscriber_ratio', 'cluster_name']].to_string())

    # 保存聚类结果
    station_feats.to_csv(os.path.join(OUTPUT_MODEL, 'kmeans_clustering_results.csv'),
                          index=False, encoding='utf-8-sig')
    cluster_summary.to_csv(os.path.join(OUTPUT_MODEL, 'kmeans_cluster_summary.csv'),
                           encoding='utf-8-sig')

    # --- 聚类深化：每簇判别特征（相对整体均值的标准化偏差Top3）+ 运营建议 ---
    print("\n  聚类深化解读（判别特征 + 运营建议）...")
    cluster_feats_mean = station_feats[cluster_cols].mean()
    cluster_feats_std = station_feats[cluster_cols].std() + 1e-8
    FEATURE_CN = {
        'total_trips': '总流量', 'avg_duration': '平均时长', 'peak_hour': '高峰小时',
        'morning_peak_ratio': '早高峰占比', 'evening_peak_ratio': '晚高峰占比',
        'weekend_ratio': '周末占比', 'subscriber_ratio': '会员占比',
        'flow_balance': '流量平衡度', 'lat': '纬度', 'lng': '经度',
    }

    def gen_cluster_advice(row):
        """基于簇特征规则生成运营建议（规则可解释，非编造）"""
        flow = classify_flow(row['avg_total_trips'])
        if row['avg_weekend_ratio'] > 0.3:
            style = '休闲型'
        elif row['avg_morning_ratio'] > 0.15 or row['avg_evening_ratio'] > 0.2:
            style = '通勤型'
        else:
            style = '综合型'
        if flow == '高流量' and style == '通勤型':
            return '通勤枢纽站：早晚高峰潮汐明显，建议高峰前预调度车辆、推出会员通勤套餐，并联动地铁口布点'
        if flow == '高流量' and style == '休闲型':
            return '热门休闲站：周末与节假日客流集中，建议周末加密车辆、与周边商业/景区联动营销'
        if flow == '中流量' and style == '通勤型':
            return '中等通勤站：日均需求中等但高峰时段稳定，建议高峰加密班次、平峰期向热点站错峰调拨冗余车辆'
        if flow == '低流量' and style == '休闲型':
            return '低频休闲站：整体需求平缓，建议控制投放规模、按需调度，避免车辆长期闲置'
        if flow == '低流量' and style == '通勤型':
            return '社区通勤站：高峰时段有稳定通勤需求，建议高峰保障运力、平峰期向热点站调拨'
        return '均衡型站点：维持现有运力配置，结合节假日与大型活动动态调整'

    insight_rows = []
    for c in cluster_summary.index:
        row = station_feats[station_feats['cluster'] == c][cluster_cols].mean()
        z = (row - cluster_feats_mean) / cluster_feats_std
        top3 = z.abs().sort_values(ascending=False).head(3)
        desc = '；'.join(
            f"{FEATURE_CN.get(f, f)}{'偏高' if z[f] > 0 else '偏低'}"
            for f in top3.index
        )
        advice = gen_cluster_advice(cluster_summary.loc[c])
        insight_rows.append({
            '簇编号': c,
            '簇名称': cluster_names[c],
            '站点数': int((station_feats['cluster'] == c).sum()),
            '判别特征Top3': desc,
            '运营建议': advice,
        })
    insight_df = pd.DataFrame(insight_rows)
    insight_df.to_csv(os.path.join(OUTPUT_MODEL, 'kmeans_cluster_insights.csv'),
                      index=False, encoding='utf-8-sig')
    for _, r in insight_df.iterrows():
        print(f"  {r['簇名称']}: {r['判别特征Top3']}")
        print(f"    建议: {r['运营建议']}")

    # --- 可视化1：聚类散点图（经纬度空间分布）---
    fig, ax = plt.subplots(figsize=(12, 9))
    colors = plt.cm.Set2(np.linspace(0, 1, best_k))
    for c in range(best_k):
        mask = station_feats['cluster'] == c
        ax.scatter(station_feats.loc[mask, 'lng'], station_feats.loc[mask, 'lat'],
                   c=[colors[c]], label=cluster_names[c], alpha=0.7, s=50, edgecolors='white', linewidth=0.5)
    ax.set_xlabel('经度 (Longitude)', fontsize=12)
    ax.set_ylabel('纬度 (Latitude)', fontsize=12)
    ax.set_title(f'纽约 Citi Bike 站点 KMeans 聚类空间分布 (K={best_k})', fontsize=14, fontweight='bold')
    ax.legend(fontsize=10, loc='best')
    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_FIG, 'ml_fig2_kmeans_spatial_distribution.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  空间分布图已保存: ml_fig2_kmeans_spatial_distribution.png")

    # --- 可视化2：聚类特征雷达图 ---
    radar_cols = ['total_trips', 'avg_duration', 'morning_peak_ratio',
                  'evening_peak_ratio', 'weekend_ratio', 'subscriber_ratio', 'flow_balance']
    # 标准化到0-1用于雷达图
    radar_data = station_feats.groupby('cluster')[radar_cols].mean()
    radar_norm = (radar_data - radar_data.min()) / (radar_data.max() - radar_data.min() + 1e-8)

    angles = np.linspace(0, 2 * np.pi, len(radar_cols), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))
    for c in range(best_k):
        values = radar_norm.loc[c].tolist()
        values += values[:1]
        ax.plot(angles, values, 'o-', linewidth=2, label=cluster_names[c], color=colors[c])
        ax.fill(angles, values, alpha=0.15, color=colors[c])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(['总流量', '平均时长', '早高峰占比', '晚高峰占比',
                        '周末占比', '会员占比', '流量平衡度'], fontsize=11)
    ax.set_ylim(0, 1)
    ax.set_title(f'各簇站点特征雷达图 (K={best_k})', fontsize=14, fontweight='bold', pad=20)
    ax.legend(loc='upper right', bbox_to_anchor=(1.3, 1.1), fontsize=10)
    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_FIG, 'ml_fig3_kmeans_radar_chart.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  雷达图已保存: ml_fig3_kmeans_radar_chart.png")

    # --- 可视化3：各簇站点数量柱状图 ---
    fig, ax = plt.subplots(figsize=(10, 6))
    counts = station_feats['cluster'].value_counts().sort_index()
    bars = ax.bar([cluster_names[c] for c in counts.index], counts.values,
                  color=[colors[c] for c in counts.index], edgecolor='white', linewidth=1.5)
    for bar, val in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                str(val), ha='center', va='bottom', fontsize=12, fontweight='bold')
    ax.set_ylabel('站点数量', fontsize=12)
    ax.set_title(f'各簇站点数量分布 (K={best_k})', fontsize=14, fontweight='bold')
    plt.xticks(rotation=15, ha='right')
    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_FIG, 'ml_fig4_kmeans_cluster_count.png'), dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  簇数量图已保存: ml_fig4_kmeans_cluster_count.png")

    # 保存聚类评估指标
    eval_df = pd.DataFrame({
        '指标': ['最佳聚类数K', '轮廓系数(Silhouette)', 'CH指数(Calinski-Harabasz)',
                'DB指数(Davies-Bouldin)', 'SSE(簇内平方和)'],
        '数值': [best_k, round(final_silhouette, 4), round(final_ch, 2),
                round(final_db, 4), round(final_km.inertia_, 2)]
    })
    eval_df.to_csv(os.path.join(OUTPUT_MODEL, 'kmeans_evaluation_metrics.csv'),
                   index=False, encoding='utf-8-sig')

    return station_feats, best_k, cluster_names


# ============================================================
# 模块二：骑行时长预测（回归）
# ============================================================
def predict_duration(df):
    """
    骑行时长预测
    目标变量：duration_min（骑行时长，分钟）
    特征：小时、星期、是否周末、用户类型、车辆类型、起止站点、月份等
    模型：线性回归、决策树、随机森林、梯度提升
    评估：R², MAE, RMSE
    """
    print("\n[4/6] 骑行时长预测模型...")

    # 构建特征
    data = df.copy()
    # 目标变量
    y = data['duration_min'].values

    # 特征工程
    features = pd.DataFrame()
    # Haversine骑行距离——时长预测最核心特征（贡献约60%+解释力）
    features['distance_km'] = data['distance_km']
    features['hour'] = data['hour']
    features['weekday'] = data['weekday']
    features['is_weekend'] = data['is_weekend']
    features['month'] = data['start_date'].dt.month
    features['day_of_month'] = data['start_date'].dt.day

    # 分类变量 one-hot 编码
    user_type_dummy = pd.get_dummies(data['user_type'], prefix='user_type')
    rideable_dummy = pd.get_dummies(data['rideable_type'], prefix='bike_type')
    features = pd.concat([features, user_type_dummy, rideable_dummy], axis=1)

    # 站点流量特征（用排名代替one-hot，降维）
    station_start_count = data['start_station'].value_counts()
    station_end_count = data['end_station'].value_counts()
    features['start_station_popularity'] = data['start_station'].map(station_start_count).fillna(0)
    features['end_station_popularity'] = data['end_station'].map(station_end_count).fillna(0)

    # 时段特征：是否高峰
    features['is_morning_peak'] = ((data['hour'] >= 7) & (data['hour'] <= 9)).astype(int)
    features['is_evening_peak'] = ((data['hour'] >= 17) & (data['hour'] <= 19)).astype(int)
    features['is_night'] = ((data['hour'] >= 22) | (data['hour'] <= 5)).astype(int)

    # 小时的正弦/余弦编码（捕捉周期性）
    features['hour_sin'] = np.sin(2 * np.pi * data['hour'] / 24)
    features['hour_cos'] = np.cos(2 * np.pi * data['hour'] / 24)

    X = features.values
    feature_names = features.columns.tolist()
    print(f"  特征维度: {X.shape[1]}")
    print(f"  特征列表: {feature_names}")

    # 划分训练集/测试集 (80/20)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE
    )
    print(f"  训练集: {X_train.shape[0]}, 测试集: {X_test.shape[0]}")

    # 标准化（对线性模型需要，树模型不需要，但统一处理）
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 定义模型池（超参数统一收敛到顶部 DURATION_MODEL_PARAMS）
    models = {
        '线性回归 (Linear Regression)': LinearRegression(),
        '岭回归 (Ridge)': Ridge(alpha=1.0, random_state=RANDOM_STATE),
        '决策树 (Decision Tree)': DecisionTreeRegressor(
            random_state=RANDOM_STATE, **DURATION_MODEL_PARAMS['决策树 (Decision Tree)']),
        '随机森林 (Random Forest)': RandomForestRegressor(
            random_state=RANDOM_STATE, **DURATION_MODEL_PARAMS['随机森林 (Random Forest)']),
        '梯度提升 (Gradient Boosting)': GradientBoostingRegressor(
            random_state=RANDOM_STATE, **DURATION_MODEL_PARAMS['梯度提升 (Gradient Boosting)']),
    }

    results = []
    trained_models = {}

    for name, model in models.items():
        print(f"  训练 {name}...")
        # 线性模型用标准化数据，树模型用原始数据
        if 'Linear' in name or 'Ridge' in name:
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mape = np.mean(np.abs((y_test - y_pred) / (y_test + 1e-8))) * 100

        results.append({
            '模型': name,
            'R²': round(r2, 4),
            'MAE(分钟)': round(mae, 3),
            'RMSE(分钟)': round(rmse, 3),
            'MAPE(%)': round(mape, 2),
        })
        trained_models[name] = model
        print(f"    R²={r2:.4f}, MAE={mae:.3f}min, RMSE={rmse:.3f}min")

    # 朴素基线对比：均值/中位数预测，用于衡量模型相对简单基准的真实增益
    y_mean_pred = np.full_like(y_test, y_train.mean())
    y_median_pred = np.full_like(y_test, np.median(y_train))
    for bl_name, bl_pred in [('基线-均值预测', y_mean_pred), ('基线-中位数预测', y_median_pred)]:
        results.append({
            '模型': bl_name,
            'R²': round(r2_score(y_test, bl_pred), 4),
            'MAE(分钟)': round(mean_absolute_error(y_test, bl_pred), 3),
            'RMSE(分钟)': round(np.sqrt(mean_squared_error(y_test, bl_pred)), 3),
            'MAPE(%)': round(np.mean(np.abs((y_test - bl_pred) / (y_test + 1e-8))) * 100, 2),
        })
    print("  朴素基线对比完成: 均值/中位数预测")

    results_df = pd.DataFrame(results)
    results_df.to_csv(os.path.join(OUTPUT_MODEL, 'duration_prediction_report.csv'),
                      index=False, encoding='utf-8-sig')
    print("\n  骑行时长预测模型对比:")
    print(results_df.to_string(index=False))

    # 选择最佳模型（R²最高）
    best_model_name = results_df.loc[results_df['R²'].idxmax(), '模型']
    best_model = trained_models[best_model_name]
    print(f"\n  最佳模型: {best_model_name}")

    # 特征重要性（树模型）
    if hasattr(best_model, 'feature_importances_'):
        importances = best_model.feature_importances_
        feat_imp = pd.DataFrame({
            '特征': feature_names,
            '重要性': importances
        }).sort_values('重要性', ascending=False)
        feat_imp.to_csv(os.path.join(OUTPUT_MODEL, 'duration_feature_importance.csv'),
                        index=False, encoding='utf-8-sig')

        # 特征重要性可视化
        fig, ax = plt.subplots(figsize=(12, 8))
        top_n = min(15, len(feat_imp))
        top_feats = feat_imp.head(top_n).iloc[::-1]
        ax.barh(range(top_n), top_feats['重要性'].values, color='steelblue', edgecolor='white')
        ax.set_yticks(range(top_n))
        ax.set_yticklabels(top_feats['特征'].values, fontsize=11)
        ax.set_xlabel('特征重要性', fontsize=12)
        ax.set_title(f'骑行时长预测 - 特征重要性排名 ({best_model_name})', fontsize=14, fontweight='bold')
        for i, v in enumerate(top_feats['重要性'].values):
            ax.text(v + 0.001, i, f'{v:.4f}', va='center', fontsize=10)
        plt.tight_layout()
        fig.savefig(os.path.join(OUTPUT_FIG, 'ml_fig5_duration_feature_importance.png'),
                    dpi=150, bbox_inches='tight')
        plt.close(fig)
        print("  特征重要性图已保存: ml_fig5_duration_feature_importance.png")

    # 预测值 vs 真实值散点图（最佳模型）
    if 'Linear' in best_model_name or 'Ridge' in best_model_name:
        y_pred_best = best_model.predict(X_test_scaled)
    else:
        y_pred_best = best_model.predict(X_test)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # 散点图
    sample_idx = np.random.choice(len(y_test), size=min(5000, len(y_test)), replace=False)
    axes[0].scatter(y_test[sample_idx], y_pred_best[sample_idx], alpha=0.3, s=10, c='steelblue')
    max_val = max(y_test.max(), y_pred_best.max())
    axes[0].plot([0, max_val], [0, max_val], 'r--', linewidth=2, label='完美预测线')
    axes[0].set_xlabel('真实骑行时长 (分钟)', fontsize=12)
    axes[0].set_ylabel('预测骑行时长 (分钟)', fontsize=12)
    axes[0].set_title(f'预测值 vs 真实值 ({best_model_name})', fontsize=14, fontweight='bold')
    axes[0].legend(fontsize=11)
    axes[0].set_xlim(0, np.percentile(y_test, 99))
    axes[0].set_ylim(0, np.percentile(y_pred_best, 99))

    # 残差分布
    residuals = y_test - y_pred_best
    axes[1].hist(residuals, bins=100, color='coral', edgecolor='white', alpha=0.7, density=True)
    axes[1].axvline(x=0, color='black', linestyle='--', linewidth=2)
    axes[1].set_xlabel('残差 (真实 - 预测)', fontsize=12)
    axes[1].set_ylabel('密度', fontsize=12)
    axes[1].set_title('残差分布图', fontsize=14, fontweight='bold')
    axes[1].set_xlim(np.percentile(residuals, 1), np.percentile(residuals, 99))

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_FIG, 'ml_fig6_duration_prediction_scatter.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  预测散点图已保存: ml_fig6_duration_prediction_scatter.png")

    # 模型对比柱状图
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    x = range(len(results_df))
    model_labels = [m.split(' ')[0] for m in results_df['模型']]

    axes[0].bar(x, results_df['R²'], color='steelblue', edgecolor='white')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(model_labels, rotation=20, ha='right')
    axes[0].set_ylabel('R²', fontsize=12)
    axes[0].set_title('模型 R² 对比 (越高越好)', fontsize=13, fontweight='bold')
    for i, v in enumerate(results_df['R²']):
        axes[0].text(i, v + 0.005, f'{v:.3f}', ha='center', fontsize=10)

    axes[1].bar(x, results_df['MAE(分钟)'], color='coral', edgecolor='white')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(model_labels, rotation=20, ha='right')
    axes[1].set_ylabel('MAE (分钟)', fontsize=12)
    axes[1].set_title('模型 MAE 对比 (越低越好)', fontsize=13, fontweight='bold')
    for i, v in enumerate(results_df['MAE(分钟)']):
        axes[1].text(i, v + 0.1, f'{v:.2f}', ha='center', fontsize=10)

    axes[2].bar(x, results_df['RMSE(分钟)'], color='seagreen', edgecolor='white')
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(model_labels, rotation=20, ha='right')
    axes[2].set_ylabel('RMSE (分钟)', fontsize=12)
    axes[2].set_title('模型 RMSE 对比 (越低越好)', fontsize=13, fontweight='bold')
    for i, v in enumerate(results_df['RMSE(分钟)']):
        axes[2].text(i, v + 0.1, f'{v:.2f}', ha='center', fontsize=10)

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_FIG, 'ml_fig7_duration_model_comparison.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  模型对比图已保存: ml_fig7_duration_model_comparison.png")

    # 误差归因分析：按真实骑行时长分桶统计最佳模型 MAE，定位误差集中在哪类骑行
    buckets = [0, 5, 10, 15, 30, 60, np.inf]
    labels = ['<5分钟', '5-10分钟', '10-15分钟', '15-30分钟', '30-60分钟', '>60分钟']
    err_df = pd.DataFrame({'真实时长': y_test, '预测时长': y_pred_best})
    err_df['绝对误差'] = (err_df['真实时长'] - err_df['预测时长']).abs()
    err_df['时长区间'] = pd.cut(err_df['真实时长'], bins=buckets, labels=labels, right=True)
    error_analysis = err_df.groupby('时长区间', observed=True).agg(
        样本数=('真实时长', 'count'),
        真实均值=('真实时长', 'mean'),
        MAE=('绝对误差', 'mean'),
    ).round(3)
    error_analysis['MAE占比'] = (error_analysis['MAE'] / error_analysis['MAE'].sum() * 100).round(1)
    error_analysis.to_csv(os.path.join(OUTPUT_MODEL, 'duration_error_analysis.csv'),
                          encoding='utf-8-sig')
    print("\n  误差归因分析（按真实时长分桶）:")
    print(error_analysis.to_string())

    return results_df


# ============================================================
# 模块三：客流预测（小时级流量回归）
# ============================================================
def predict_demand(df):
    """
    客流预测：按小时聚合总骑行量，预测未来小时流量
    目标变量：hourly_rides（每小时骑行次数）
    特征：小时、星期、是否周末、日期、滞后特征等
    模型：线性回归、随机森林、梯度提升
    评估：R², MAE, RMSE
    """
    print("\n[5/6] 客流预测模型...")

    # 按小时聚合
    hourly = df.groupby(['start_date', 'hour']).agg(
        hourly_rides=('ride_duration', 'count'),
        avg_duration=('duration_min', 'mean'),
        subscriber_count=('user_type', lambda x: (x == 'Subscriber').sum()),
    ).reset_index()

    hourly['is_weekend'] = hourly['start_date'].dt.dayofweek.isin([5, 6]).astype(int)
    hourly['weekday'] = hourly['start_date'].dt.dayofweek
    hourly['day_of_month'] = hourly['start_date'].dt.day

    print(f"  小时级样本数: {len(hourly)}")
    print(f"  时间范围: {hourly['start_date'].min().date()} ~ {hourly['start_date'].max().date()}")

    # 特征工程
    features = pd.DataFrame()
    features['hour'] = hourly['hour']
    features['weekday'] = hourly['weekday']
    features['is_weekend'] = hourly['is_weekend']
    features['day_of_month'] = hourly['day_of_month']

    # 小时周期性编码
    features['hour_sin'] = np.sin(2 * np.pi * hourly['hour'] / 24)
    features['hour_cos'] = np.cos(2 * np.pi * hourly['hour'] / 24)

    # 星期周期性编码
    features['weekday_sin'] = np.sin(2 * np.pi * hourly['weekday'] / 7)
    features['weekday_cos'] = np.cos(2 * np.pi * hourly['weekday'] / 7)

    # 滞后特征：前1小时、前24小时的流量
    hourly_sorted = hourly.sort_values(['start_date', 'hour']).reset_index(drop=True)
    features['lag_1h'] = hourly_sorted['hourly_rides'].shift(1).bfill()
    features['lag_24h'] = hourly_sorted['hourly_rides'].shift(24).bfill()
    # 滑动平均
    features['rolling_3h_mean'] = hourly_sorted['hourly_rides'].shift(1).rolling(3).mean().bfill()

    # 是否高峰
    features['is_morning_peak'] = ((hourly['hour'] >= 7) & (hourly['hour'] <= 9)).astype(int)
    features['is_evening_peak'] = ((hourly['hour'] >= 17) & (hourly['hour'] <= 19)).astype(int)

    X = features.values
    y = hourly_sorted['hourly_rides'].values
    feature_names = features.columns.tolist()

    print(f"  特征维度: {X.shape[1]}")
    print(f"  特征列表: {feature_names}")

    # 时间序列划分：前80%训练，后20%测试（不能随机打乱）
    split_idx = int(len(X) * 0.8)
    X_train, X_test = X[:split_idx], X[split_idx:]
    y_train, y_test = y[:split_idx], y[split_idx:]
    print(f"  训练集: {X_train.shape[0]} 小时, 测试集: {X_test.shape[0]} 小时")

    # 标准化
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # 模型池（超参数统一收敛到顶部 DEMAND_MODEL_PARAMS）
    models = {
        '线性回归 (Linear Regression)': LinearRegression(),
        '岭回归 (Ridge)': Ridge(alpha=1.0, random_state=RANDOM_STATE),
        '决策树 (Decision Tree)': DecisionTreeRegressor(
            random_state=RANDOM_STATE, **DEMAND_MODEL_PARAMS['决策树 (Decision Tree)']),
        '随机森林 (Random Forest)': RandomForestRegressor(
            random_state=RANDOM_STATE, **DEMAND_MODEL_PARAMS['随机森林 (Random Forest)']),
        '梯度提升 (Gradient Boosting)': GradientBoostingRegressor(
            random_state=RANDOM_STATE, **DEMAND_MODEL_PARAMS['梯度提升 (Gradient Boosting)']),
    }

    results = []
    trained_models = {}

    for name, model in models.items():
        print(f"  训练 {name}...")
        if 'Linear' in name or 'Ridge' in name:
            model.fit(X_train_scaled, y_train)
            y_pred = model.predict(X_test_scaled)
        else:
            model.fit(X_train, y_train)
            y_pred = model.predict(X_test)

        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        mape = np.mean(np.abs((y_test - y_pred) / (y_test + 1e-8))) * 100

        results.append({
            '模型': name,
            'R²': round(r2, 4),
            'MAE(次/小时)': round(mae, 2),
            'RMSE(次/小时)': round(rmse, 2),
            'MAPE(%)': round(mape, 2),
        })
        trained_models[name] = model
        print(f"    R²={r2:.4f}, MAE={mae:.2f}, RMSE={rmse:.2f}")

    # 朴素基线对比：均值/中位数预测（客流为时间序列，基线=历史均值水平）
    y_mean_pred = np.full_like(y_test, y_train.mean())
    y_median_pred = np.full_like(y_test, np.median(y_train))
    for bl_name, bl_pred in [('基线-均值预测', y_mean_pred), ('基线-中位数预测', y_median_pred)]:
        results.append({
            '模型': bl_name,
            'R²': round(r2_score(y_test, bl_pred), 4),
            'MAE(次/小时)': round(mean_absolute_error(y_test, bl_pred), 2),
            'RMSE(次/小时)': round(np.sqrt(mean_squared_error(y_test, bl_pred)), 2),
            'MAPE(%)': round(np.mean(np.abs((y_test - bl_pred) / (y_test + 1e-8))) * 100, 2),
        })
    print("  朴素基线对比完成: 均值/中位数预测")

    results_df = pd.DataFrame(results)
    results_df.to_csv(os.path.join(OUTPUT_MODEL, 'demand_prediction_report.csv'),
                      index=False, encoding='utf-8-sig')
    print("\n  客流预测模型对比:")
    print(results_df.to_string(index=False))

    # 最佳模型
    best_model_name = results_df.loc[results_df['R²'].idxmax(), '模型']
    best_model = trained_models[best_model_name]
    print(f"\n  最佳模型: {best_model_name}")

    # 特征重要性
    if hasattr(best_model, 'feature_importances_'):
        importances = best_model.feature_importances_
        feat_imp = pd.DataFrame({
            '特征': feature_names,
            '重要性': importances
        }).sort_values('重要性', ascending=False)
        feat_imp.to_csv(os.path.join(OUTPUT_MODEL, 'demand_feature_importance.csv'),
                        index=False, encoding='utf-8-sig')

        fig, ax = plt.subplots(figsize=(12, 7))
        top_n = min(15, len(feat_imp))
        top_feats = feat_imp.head(top_n).iloc[::-1]
        ax.barh(range(top_n), top_feats['重要性'].values, color='darkorange', edgecolor='white')
        ax.set_yticks(range(top_n))
        ax.set_yticklabels(top_feats['特征'].values, fontsize=11)
        ax.set_xlabel('特征重要性', fontsize=12)
        ax.set_title(f'客流预测 - 特征重要性排名 ({best_model_name})', fontsize=14, fontweight='bold')
        for i, v in enumerate(top_feats['重要性'].values):
            ax.text(v + 0.005, i, f'{v:.4f}', va='center', fontsize=10)
        plt.tight_layout()
        fig.savefig(os.path.join(OUTPUT_FIG, 'ml_fig8_demand_feature_importance.png'),
                    dpi=150, bbox_inches='tight')
        plt.close(fig)
        print("  特征重要性图已保存: ml_fig8_demand_feature_importance.png")

    # 预测时序图
    if 'Linear' in best_model_name or 'Ridge' in best_model_name:
        y_pred_best = best_model.predict(X_test_scaled)
    else:
        y_pred_best = best_model.predict(X_test)

    test_dates = hourly_sorted.iloc[split_idx:].copy()
    test_dates['datetime'] = pd.to_datetime(test_dates['start_date']) + pd.to_timedelta(test_dates['hour'], unit='h')

    fig, ax = plt.subplots(figsize=(16, 7))
    ax.plot(test_dates['datetime'], y_test, 'b-', linewidth=1.5, label='真实流量', alpha=0.8)
    ax.plot(test_dates['datetime'], y_pred_best, 'r--', linewidth=1.5, label='预测流量', alpha=0.8)
    ax.set_xlabel('时间', fontsize=12)
    ax.set_ylabel('每小时骑行次数', fontsize=12)
    ax.set_title(f'客流预测时序对比 ({best_model_name}, 测试集)', fontsize=14, fontweight='bold')
    ax.legend(fontsize=12)
    plt.xticks(rotation=30, ha='right')
    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_FIG, 'ml_fig9_demand_prediction_timeseries.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  预测时序图已保存: ml_fig9_demand_prediction_timeseries.png")

    # 模型对比图
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    x = range(len(results_df))
    model_labels = [m.split(' ')[0] for m in results_df['模型']]

    axes[0].bar(x, results_df['R²'], color='steelblue', edgecolor='white')
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(model_labels, rotation=20, ha='right')
    axes[0].set_ylabel('R²', fontsize=12)
    axes[0].set_title('模型 R² 对比 (越高越好)', fontsize=13, fontweight='bold')
    for i, v in enumerate(results_df['R²']):
        axes[0].text(i, v + 0.005, f'{v:.3f}', ha='center', fontsize=10)

    axes[1].bar(x, results_df['MAE(次/小时)'], color='coral', edgecolor='white')
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(model_labels, rotation=20, ha='right')
    axes[1].set_ylabel('MAE (次/小时)', fontsize=12)
    axes[1].set_title('模型 MAE 对比 (越低越好)', fontsize=13, fontweight='bold')
    for i, v in enumerate(results_df['MAE(次/小时)']):
        axes[1].text(i, v + 5, f'{v:.1f}', ha='center', fontsize=10)

    axes[2].bar(x, results_df['RMSE(次/小时)'], color='seagreen', edgecolor='white')
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(model_labels, rotation=20, ha='right')
    axes[2].set_ylabel('RMSE (次/小时)', fontsize=12)
    axes[2].set_title('模型 RMSE 对比 (越低越好)', fontsize=13, fontweight='bold')
    for i, v in enumerate(results_df['RMSE(次/小时)']):
        axes[2].text(i, v + 5, f'{v:.1f}', ha='center', fontsize=10)

    plt.tight_layout()
    fig.savefig(os.path.join(OUTPUT_FIG, 'ml_fig10_demand_model_comparison.png'),
                dpi=150, bbox_inches='tight')
    plt.close(fig)
    print("  模型对比图已保存: ml_fig10_demand_model_comparison.png")

    # 误差归因分析：按真实小时流量分桶统计最佳模型 MAE，定位误差集中的流量区间
    buckets = [0, 20, 50, 100, 200, np.inf]
    labels = ['<20次', '20-50次', '50-100次', '100-200次', '>200次']
    err_df = pd.DataFrame({'真实流量': y_test, '预测流量': y_pred_best})
    err_df['绝对误差'] = (err_df['真实流量'] - err_df['预测流量']).abs()
    err_df['流量区间'] = pd.cut(err_df['真实流量'], bins=buckets, labels=labels, right=True)
    error_analysis = err_df.groupby('流量区间', observed=True).agg(
        样本数=('真实流量', 'count'),
        真实均值=('真实流量', 'mean'),
        MAE=('绝对误差', 'mean'),
    ).round(3)
    error_analysis['MAE占比'] = (error_analysis['MAE'] / error_analysis['MAE'].sum() * 100).round(1)
    error_analysis.to_csv(os.path.join(OUTPUT_MODEL, 'demand_error_analysis.csv'),
                          encoding='utf-8-sig')
    print("\n  误差归因分析（按真实小时流量分桶）:")
    print(error_analysis.to_string())

    return results_df


# ============================================================
# 主函数
# ============================================================
def main():
    print("=" * 70)
    print("  纽约公共自行车数据分析 - 机器学习模块 (成员4)")
    print("  KMeans 站点聚类 + 骑行时长预测 + 客流预测")
    print("=" * 70)

    # 1. 加载数据
    df = load_data()

    # 2. KMeans 站点聚类
    station_feats, cluster_cols = build_station_features(df)
    station_feats, best_k, cluster_names = kmeans_clustering(station_feats, cluster_cols)
    cluster_insights = pd.read_csv(os.path.join(OUTPUT_MODEL, 'kmeans_cluster_insights.csv'),
                                   encoding='utf-8-sig')

    # 3. 骑行时长预测
    duration_results = predict_duration(df)

    # 4. 客流预测
    demand_results = predict_demand(df)

    # 5. 生成总结报告
    print("\n[6/6] 生成机器学习总结报告...")
    summary = []
    summary.append("=" * 60)
    summary.append("  纽约公共自行车 - 机器学习模块总结报告 (成员4)")
    summary.append("=" * 60)
    summary.append("")
    summary.append("一、KMeans 站点聚类")
    summary.append(f"  - 有效站点数: {len(station_feats)}")
    summary.append(f"  - 聚类特征维度: {len(cluster_cols)}")
    summary.append(f"  - 最佳聚类数 K: {best_k}")
    summary.append(f"  - 各簇站点数: {station_feats['cluster'].value_counts().sort_index().to_dict()}")
    summary.append("  聚类深化解读（判别特征 + 运营建议）:")
    for _, r in cluster_insights.iterrows():
        summary.append(f"    - {r['簇名称']} ({r['站点数']}站): 判别特征 {r['判别特征Top3']}")
        summary.append(f"      运营建议: {r['运营建议']}")
    summary.append("")
    summary.append("二、骑行时长预测 (5种模型 + 2朴素基线对比)")
    for _, row in duration_results.iterrows():
        summary.append(f"  - {row['模型']}: R²={row['R²']}, MAE={row['MAE(分钟)']}min, RMSE={row['RMSE(分钟)']}min")
    summary.append("")
    summary.append("三、客流预测 (5种模型 + 2朴素基线对比)")
    for _, row in demand_results.iterrows():
        summary.append(f"  - {row['模型']}: R²={row['R²']}, MAE={row['MAE(次/小时)']}, RMSE={row['RMSE(次/小时)']}")
    summary.append("")
    summary.append("四、预测误差归因分析")
    dur_ea = pd.read_csv(os.path.join(OUTPUT_MODEL, 'duration_error_analysis.csv'), encoding='utf-8-sig')
    summary.append("  骑行时长预测误差（按真实时长分桶，最佳模型）:")
    for _, r in dur_ea.iterrows():
        summary.append(f"    - {r['时长区间']}: 样本{r['样本数']}条, 真实均值{r['真实均值']}min, MAE={r['MAE']}min, 占{r['MAE占比']}%")
    dem_ea = pd.read_csv(os.path.join(OUTPUT_MODEL, 'demand_error_analysis.csv'), encoding='utf-8-sig')
    summary.append("  客流预测误差（按小时流量分桶，最佳模型）:")
    for _, r in dem_ea.iterrows():
        summary.append(f"    - {r['流量区间']}: 样本{r['样本数']}条, 真实均值{r['真实均值']}次, MAE={r['MAE']}次, 占{r['MAE占比']}%")
    summary.append("")
    summary.append("五、输出文件清单")
    summary.append("  output/model/:")
    for f in sorted(os.listdir(OUTPUT_MODEL)):
        summary.append(f"    - {f}")
    summary.append("  output/fig/:")
    for f in sorted(os.listdir(OUTPUT_FIG)):
        if f.startswith('ml_'):
            summary.append(f"    - {f}")
    summary.append("")
    summary.append("=" * 60)
    summary.append("  机器学习模块全部完成！")
    summary.append("=" * 60)

    report_text = "\n".join(summary)
    with open(os.path.join(OUTPUT_MODEL, 'ml_summary_report.txt'), 'w', encoding='utf-8') as f:
        f.write(report_text)
    print(report_text)


if __name__ == '__main__':
    main()
