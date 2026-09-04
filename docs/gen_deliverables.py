# -*- coding: utf-8 -*-
"""生成期末报告 docx 与答辩 PPT。运行：python docs/gen_deliverables.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
import config

FIG = config.FIG_DIR
MLF = os.path.join(FIG, "ml")
M5F = os.path.join(FIG, "member5")
DOCX_OUT = os.path.join(config.BASE_DIR, "docs", "期末报告-纽约公共自行车数据分析.docx")
PPTX_OUT = os.path.join(config.BASE_DIR, "docs", "答辩PPT-纽约公共自行车数据分析.pptx")

doc = Document()
style = doc.styles["Normal"]
style.font.name = "Times New Roman"
style.font.size = Pt(12)
style._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

def _cn(run, size=12, bold=False):
    run.font.name = "Times New Roman"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    run.font.size = Pt(size)
    run.bold = bold
    return run

def title(t, size=16):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _cn(p.add_run(t), size, True)

def h(t):
    p = doc.add_paragraph(); _cn(p.add_run(t), 14, True)

def body(t):
    p = doc.add_paragraph(); p.paragraph_format.first_line_indent = Pt(24)
    _cn(p.add_run(t), 12)

def code(t):
    p = doc.add_paragraph(); _cn(p.add_run(t), 10.5)

def fig(path, caption, width=5.2):
    if not os.path.exists(path):
        print("missing fig:", path); return
    doc.add_picture(path, width=Inches(width))
    doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    _cn(p.add_run(caption), 10.5)

# ---- 封面 ----
for _ in range(4): doc.add_paragraph()
title("《软件开发实践1》期末报告", 22)
doc.add_paragraph()
title("纽约公共自行车（Citi Bike）数据分析与可视化", 18)
for _ in range(3): doc.add_paragraph()
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
_cn(p.add_run("班级：01　小组：02\n\n完成时间：2026年9月"), 14)
doc.add_page_break()

# ---- 1 团队成员成绩和分工 ----
h("1 团队成员成绩和分工")
body("组长（第1位）：整体架构设计；CSV 列名规范与目录结构约定（config.py、docs/data_dict.md）；"
     "接口文档编写；download_data.py 数据获取脚本与 main.py 全流程整合脚本开发；期末报告、PPT 与项目打包。")
body("成员2：数据预处理模块 cleaning/preprocess.py —— 字段归一、会员/车型枚举归一、时长补算、"
     "异常过滤（60s~24h）、抽样20万条与派生特征，输出统一标准表。")
body("成员3：统计分析与时空规律挖掘 —— 完整分析代码.ipynb，输出描述统计、热门站点、时段/工作日规律、"
     "统计结果汇总表与分析结论与业务建议。")
body("成员4：机器学习模块 src/ml.py —— KMeans 站点聚类（肘部法+轮廓系数选K）、骑行时长预测与站点客流预测"
     "（线性回归/岭回归/决策树/随机森林/梯度提升五模型对比），10 张分析图。")
body("成员5：可视化模块 可视化呈现代码.ipynb —— 12 张图表：时段/星期分布、用户与车型占比、"
     "TOP10 站点、骑行时长分布、起讫点地图等。")

# ---- 2 项目背景介绍 ----
h("2 项目背景介绍")
body("共享单车已成为城市“最后一公里”出行的关键方式。纽约 Citi Bike 官方公开月度行程级数据，"
     "本课题（选题4）基于其 2026 年 6-7 月真实数据开展清洗、统计分析、数据挖掘与可视化，"
     "刻画纽约市民骑行出行模式，并进一步通过聚类与预测模型为车辆调度提供数据支持。")
body("数据来源：https://www.citibikenyc.com/system-data（S3：s3.amazonaws.com/tripdata/）。"
     "202607 为大月份，官方 zip 内含 5 个 CSV 分片共约 974MB、499 万条行程。")

# ---- 3 设计说明 ----
h("3 设计说明")
body("开发工具：PyCharm / VS Code；Python 3.13；主要依赖：pandas、numpy、scikit-learn、matplotlib、"
     "openpyxl（可选 folium 交互地图）。")
body("使用的 Coding Agent 工具：Claude Code / TRAE，用于代码生成、接口规范起草与调试排错；"
     "架构设计、规范制定与结果校验由小组人工完成。")
body("架构约定：config.py 集中管理路径、CSV 列名规范（RAW_ALIASES/CANONICAL_SCHEMA）、清洗参数与字体；"
     "docs/data_dict.md 为成员间接口契约。目录：cleaning/（预处理）、analysis/（统计）、model/（挖掘）、"
     "visualization/（可视化）、data/（原始与清洗数据）、output/（结果图表）。")

# ---- 4 功能说明 ----
h("4 功能说明")
body("一键运行 python main.py 依次完成：①数据获取（download_data.py，本机 zip 优先、S3 兜底，自动合并分片）→ "
     "②数据预处理（字段归一/时长补算/异常过滤/抽样）→ ③统计分析（描述统计+时空规律）→ "
     "④可视化（6 类图表+可选地图）→ ⑤机器学习（站点聚类+时长/客流预测）。")

# ---- 5 系统设计与实现 ----
h("5 系统设计与实现")
body("数据处理流程：原始 499 万行 → 字段归一（ride_id→bikeid 等 16 列）→ 时间解析与时长补算 → "
     "异常过滤（有效 497.6 万行，剔除率仅 0.3%）→ 固定随机种子抽样 20 万条 → 派生 hour/weekday/is_weekend 特征。")
body("数据挖掘算法：① KMeans 站点聚类（特征：流量、平均时长、会员占比、经纬度，标准化后聚类）；"
     "② 骑行时长预测与站点×小时客流预测，对比线性回归、岭回归、决策树、随机森林、梯度提升五种模型。")
body("关键代码（预处理-时长补算与异常过滤）：")
code("df['ride_duration'] = (df['end_time']-df['start_time']).dt.total_seconds()\n"
     "df = df[(df['ride_duration']>=60)&(df['ride_duration']<=24*3600)]")
body("关键代码（KMeans 聚类）：")
code("X = (X-X.mean())/X.std(); km = KMeans(n_clusters=4, random_state=42, n_init=10)\n"
     "labels = km.fit_predict(X); sil = silhouette_score(X, labels)")

# ---- 6 运行结果 ----
h("6 运行结果及详细性能")
body("描述统计：20 万条样本中平均骑行 13.2 分钟（中位 9.5 分钟）；会员占 79.7%；"
     "车型以 electric_bike 为主（73.5%）；早高峰 8 时、晚高峰 17-19 时呈明显双峰，工作日约为周末 2.6 倍；"
     "热门站点集中在曼哈顿中城/下城（Pier 61 at Chelsea Piers、W 21 St & 6 Ave 等）。")
fig(os.path.join(FIG, "hour_distribution.png"), "图1 各时段骑行量分布（早晚双峰）")
fig(os.path.join(FIG, "weekday_distribution.png"), "图2 一周各日骑行量")
fig(os.path.join(FIG, "hot_stations.png"), "图3 热门起讫点站点 TOP10")
fig(os.path.join(FIG, "station_scatter.png"), "图4 站点流量空间分布")
body("站点聚类：K=4，轮廓系数 0.278。高流量中转型站点（平均 258 次）与低流量休闲型差异显著；"
     "长时骑行型站点会员占比明显偏低（52.0%），符合旅游休闲区特征。")
body("预测性能：本项目基线线性回归客流预测 R²=0.571（MAE=2.98 次/站·小时）；"
     "成员4 扩展五模型对比中，随机森林客流预测 R²=0.937、MAE=31.98 次/小时（MAPE 25.6%），"
     "为最优模型；时长预测最优为随机森林 R²=0.223、MAE=4.71 分钟（时长受骑行距离等未纳入特征影响，"
     "符合预期）。")
fig(os.path.join(MLF, "ml_fig2_kmeans_spatial_distribution.png"), "图5 KMeans 站点聚类空间分布")
fig(os.path.join(MLF, "ml_fig1_kmeans_elbow_method.png"), "图6 肘部法选择最佳聚类数")
fig(os.path.join(MLF, "ml_fig9_demand_prediction_timeseries.png"), "图7 客流预测时序对比")
fig(os.path.join(M5F, "start_point_map.png"), "图8 成员5：起点站地图可视化")

# ---- 7 AI辅助使用 ----
h("7 AI 辅助记录")
body("本项目中 AI Coding Agent 主要用于：①根据提示词生成 config.py 列名规范与 data_dict.md 接口文档初稿；"
     "②生成预处理/统计/建模模块的初始代码；③调试报错（Windows GBK 编码、大文件分块读取等）。"
     "人工完成：架构与分工设计、清洗规则阈值确认、结果合理性核验（如剔除率 0.3%、会员占比 79.7% 与官方口径核对）、"
     "图表中文显示优化与报告撰写修改。AI 生成内容均经过人工运行验证与修改，体现了“AI 初稿+人工优化”的完整过程。")

# ---- 8 总结 ----
h("8 总结")
body("本项目打通了“获取→清洗→统计→可视化→挖掘”完整闭环，在 499 万行真实数据上验证了架构约定的有效性："
     "统一列名规范使 5 名成员模块零冲突对接。创新点：①本机 zip 优先的分片自动合并下载策略；"
     "②五模型对比的客流预测，随机森林 R² 达 0.937。可改进方向：引入骑行距离、天气、节假日特征提升时长预测；"
     "使用 ST-GCN 等时空图模型；接入 folium 交互地图与调度仿真。")

doc.save(DOCX_OUT)
print("saved:", DOCX_OUT)

# ============================ 答辩 PPT ============================
from pptx import Presentation
from pptx.util import Inches as PInches

prs = Presentation()

def slide(t, lines, img=None):
    s = prs.slides.add_slide(prs.slide_layouts[1])
    s.shapes.title.text = t
    tf = s.placeholders[1].text_frame
    tf.text = lines[0]
    for ln in lines[1:]:
        tf.add_paragraph().text = ln
    if img and os.path.exists(img):
        s.shapes.add_picture(img, PInches(5.2), PInches(1.6), height=PInches(5.2))
    return s

s0 = prs.slides.add_slide(prs.slide_layouts[0])
s0.shapes.title.text = "纽约公共自行车（Citi Bike）数据分析与可视化"
s0.placeholders[1].text = "《软件开发实践1》　班级01·小组02　2026年9月"

slide("项目背景与数据", [
    "选题4：纽约 Citi Bike 公开骑行数据分析",
    "官方数据：2026 年 6-7 月，974MB / 499 万条行程",
    "目标：清洗→统计→可视化→聚类与预测",
    "数据源：citibikenyc.com/system-data"],
    os.path.join(M5F, "start_point_map.png"))
slide("团队分工", [
    "组长：架构/列名规范/接口文档/download_data.py/main.py/报告PPT打包",
    "成员2：数据预处理 cleaning/preprocess.py",
    "成员3：统计分析（ipynb）与业务建议",
    "成员4：机器学习 src/ml.py（聚类+五模型预测）",
    "成员5：可视化 12 图（ipynb）"])
slide("系统架构与规范", [
    "config.py：路径/CSV列名规范/清洗参数 单点维护",
    "docs/data_dict.md：成员间接口契约",
    "main.py 一键全流程：下载→清洗→统计→画图→建模",
    "清洗：字段归一/时长补算/60s~24h过滤/抽样20万(可复现)"])
slide("统计分析结果", [
    "平均骑行 13.2 分钟，中位 9.5 分钟（短途通勤为主）",
    "会员占 79.7%，electric_bike 占 73.5%",
    "早高峰 8 时 / 晚高峰 17-19 时，双峰形态",
    "工作日约为周末 2.6 倍；热点集中于曼哈顿中城/下城"],
    os.path.join(FIG, "hour_distribution.png"))
slide("数据挖掘：站点聚类（KMeans）", [
    "K=4（肘部法+轮廓系数 0.278）",
    "高流量中转型 / 低流量休闲型 / 通勤型 / 长时骑行型",
    "长时骑行型站点会员占比仅 52%（旅游休闲区特征）",
    "2295 个站点全部完成聚类打标"],
    os.path.join(MLF, "ml_fig2_kmeans_spatial_distribution.png"))
slide("数据挖掘：预测模型对比", [
    "时长预测最优：随机森林 R²=0.223 / MAE=4.71min",
    "客流预测最优：随机森林 R²=0.937 / MAPE 25.6%",
    "5 模型对比：线性/岭回归/决策树/随机森林/梯度提升",
    "结论：站点客流可预测性强，可用于辅助调度"],
    os.path.join(MLF, "ml_fig9_demand_prediction_timeseries.png"))
slide("可视化成果", [
    "12 张业务图表 + 10 张机器学习分析图",
    "时段/星期/占比/TOP10 站点/时长分布/站点地图"],
    os.path.join(M5F, "top10_start_station.png"))
slide("AI 辅助与总结", [
    "AI 用于：规范初稿、模块代码生成、调试排错",
    "人工：架构设计、阈值确认、结果核验、报告修改",
    "创新：分片自动合并下载；五模型对比预测",
    "改进：引入距离/天气特征；ST-GCN 时空模型"])
prs.save(PPTX_OUT)
print("saved:", PPTX_OUT)

