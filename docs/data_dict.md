# 数据字典与清洗规范（data_dict.md）

> 组长统一编制，**全员必须遵守**。
> 本文件是各成员模块间的"接口契约"：字段名、字段格式、清洗规则都以本文档为准。
> 版本：v1.1（2026-09）
> 适用数据月份：202607（纽约 Citi Bike 2026 年 7 月真实数据）

---

## 一、数据来源

- 官方页面：<https://www.citibikenyc.com/system-data>
- 官方数据服务器：<https://s3.amazonaws.com/tripdata/>
- 本机已下载：`C:\Users\Lenovo\Downloads\202607-citibike-tripdata.zip`（约 930MB）

> 说明：2026 年 7 月为**大月份**，官方 zip 内拆成 5 个 CSV 分片
> （`202607-citibike-tripdata_1.csv` ~ `_5.csv`，每个约 185MB）。
> `download_data.py` 会自动解压并合并为一份。

---

## 二、目录约定（各组员代码里请用 `config.py` 的常量，不写死路径）

| 用途 | 目录/文件 | config 常量 |
|---|---|---|
| 原始下载数据（不入库） | `data/raw/202607-citibike-tripdata.csv` | `config.RAW_DATA_FILE` |
| **清洗后标准表（下游只读这张）** | `data/clean_citibike.csv` | `config.CLEAN_DATA_FILE` |
| 统计/分析结果 | `output/` | `config.OUTPUT_DIR` |
| 图表 | `output/figures/` | `config.FIG_DIR` |
| 模型指标/聚类结果 | `output/model/` | `config.MODEL_DIR` |

> 代码里一律用 `config.XX`，由 `config.py` 统一派生绝对路径，禁止手写相对/绝对路径。

---

## 三、原始字段字典（2026 版，`data/raw/` 合并前）

| 原始字段名 | 含义 | 示例 | 备注 |
|---|---|---|---|
| `ride_id` | 行程ID | `DD531B4CAE426168` | 直接归为 `bikeid` |
| `rideable_type` | 车辆类型 | `electric_bike` | 归为 `rideable_type` |
| `started_at` | 出发时间 | `2026-07-11 16:56:58.899` | 归为 `start_time` |
| `ended_at` | 到达时间 | `2026-07-11 17:05:48.330` | 归为 `end_time` |
| `start_station_name` | 出发站名 | `Madison Ave & E 99 St` | 归为 `start_station` |
| `start_station_id` | 出发站ID | `7443.01` | 归为 `start_station_id` |
| `end_station_name` | 到达站名 | `W 82 St & Central Park W` | 归为 `end_station` |
| `end_station_id` | 到达站ID | `7304.08` | 归为 `end_station_id` |
| `start_lat` | 出发纬度 | `40.789485` | |
| `start_lng` | 出发经度 | `-73.952429` | |
| `end_lat` | 到达纬度 | `40.782750` | |
| `end_lng` | 到达经度 | `-73.971370` | |
| `member_casual` | 会员/单次 | `member`/`casual` | 归为 `user_type` |

> 注意：**2026 新格式没有 `tripduration` 字段**，骑行时长需用
> `ended_at - started_at` 计算（`preprocess.py` 已实现自动补算）。

---

## 四、清洗后标准表（`data/clean_citibike.csv`）

成员2 在 `storage/preprocess.py` 中须输出**下列统一列名、统一类型、统一取值**，
成员3/4/5 只依赖这张表。

| 标准列名 | 类型/取值 | 说明 |
|---|---|---|
| `ride_duration` | float64，秒 | 骑行时长（<60s 已剔除，>24h 剔除） |
| `start_time` | datetime64 | 出发时间 |
| `end_time` | datetime64 | 到达时间 |
| `start_station` | str | 出发站名 |
| `end_station` | str | 到达站名 |
| `start_lat` / `start_lng` | float64 | 出发经纬度 |
| `end_lat` / `end_lng` | float64 | 到达经纬度 |
| `user_type` | str | **`Subscriber`（会员）/ `Customer`（单次）** |
| `bikeid` | str | 车辆/行程ID |
| `rideable_type` | str | `classic` / `electric`（可选） |
| `start_date` | datetime(date) | 出发日期（由 start_time 派生） |
| `hour` | int 0–23 | 出发小时 |
| `weekday` | int 0–6 | 0=周一 … 6=周日 |
| `is_weekend` | int 0/1 | 0=工作日 1=周末 |

> `gender` 字段在 2026 新格式中**已不存在**（旧版才有），各模块不要强制要求该列。

---

## 五、清洗规则（成员2 落地，务必统一）

1. **字段归一**：通过`config.RAW_ALIASES`把不同版本表头统一为标准列名。
2. **会员值归一**：`member_casual` 的 `member`→`Subscriber`、`casual`→`Customer`
   （见`config.USER_TYPE_MAP`），保证统计里会员占比不为 0%。
3. **时间解析**：`start_time`/`end_time`→`datetime64`，无法解析置 `NaT`。
4. **时长补算**：若缺 `ride_duration`，用 `end_time - start_time` 补（秒）。
5. **异常过滤**：保留 `60 <= ride_duration <= 24h`，剔除 <60s（假启动）与 >24h。
6. **抽样**：全量约数百万行，默认按 `config.SAMPLE_SIZE=200000` 抽样，
   固定 `random_state=42`，保证可复现。
7. **派生特征**：`start_date`/`hour`/`weekday`/`is_weekend` 由 `start_time` 派生。
8. **落盘**：输出到 `data/clean_citibike.csv`，编码 `utf-8-sig`，`index=False`。

---

## 六、给各成员的接口提醒

- **成员2（preprocess.py）**：输出本表第五节标准列，字段见第四节。
- **成员3（stats.py）**：读 `clean_citibike.csv`，会员占比按 `user_type` 统计
  （`Subscriber`/`Customer`）。
- **成员4（ml.py）**：读 `clean_citibike.csv`；站点聚类自建特征，时长单位秒→分钟。
- **成员5（visualize.py）**：图存 `output/figures/`，中文用 `config.CHINESE_FONT`。