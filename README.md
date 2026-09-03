# 纽约公共自行车数据分析与可视化（Citi Bike）

## 项目简介
基于纽约 Citi Bike 公共自行车的官方月度骑行数据，完成
**数据获取 → 数据清洗 → 描述统计 → 时空分析 → 地图可视化 → 机器学习(聚类+预测)** 的完整闭环，
可视化呈现纽约市民的共享单车出行模式。

## 环境要求
- Python 3.9+（推荐 3.10+）
- 主要依赖库：
  - pandas / numpy（数据处理）
  - matplotlib（基础可视化）
  - scikit-learn（聚类、回归预测）
  - folium / pyecharts（地图可视化，可选，用于绘制站点地图）

## 安装说明
```bash
# 1) 进入项目目录
cd nyc_citibike

# 2) 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate        # Windows

# 3) 安装依赖（版本已固定）
pip install -r requirements.txt

# 4)（可选）地图需要 folium
pip install -r requirements-optional.txt
```

## 使用说明
主程序入口为 `main.py`，按 **下载 → 清洗 → 统计 → 建模 → 画图** 依次执行：

```bash
# 一键运行完整流程（含数据获取）
python main.py

# 或只获取数据（本机已有 zip 则直接解压合并，不重复下载）
python download_data.py
```

### 真实数据使用步骤
1. 把官方 zip（如 `202607-citibike-tripdata.zip`）放进
   `config.LOCAL_ZIP_PATHS` 指向的路径（默认 `C:\Users\Lenovo\Downloads\`）。
2. 运行 `python download_data.py`：自动解压合并到 `data/raw/202607-citibike-tripdata.csv`。
3. 运行 `python main.py` 完成全流程。
4. 也可以指定其他月份：`python download_data.py --month 202508`。

> 说明：`download_data.py` 优先使用本机已下载的 zip（避免重复下载 900MB+）；
> 若没有则会自动从官网 S3 下载。详细规范见 `docs/data_dict.md`。

## 目录结构
```
nyc_citibike/
├── main.py                # 全流程入口（下载→清洗→统计→建模→画图）
├── download_data.py       # 数据下载脚本（组长）
├── config.py              # 全局配置：路径/列名/清洗参数（统一规范）
├── requirements.txt       # 锁定的依赖版本
├── docs/data_dict.md      # 字段字典与清洗规范（接口契约）
├── data/raw/              # 原始下载数据（不入库）
├── data/clean_citibike.csv# 清洗后统一标准表
├── storage/               # 数据预处理模块（成员2）
├── analysis/              # 描述统计与时空分析模块（成员3）
├── model/                 # 机器学习模块（成员4）
├── visualization/         # 可视化模块（成员5）
└── output/                # 输出结果(CSV/图表/模型指标)
```

## 数据来源
- 官方数据：https://www.citibikenyc.com/system-data （纽约Citi Bike月度行程数据，公开免费下载）