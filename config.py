# -*- coding: utf-8 -*-
"""
config.py —— 项目全局配置（组长维护的"公共地基"）
=================================================
统一约定：路径、数据列名、清洗参数、可视化字体等。
所有模块都从这里读配置，改这里即可定制整个项目。
"""

import os
import matplotlib
matplotlib.use("Agg")   # 使用无窗口后端，便于保存图片
import matplotlib.pyplot as plt

# ============================================================
# 1. 基础目录（自动定位项目根目录）
# ============================================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")        # 数据总目录
RAW_DIR = os.path.join(DATA_DIR, "raw")           # 原始下载数据（不入库）
OUTPUT_DIR = os.path.join(BASE_DIR, "output")    # 分析结果+图表
FIG_DIR = os.path.join(OUTPUT_DIR, "figures")    # 图表子目录
MODEL_DIR = os.path.join(OUTPUT_DIR, "model")     # 模型指标

# 原始合并数据（download_data.py 的输出，即清洗流程的输入）
RAW_DATA_FILE = os.path.join(RAW_DIR, "202607-citibike-tripdata.csv")
# 清洗后的数据
CLEAN_DATA_FILE = os.path.join(DATA_DIR, "clean_citibike.csv")

for _d in (DATA_DIR, RAW_DIR, OUTPUT_DIR, FIG_DIR, MODEL_DIR):
    os.makedirs(_d, exist_ok=True)

# ============================================================
# 2. 数据获取参数（download_data.py 使用）
# ============================================================
BASE_URL = "https://s3.amazonaws.com/tripdata/"   # Citi Bike 官方数据服务器
DEFAULT_MONTH = "202607"                          # 默认月份 YYYYMM
DOWNLOAD_TIMEOUT = 120                            # 连接超时(秒)
FORCE_DOWNLOAD = False                            # 强制重新下载并覆盖

# 本机已下载好的官方 zip（可直接解压复用，避免重复下载 900MB+）
# 为空列表则不启用，仅走网络下载
LOCAL_ZIP_PATHS = [
    r"C:\Users\Lenovo\Downloads\202607-citibike-tripdata.zip",
]

# 若真实数据未放入，则是否使用内置示例数据兜底
USE_SAMPLE_FALLBACK = True

# ============================================================
# 3. Citi Bike 官方字段（不同版本字段名略有差异，统一起别名）
# ============================================================
# 统一后的标准列名 -> 原始可能的字段名
RAW_ALIASES = {
    "ride_duration": ["tripduration", "ride_duration"],
    "start_time":   ["starttime", "started_at"],
    "end_time":     ["stoptime", "ended_at"],
    "start_station":["start station name", "start_station_name"],
    "end_station":  ["end station name", "end_station_name"],
    "start_lat":    ["start station latitude", "start_lat"],
    "start_lng":    ["start station longitude", "start_lng"],
    "end_lat":      ["end station latitude", "end_lat"],
    "end_lng":      ["end station longitude", "end_lng"],
    "user_type":    ["usertype", "member_casual"],
    "gender":       ["gender"],
    "ride_id":      ["ride_id", "bikeid"],
    "rideable_type":  ["rideable_type"],
    "start_station_id": ["start station id", "start_station_id"],
    "end_station_id":   ["end station id", "end_station_id"],
}

# 2026 新版会员字段(member_casual) -> 统一标准值；旧版 usertype 已是 Subscriber/Customer
USER_TYPE_MAP = {
    "member": "Subscriber", "casual": "Customer",
    "subscriber": "Subscriber", "customer": "Customer",  # 兼容旧版大小写
}

# ============================================================
# 4. 清洗后统一表的字段规范（与 docs/data_dict.md 保持一致）
#    下游各成员模块只依赖此表，字段格式以此为统一标准
# ============================================================
CANONICAL_SCHEMA = {
    "ride_duration": "float64，单位：秒",
    "start_time":    "datetime64[ns]",
    "end_time":      "datetime64[ns]",
    "start_station": "str，站点名",
    "end_station":   "str，站点名",
    "start_lat":     "float64，纬度",
    "start_lng":     "float64，经度",
    "end_lat":       "float64，纬度",
    "end_lng":       "float64，经度",
    "user_type":     "str，Subscriber | Customer",
    "gender":        "int64，0未知/1男/2女（可缺省）",
    "ride_id":       "str，行程ID",
    "rideable_type": "str，classic | electric（可选）",
    "start_date":    "datetime64[ns]，由 start_time 派生",
    "hour":          "int，0-23",
    "weekday":       "int，0=周一 ~ 6=周日",
    "is_weekend":    "int，0=工作日 1=周末",
}

# ============================================================
# 5. 清洗与抽样参数
# ============================================================
# 有效骑行时长范围（秒），过滤异常：<60秒(可能假启动)，>24h(异常)
MIN_DURATION = 60
MAX_DURATION = 24 * 3600

# 经纬度合理范围（纽约附近，宽松起见；可收紧到 40.5~41.0 / -74.3~-73.7）
LAT_MIN, LAT_MAX = 0, 90
LNG_MIN, LNG_MAX = -180, 180

# 抽样：若原始数据量过大，随机抽取 N 条用于分析（0=不抽样，用全部）
SAMPLE_SIZE = 200000

# ============================================================
# 5. 中文字体（保证图表中文显示）
# ============================================================
CHINESE_FONTS = ["SimHei", "Microsoft YaHei", "SimSun", "KaiTi"]

def _setup_font():
    for f in CHINESE_FONTS:
        try:
            plt.rcParams["font.sans-serif"] = [f]
            plt.rcParams["axes.unicode_minus"] = False
            return f
        except Exception:
            continue
    return None

CHINESE_FONT = _setup_font()

# ============================================================
# 6. 机器学习参数
# ============================================================
TEST_SIZE = 0.2          # 测试集比例（训练/测试）
RANDOM_STATE = 42        # 固定随机种子，结果可复现
N_CLUSTERS = 4           # KMeans 聚类数（站点）


if __name__ == "__main__":
    print("项目根目录:", BASE_DIR)
    print("中文字体:", CHINESE_FONT if CHINESE_FONT else "未找到(图表中文将显示方块)")
    print("数据目录:", DATA_DIR)