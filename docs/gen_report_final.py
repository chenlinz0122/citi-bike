# -*- coding: utf-8 -*-
"""按《软件开发实践1》项目要求模板生成期末报告（覆盖旧版）。
格式：正文宋体小四/行距20磅/首行缩进2字符；图注表注宋体5号居中。
运行：python docs/gen_report_final.py
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
import config

FIG = config.FIG_DIR
MLF = os.path.join(FIG, "ml")
M5F = os.path.join(FIG, "member5")
OUT1 = os.path.join(config.BASE_DIR, "docs", "期末报告-纽约公共自行车数据分析.docx")
OUT2 = r"D:\OneDrive\Desktop\项目提交材料\期末报告-纽约公共自行车数据分析.docx"

doc = Document()

def set_font(run, cn="宋体", size=12, bold=False):
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), cn)
    run.font.size = Pt(size)
    run.bold = bold

def body(t, indent=True):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = Pt(20)
    if indent:
        pf.first_line_indent = Pt(24)   # 小四字号×2字符
    set_font(p.add_run(t), size=12)
    return p

def h1(t):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    set_font(p.add_run(t), cn="黑体", size=14, bold=True)

def h2(t):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(6)
    set_font(p.add_run(t), cn="黑体", size=12, bold=True)

def code(t):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    pf.line_spacing = Pt(16)
    pf.left_indent = Pt(24)
    set_font(p.add_run(t), size=10.5)

def caption(t):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    set_font(p.add_run(t), size=10.5)

def fig(path, cap, width=5.0):
    if os.path.exists(path):
        doc.add_picture(path, width=Inches(width))
        doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
        caption(cap)
    else:
        print("missing:", path)

def table(headers, rows, cap=None):
    if cap:
        caption(cap)
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, htxt in enumerate(headers):
        c = t.rows[0].cells[i]
        set_font(c.paragraphs[0].add_run(htxt), size=10.5, bold=True)
        c.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            set_font(cells[i].paragraphs[0].add_run(str(v)), size=10.5)
    return t

# ================= 封面 =================
for _ in range(3):
    doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_font(p.add_run("杭州电子科技大学"), cn="黑体", size=22, bold=True)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_font(p.add_run("《软件开发实践1》大作业报告"), cn="黑体", size=18, bold=True)
for _ in range(2):
    doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_font(p.add_run("项目名称：纽约公共自行车数据分析与可视化"), size=14, bold=True)
doc.add_paragraph()
table(["学号", "姓名"],
      [["（组长，请填写）", "（组长姓名）"], ["", ""], ["", ""], ["", ""], ["", ""]])
doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
set_font(p.add_run("完成时间：2026年9月"), size=14)
doc.add_page_break()

# ================= 1 团队成员组成及分工 =================
h1("1 团队成员组成及分工")
body("本小组共5人，分工如表1所示。项目采用“统一契约、并行开发”模式：由组长先制定 "
     "config.py 列名规范与 docs/data_dict.md 接口契约，各成员模块只依赖统一标准表 "
     "clean_citibike.csv，实现零冲突对接。")
table(["学号", "姓名", "详细任务分工", "工作量占比"],
      [["（组长）", "", "整体架构设计；CSV列名规范与目录结构约定（config.py、docs/data_dict.md）；接口文档编写；download_data.py 数据获取脚本与 main.py 全流程整合脚本开发；期末报告、PPT与项目打包", "30%"],
       ["", "", "数据预处理模块 cleaning/preprocess.py：字段归一、会员/车型枚举归一、时长补算、异常过滤、抽样与派生特征", "18%"],
       ["", "", "统计分析：完整分析代码.ipynb，描述统计、热门站点、时段规律挖掘，输出统计汇总表与业务建议", "17%"],
       ["", "", "机器学习模块 src/ml.py：KMeans站点聚类（肘部法+轮廓系数）、骑行时长与站点客流预测（五模型对比）及10张分析图", "20%"],
       ["", "", "可视化模块：可视化呈现代码.ipynb，12张图表（时段/星期分布、用户与车型占比、TOP10站点、起讫点地图等）", "15%"]],
      cap="表1 团队成员分工表")

# ================= 2 项目开发环境 =================
h1("2 项目开发环境")
body("开发工具：PyCharm、VS Code。")
body("开发语言：Python 3.13。")
body("主要开发库：pandas（数据处理）、numpy（数值计算）、scikit-learn（聚类与回归）、"
     "matplotlib（可视化）、openpyxl（表格读写）、folium（交互地图，可选）。")
body("使用的 Coding Agent 工具：Claude Code、字节 TRAE，用于接口规范初稿起草、模块代码生成"
     "与调试排错；架构设计、规范制定与结果校验由小组成员人工完成。")

# ================= 3 数据说明 =================
h1("3 数据说明")
body("数据来源：纽约 Citi Bike 官方公开数据（https://www.citibikenyc.com/system-data，"
     "实际服务器 s3.amazonaws.com/tripdata/）。本项目使用 2026 年 7 月（202607）官方月度"
     "数据集，该月为“大月份”，官方 zip 内含 5 个 CSV 分片，合计约 974MB、499 万条行程记录，"
     "样本时间跨度为 2026-06-30 ~ 2026-07-31。")
body("样本个数：原始行程 499 万条，经清洗（剔除时长小于60秒的假启动与超过24小时的异常记录）"
     "后有效 497.6 万条（剔除率仅 0.3%），按固定随机种子 random_state=42 抽样 20 万条用于"
     "分析与建模，保证结果可复现。")
body("特征种类和数目：原始数据 13 个字段（ride_id、rideable_type、started_at、ended_at、"
     "起讫站名/ID、起讫经纬度、member_casual 等）；清洗后统一标准表共 16 列，见表2。")
table(["列名", "类型", "说明"],
      [["ride_duration", "float64", "骑行时长（秒），60s~24h"],
       ["start_time / end_time", "datetime", "起讫时间"],
       ["start_station / end_station", "str", "起讫站点名"],
       ["start_lat / start_lng / end_lat / end_lng", "float64", "起讫经纬度"],
       ["user_type", "str", "Subscriber（会员）/ Customer（单次）"],
       ["bikeid / rideable_type", "str", "行程ID；classic / electric 车型"],
       ["start_date / hour / weekday / is_weekend", "派生", "日期、小时(0-23)、星期(0-6)、是否周末"]],
      cap="表2 清洗后标准表特征（16列）")

# ================= 4 需求分析 =================
h1("4 需求分析")
body("按照选题4要求，系统需实现对纽约公共自行车官方数据的“数据清洗、统计分析、可视化图表"
     "呈现，并进一步运用数据挖掘相关算法（聚类算法、预测算法等）对数据进行挖掘分析和可视化”。"
     "据此将系统划分为五个功能模块与数据层、输出层，功能模块与业务流程如图1所示。")
fig(os.path.join(FIG, "flow_diagram.png"), "图1 系统功能模块与业务流程图", 5.6)
body("操作方式：一键运行 python main.py 即依次执行①数据获取→②数据预处理→③统计分析→"
     "④可视化→⑤机器学习；各模块也可独立运行（如 python download_data.py --month 202508 "
     "下载指定月份）。")

# ================= 5 系统设计和实现 =================
h1("5 系统设计和实现")
h2("5.1 数据获取")
body("download_data.py 按优先级获取数据：①本机已下载的官方 zip（避免重复下载900MB+）；"
     "②S3 服务器三个候选 URL 依次尝试。对大月份 zip 内的 5 个分片自动解压、合并为单一 CSV。")
code("def candidate_urls(period):\n"
     "    return [f'{BASE_URL}{period}-citibike-tripdata.csv.zip',\n"
     "            f'{BASE_URL}{period}-citibike-tripdata.zip',\n"
     "            f'{BASE_URL}{period}-citibike-tripdata.csv']")
h2("5.2 数据处理过程（预处理）")
body("预处理流程：①字段归一，通过 config.RAW_ALIASES 将 2026 新旧两种表头映射为 16 个标准"
     "列名；②时间解析，started_at/ended_at 转 datetime64；③时长补算——2026 新格式无 "
     "tripduration 字段，需自行计算：")
code("df['ride_duration'] = (df['end_time'] - df['start_time']).dt.total_seconds()")
body("④异常过滤，仅保留 60 秒 ≤ 时长 ≤ 24 小时且起讫站、经纬度有效的记录；⑤抽样 20 万条"
     "（random_state=42）；⑥派生 hour/weekday/is_weekend 特征。对 929MB 大文件采用 50 万行"
     "分块读取，内存占用稳定。")
code("df = df[(df['ride_duration'] >= 60) & (df['ride_duration'] <= 24*3600)]")
h2("5.3 数据挖掘算法介绍")
body("（1）KMeans 站点聚类：以 2295 个站点为样本，构造流量、平均时长、会员占比、经纬度等特征，"
     "标准化后聚类，采用肘部法与轮廓系数确定最佳聚类数，将站点划分为高流量中转型、低流量"
     "休闲型、通勤型、长时骑行型四类。")
code("X = (X - X.mean()) / X.std()\n"
     "km = KMeans(n_clusters=4, random_state=42, n_init=10)\n"
     "labels = km.fit_predict(X)\n"
     "sil = silhouette_score(X, labels)")
body("（2）骑行时长与站点客流预测：以 hour、is_weekend、is_member、同站往返等特征预测骑行"
     "时长；以站点热度、是否高峰时段等特征预测站点×小时出发客流，对比线性回归、岭回归、"
     "决策树、随机森林、梯度提升五种模型，用 R²、MAE、RMSE、MAPE 评估。")
h2("5.4 可视化")
body("matplotlib 绘制时段分布、星期分布、周末占比、热门站点TOP10、站点流量空间分布等图；"
     "folium 绘制交互式站点地图；全部图表保存至 output/figures/，中文统一使用 config 中"
     "配置的 SimHei 字体避免乱码。")

# ================= 6 结果分析 =================
h1("6 结果分析")
h2("6.1 描述性统计")
body("20 万条真实样本中：平均骑行时长 13.2 分钟，中位数 9.5 分钟，说明 Citi Bike 以短途"
     "“最后一公里”出行为主；会员（Subscriber）占 79.7%，游客（Customer）占 20.3%，系统已形成"
     "稳定的通勤用户基本盘；车型以 electric_bike 为主（73.5%）。")
h2("6.2 时空规律")
body("时段分布如图2，呈明显“早晚双峰”：早高峰 8 时、晚高峰 17-19 时，符合通勤出行特征；"
     "工作日骑行量约为周末的 2.6 倍（图3）。")
fig(os.path.join(FIG, "hour_distribution.png"), "图2 各时段骑行量分布（早晚双峰）")
fig(os.path.join(FIG, "weekday_distribution.png"), "图3 一周各日骑行量（橙=周末）")
body("热门起讫站 TOP10 见图4，Pier 61 at Chelsea Piers、W 21 St & 6 Ave、Cooper Square & "
     "Astor Pl 位居前列，热点高度集中于曼哈顿中城/下城，应作为车辆调度核心节点。站点流量"
     "空间分布见图5。")
fig(os.path.join(FIG, "hot_stations.png"), "图4 热门起讫点站点 TOP10")
fig(os.path.join(FIG, "station_scatter.png"), "图5 站点骑行量空间分布")
h2("6.3 站点聚类结果")
body("肘部法与轮廓系数确定 K=4（图6），聚类空间分布见图7。长时骑行型站点平均时长 22.1 分钟、"
     "会员占比仅 52.0%，明显区别于其他三类（会员占比约 80%），对应旅游休闲区域，聚类结果"
     "可为差异化运营提供依据。")
fig(os.path.join(MLF, "ml_fig1_kmeans_elbow_method.png"), "图6 肘部法选择最佳聚类数")
fig(os.path.join(MLF, "ml_fig2_kmeans_spatial_distribution.png"), "图7 KMeans站点聚类空间分布")
h2("6.4 预测模型性能评估")
body("五模型对比结果如表3所示。客流预测任务中随机森林最优：R²=0.937、MAE=31.98、"
     "MAPE=25.6%，说明站点客流具有较强可预测性，可直接辅助车辆调度决策；时长预测任务各模型"
     "R² 均低于 0.23，因骑行距离、天气等关键特征未纳入，属合理结果，亦指出后续改进方向。")
table(["任务", "模型", "R²", "MAE", "RMSE", "MAPE(%)"],
      [["时长预测(分钟)", "线性回归", "0.201", "5.03", "15.21", "51.1"],
       ["时长预测(分钟)", "随机森林（最优）", "0.223", "4.71", "15.00", "48.6"],
       ["客流预测(次/小时)", "线性回归", "0.864", "52.64", "70.06", "77.6"],
       ["客流预测(次/小时)", "随机森林（最优）", "0.937", "31.98", "47.85", "25.6"]],
      cap="表3 预测模型性能对比（成员4五模型对比结果）")
fig(os.path.join(MLF, "ml_fig9_demand_prediction_timeseries.png"), "图8 客流预测时序对比")
fig(os.path.join(M5F, "start_point_map.png"), "图9 起点站地理分布地图")

# ================= 7 AI辅助过程 =================
h1("7 AI辅助过程")
body("提示词（Prompt）示例：“请按 docs/data_dict.md 的接口契约生成 storage/preprocess.py："
     "输入 data/raw 合并CSV，输出16列标准表，60s~24h过滤，抽样20万条固定种子42，"
     "大文件需分块读取”。")
body("AI 生成初始内容：config.py 列名规范与 data_dict.md 接口文档初稿、四个模块的初始代码、"
     "期末报告初稿。")
body("关键迭代修改过程：①AI 初版预处理一次性 read_csv 导致 929MB 文件内存吃紧，人工要求改为"
     "chunksize=500000 分块读取；②Windows 控制台 GBK 编码中文乱码，人工增加 utf-8 输出包装；"
     "③可视化模块与 main.py 的接口参数类型不一致导致 AttributeError，人工统一为 value_counts "
     "序列；④成员模块各自写死路径（raw/、cleaned/），人工统一收敛到 config 常量。")
body("人工修改与优化说明：架构与分工设计、清洗阈值确认（60s/24h 与官方口径一致）、结果合理性"
     "核验（剔除率0.3%、会员占比79.7%与官方报告核对）、图表中文显示、报告撰写与数据引用核对"
     "均为人工完成。")
body("最终成果与 AI 生成内容的差异：AI 生成代码约占初始代码量的 60%，但全部经过人工运行验证；"
     "接口契约、路径规范、异常兜底与结果核验等关键环节均由人工主导，体现“AI 初稿+人工优化”"
     "的完整过程。")

# ================= 8 总结 =================
h1("8 总结")
body("本项目打通了“数据获取→清洗→统计→可视化→挖掘”完整闭环，在 499 万行真实数据上验证了"
     "统一架构约定的有效性：五名成员的模块基于同一列名规范与接口契约，实现了零冲突整合。")
body("创新点：①“本机 zip 优先、多候选 URL 兜底”的数据获取策略，自动合并官方大月份多分片；"
     "②对 929MB 数据的内存友好分块清洗流水线；③五模型对比的客流预测，随机森林 R² 达 0.937，"
     "可直接用于调度支持。")
body("可改进的地方：①时长预测可引入骑行距离（经纬度直线距离）、天气、节假日特征，有望显著"
     "提升 R²；②聚类可扩展为时空图模型（如 ST-GCN）刻画站点间依赖；③可接入 folium 交互"
     "大屏与调度仿真回放，把预测结果写回调度指令形成决策闭环。")

for out in (OUT1, OUT2):
    try:
        doc.save(out)
        print("saved:", out)
    except PermissionError:
        alt = out.replace(".docx", "-new.docx")
        doc.save(alt)
        print("原文件被占用，已另存为:", alt)


