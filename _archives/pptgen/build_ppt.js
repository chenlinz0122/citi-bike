// build_ppt.js —— 重做《纽约公共自行车数据分析》答辩 PPT（正式工作汇报风格）
// 设计系统：严谨 / 有序 / 克制；深蓝主色 + 琥珀点缀 + 暖白背景
const PptxGenJS = require("pptxgenjs");
const path = require("path");

const FIG = "E:/citi-bike/output/figures";
const OUT = path.join(__dirname, "答辩PPT-纽约公共自行车数据分析_v2.pptx");

const pptx = new PptxGenJS();
pptx.defineLayout({ name: "WIDE", width: 13.33, height: 7.5 });
pptx.layout = "WIDE";
pptx.author = "周晨琳 陈嘉欣 张子千 童悦家 陈静萤";
pptx.title = "纽约公共自行车数据分析";

// 按真实幻灯片序号编号（封面/结束页不计入页码时也能对齐）
let slideIndex = 0;
const _addSlide = pptx.addSlide.bind(pptx);
pptx.addSlide = function () {
  slideIndex++;
  const s = _addSlide();
  if (NOTES[slideIndex]) s.addNotes(NOTES[slideIndex]);
  return s;
};

// ================= 设计令牌 =================
const T = {
  bg: "FAFAF7",        // 暖白背景
  surface: "FFFFFF",
  ink: "1F2328",       // 近黑文字
  muted: "5B6570",     // 次要文字
  faint: "8A939E",
  accent: "1F4E79",    // 深蓝主色
  accentSoft: "E8EEF5",
  gold: "C8842C",      // 琥珀点缀
  green: "2E7D32",
  amber: "B7791F",
  red: "C0392B",
  line: "D9DEE3",
  white: "FFFFFF",
};
const FONT = "Microsoft YaHei";
const M = 0.62;            // 左右边距
const CW = 13.33 - M * 2;  // 内容宽 12.09
const PAGE_TOTAL = 17;

// ================= 短 Token 保护（防自动换行）=================
function token(slide, text, o) {
  slide.addText(text, {
    x: o.x, y: o.y, w: o.w, h: o.h,
    fontFace: o.fontFace || FONT,
    fontSize: o.fontSize || 11,
    bold: o.bold !== undefined ? o.bold : true,
    color: o.color || T.ink,
    align: o.align || "center",
    valign: "middle",
    margin: 0,
    wrap: false,
    fit: "shrink",
  });
}

// ================= 通用构件 =================
function pageHeader(slide, section, title, opts = {}) {
  slide.background = { color: T.bg };
  slide.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.33, h: 0.10, fill: { color: T.accent } });
  if (section) {
    slide.addShape(pptx.ShapeType.rect, { x: M, y: 0.345, w: 0.14, h: 0.14, fill: { color: T.gold } });
    slide.addText(section, {
      x: M + 0.26, y: 0.30, w: 6, h: 0.24,
      fontFace: FONT, fontSize: 9, bold: true, color: T.accent, margin: 0, charSpacing: 1.5,
    });
  }
  slide.addText(title, {
    x: M, y: 0.52, w: 11, h: 0.50,
    fontFace: FONT, fontSize: 22, bold: true, color: T.ink, margin: 0,
  });
  slide.addShape(pptx.ShapeType.rect, { x: M, y: 1.045, w: 0.55, h: 0.035, fill: { color: T.gold } });
  slide.addShape(pptx.ShapeType.line, {
    x: M, y: 1.10, w: CW, h: 0, line: { color: T.line, width: 1 },
  });
  // 页脚
  slide.addShape(pptx.ShapeType.line, {
    x: M, y: 7.10, w: CW, h: 0, line: { color: T.line, width: 1 },
  });
  slide.addText("纽约公共自行车数据分析 · Citi Bike", {
    x: M, y: 7.16, w: 5, h: 0.24,
    fontFace: FONT, fontSize: 8, color: T.faint, margin: 0,
  });
  if (opts.page !== false) {
    token(slide, `${slideIndex} / ${PAGE_TOTAL}`, {
      x: 12.30, y: 7.16, w: 0.85, h: 0.24, fontSize: 8, color: T.faint, align: "right",
    });
  }
}

function conclusion(slide, text, y = 6.72, h = 0.32) {
  slide.addShape(pptx.ShapeType.rect, { x: M, y, w: CW, h, fill: { color: T.accentSoft } });
  slide.addShape(pptx.ShapeType.rect, { x: M, y, w: 0.07, h, fill: { color: T.gold } });
  slide.addText(text, {
    x: M + 0.16, y, w: CW - 0.28, h,
    fontFace: FONT, fontSize: 10.5, bold: true, color: T.accent, valign: "middle", margin: 0,
  });
}

function kpi(slide, x, y, w, num, label, accent = T.accent) {
  slide.addShape(pptx.ShapeType.rect, { x, y, w, h: 1.30, fill: { color: T.surface }, line: { color: T.line, width: 0.75 }, shadow: { type: "outer", color: "D8DEE5", blur: 4, offset: 1.5, angle: 90, opacity: 0.35 } });
  slide.addShape(pptx.ShapeType.rect, { x, y, w: 0.05, h: 1.30, fill: { color: accent } });
  slide.addShape(pptx.ShapeType.rect, { x: x + 0.16, y: y + 1.13, w: w - 0.32, h: 0.05, fill: { color: accent } });
  token(slide, num, { x: x + 0.15, y: y + 0.14, w: w - 0.3, h: 0.62, fontSize: 25, color: accent, align: "left" });
  slide.addText(label, {
    x: x + 0.15, y: y + 0.82, w: w - 0.3, h: 0.34,
    fontFace: FONT, fontSize: 10.5, color: T.muted, margin: 0,
  });
}

function img(slide, file, x, y, w, h) {
  slide.addShape(pptx.ShapeType.rect, {
    x: x - 0.015, y: y - 0.015, w: w + 0.03, h: h + 0.03,
    fill: { color: T.white },
    line: { color: T.line, width: 0.75 },
    shadow: { type: "outer", color: "D8DEE5", blur: 5, offset: 1.6, angle: 90, opacity: 0.28 },
  });
  slide.addImage({ path: path.join(FIG, file), x, y, w, h });
}

function imgCap(slide, x, y, w, text) {
  slide.addText(text, {
    x, y, w, h: 0.24,
    fontFace: FONT, fontSize: 8.5, color: T.faint, align: "center", margin: 0,
  });
}

// 标准表格
function dataTable(slide, x, y, w, rows, opts = {}) {
  const colW = opts.colW || [];
  const head = rows[0];
  const body = rows.slice(1);
  const headers = head.map((h, i) => ({
    text: h, options: {
      bold: true, color: T.white, fill: { color: T.accent },
      fontFace: FONT, fontSize: opts.headSize || 9.5, align: opts.align || "center", valign: "middle",
    },
  }));
  const cells = body.map(r => r.map((c, i) => ({
    text: c, options: {
      fontFace: FONT, fontSize: opts.bodySize || 9,
      color: T.ink, align: opts.align || "center", valign: "middle",
      fill: { color: i % 2 === 0 ? T.surface : "F3F5F7" },
    },
  })));
  const allRows = [headers, ...cells];
  slide.addTable(allRows, {
    x, y, w, colW: colW.length ? colW : undefined,
    border: { type: "solid", color: T.line, pt: 0.5 },
    rowH: opts.rowH || 0.28,
    margin: 0.03, valign: "middle",
  });
}

// ============================================================
// 演讲者备注（讲稿，逐页对应）
// ============================================================
const NOTES = {
  1: `【开场 · 站定环视评委】
各位老师好！我们小组的答辩题目是《纽约公共自行车数据分析》。
本项目基于纽约 Citi Bike 官方公开数据，完成了从数据获取、清洗、统计分析、可视化到机器学习挖掘的完整闭环。
我是周晨琳，接下来由我代表小组进行汇报。
【翻页】`,

  2: `本次汇报共分五个部分：首先是团队分工与项目背景，然后是数据说明与系统设计，
第三部分是统计分析与可视化成果，第四部分是机器学习挖掘，包括站点聚类和双任务预测，
最后是 AI 辅助过程、创新点与总结展望。`,

  3: `【约 40 秒】
我们小组共五名成员。我负责整体架构设计、列名规范与全流程整合；张子千负责数据预处理，包括字段归一、异常过滤和特征工程；陈嘉欣负责统计分析；童悦家负责机器学习部分，包括 KMeans 聚类和两个预测任务；陈静萤负责可视化图表。
这里我想强调一点：我们的开发模式是"统一契约、并行开发"。先制定好 config 里的列名规范和接口契约，五个人的模块只依赖统一的标准表，最终实现了零冲突整合，每个人的工作量均分 20%。
【被问要点】你们是怎么保证并行开发不冲突的？→ 统一标准表 + 接口契约，各模块读写同一列名规范，最终由 main.py 串联。`,

  4: `【约 30 秒】
Citi Bike 是纽约市最大的公共自行车系统，日均骑行超过十万次。海量骑行数据里蕴含着城市出行规律和用户行为特征，通过分析可以辅助车辆调度、提升运营效率，这也正是课程要求的"数据清洗、统计分析、可视化、数据挖掘"四个环节。
系统按五个模块划分：数据获取、预处理、统计分析、可视化、机器学习，对应五个脚本文件。开发环境是 Python 3.10，使用 pandas、scikit-learn、matplotlib 和 folium，开发工具是 PyCharm 和 TRAE 编码智能体。
【被问要点】Python 版本是多少？→ Python 3.10（与代码环境一致）。`,

  5: `【约 40 秒】
先看数据规模。我们使用的是 2026 年 7 月的官方数据，大月份分成了 5 个 CSV 分片，压缩包约 929 兆。合并后原始记录 499 万条，清洗后有效 497.5 万条，异常剔除率只有 0.36%。考虑到计算成本，我们按固定随机种子抽样了 20 万条作为分析样本。
预处理流水线共六步：字段归一、时间解析、时长补算、异常过滤、随机抽样、特征派生。其中异常过滤采用官方口径——只剔除时长小于 60 秒的行程。
这里有一个技术亮点：929 兆的大文件我们采用分块读取的方式，内存占用稳定，普通笔记本就能跑完，这一点在创新点部分还会提到。`,

  6: `【约 30 秒】
系统架构分四层：输入层是官方公开数据；数据获取脚本负责下载；预处理脚本生成统一的 16 列标准表，这张表是整个系统的"接口契约"；下游三个模块——统计分析、可视化、机器学习——并行读取这张表；最终汇总到输出层，包括统计报表、统计图表和聚类与预测模型结果。
整个流程可以通过 python main.py 一键运行，各模块也可以独立执行。`,

  7: `【约 30 秒】
统计结果很有代表性：平均骑行时长 13.2 分钟，中位数 9.5 分钟——说明大部分骑行是短途；用户结构上会员占 79.5%，车型上电动自行车占 73.4%。
从两张环图可以直观看到：这是一个以"最后一公里"通勤出行为主的系统，已经形成了稳定的会员基本盘，而且电动化趋势非常明显。
【被问要点】为什么中位数 9.5 小于均值 13.2？→ 时长呈右偏分布，少数超长骑行（如休闲骑行）把均值拉高了，中位数更能代表典型骑行时长。`,

  8: `【约 40 秒】
时空规律这张图非常直观：时段分布呈明显的"早晚双峰"——早高峰 8 时，晚高峰 17 到 19 时，峰值出现在 18 时，单小时 17403 次；星期分布显示工作日骑行量是周末的 3.1 倍，周三最高。
热门站点方面，借车量第一的是 Pier 61 at Chelsea Piers，占 0.38%，TOP5 站点都集中在曼哈顿中城。
结论很清晰：Citi Bike 有显著的通勤特征——早晚高峰潮汐、工作日主导、核心区集中，这为车辆调度优化提供了直接依据。`,

  9: `【约 30 秒 · 可略讲】
可视化部分我们产出了五类图表：时段与星期分布柱状图、用户与车型占比饼图、TOP10 热门站点柱状图、站点空间分布散点图，以及基于 folium 的交互式地图。交互地图是 HTML 形式，支持缩放和站点信息查看，大家可以会后体验。
所有图表保存到 output/figures/ 目录，中文统一使用 SimHei 字体。`,

  10: `【重点页 · 约 60 秒】
机器学习部分，第一个任务是站点聚类。我们对 1985 个有效站点、10 维特征做 Z-score 标准化后使用 KMeans 聚类，特征涵盖流量、时长、会员占比、高峰特征、周末占比、站点平衡度和经纬度。通过四项指标综合确定 K=4：SSE 13754.9、轮廓系数 0.1630、CH 指数 292.61、DB 指数 1.8809。
从空间分布图可以看到，聚类结果与城市地理高度吻合。四类站点分别是：高流量通勤型 694 站，日均 374.6 次、会员占比 81.1%；中流量通勤型 443 站；低流量通勤型 571 站；还有一类低流量休闲型 277 站，它的特点是平均时长最长——17.8 分钟，会员占比最低——65.3%，明显是景区休闲骑行的特征。
这个结果的业务价值在于：不同类型站点要差异化运营，比如休闲站适合做周末营销，通勤站要重点保障高峰时段的车辆供给。`,

  11: `【约 30 秒 · 可略讲】
这一页展示 K 值是如何确定的。左上是肘部法则，K 从 2 到 10 的 SSE 曲线，下降趋缓的拐点落在 4；再结合轮廓系数、CH 指数和 DB 指数的交叉验证，综合确定 K=4，而不是拍脑袋选的。
右上雷达图直观呈现四类站点画像差异：休闲型站点时长最长、周末占比最高达 33.6%，而三类通勤型站点会员占比普遍超过 79%。两类站点运营策略应该显著区分。
【被问要点】为什么选 K=4？→ 肘部拐点 + 轮廓/CH/DB 三指标交叉验证。`,

  12: `【重点页 · 约 60 秒】
第二个任务是双任务预测，每个任务都用五个模型对比，并加了均值基线作为参照。
左侧是骑行时长预测，17 维特征，包含骑行距离。随机森林最优：R² 0.2031，MAE 4.80 分钟，相比均值基线的 8.31 分钟有明显提升。
右侧是站点客流预测，13 维特征，包含滞后客流特征。梯度提升最优：R² 0.9465，MAE 29.37 次每小时，比均值基线的 155 次提高了 81% 的精度。
两个任务一个"难"一个"易"：时长预测受个人骑行习惯影响大，R² 偏低是正常的；客流预测因为利用了时序滞后特征，效果非常好，可以直接支撑车辆投放调度。`,

  13: `【约 40 秒】
这一页是预测效果的细看。左上是时长预测的真实值—预测值散点与残差分布，右上是客流预测在测试集上的时序对比，可以看到预测曲线与真实曲线贴合度很高。
关键结论看最右侧：客流预测中，滞后一小时的客流特征贡献了 79.5%，说明站点客流有很强的自相关性，这也是预测准的原因；时长预测中，骑行距离是第一特征，贡献 61.8%，距离越远耗时越长，符合直觉。
相对均值基线，客流 MAE 降低了 81.1%，时长 MAE 降低了 42.2%。我们还做了误差归因：客流误差主要集中在高流量时段，时长误差集中在超过 60 分钟的长时骑行上。
【被问要点】为什么客流预测 R² 这么高？→ lag_1h 滞后客流携带强自相关信息（贡献 79.5%）；为什么时长预测 R² 低？→ 时长受个人习惯、路况、信号灯等随机因素影响大，属正常现象，且相对基线仍有 42% 提升。`,

  14: `【约 30 秒】
本课程要求体现 AI 辅助开发。我们使用字节的 TRAE Coding Agent，AI 承担了接口规范初稿起草、模块代码生成和调试排错；但架构设计、规范制定和结果校验都由人工主导。
具体来说，AI 生成了 config 列名规范与接口文档初稿、四个模块的初始代码框架、报告初稿结构和图表模板。之后我们做了四轮关键迭代：把一次性 read_csv 改成 50 万分块读取解决内存问题；解决 Windows 控制台 GBK 乱码；统一了模块间参数类型不一致；把写死的路径统一收敛到 config 常量。
一句话总结：AI 生成框架，人工主导验证与优化。`,

  15: `【约 30 秒】
创新点归纳为四条：第一，智能数据获取策略，本机 zip 优先、三个候选 URL 兜底，自动合并大月份多分片，避免重复下载 900 多兆数据；第二，内存友好的清洗流水线，分块读取让普通笔记本也能跑大数据；第三，统一契约并行开发，体现软件工程最佳实践；第四，聚类加多模型对比预测，客流预测 R² 达到 0.9465，时长预测也明确了距离为核心特征。`,

  16: `【约 30 秒】
最后总结一下：我们打通了"数据获取—清洗—统计—可视化—挖掘"的完整闭环，在 499 万行真实数据上验证了统一架构约定的有效性，产出了统计图表、站点聚类和双任务多模型对比预测。其中客流预测可以直接辅助车辆投放调度，时长预测也找出了核心影响因素。
未来改进方向有四个：引入天气、节假日等特征进一步提升时长预测精度；把聚类扩展为 ST-GCN 等时空图模型，刻画站点间依赖；接入 folium 交互大屏与调度仿真；以及接入实时数据 API 实现流式分析。`,

  17: `【面向评委 · 从容收尾】
以上就是我们小组的全部汇报，感谢各位老师的聆听，我们小组愿意回答老师们的提问。`,
};

// ============================================================
// P1 封面（深蓝）
// ============================================================
{
  const s = pptx.addSlide();
  s.background = { color: T.accent };
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 7.10, w: 13.33, h: 0.40, fill: { color: T.gold } });
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.33, h: 0.12, fill: { color: "FFFFFF" } });
  s.addText("《软件开发实践1》期末答辩", { x: 0.9, y: 1.15, w: 6, h: 0.4, fontFace: FONT, fontSize: 14, color: "D7E3F0", margin: 0 });
  s.addText("纽约公共自行车数据分析", { x: 0.88, y: 2.35, w: 11.5, h: 1.0, fontFace: FONT, fontSize: 42, bold: true, color: T.white, margin: 0 });
  s.addText("Citi Bike Data Analysis & Mining", { x: 0.92, y: 3.42, w: 8, h: 0.42, fontFace: FONT, fontSize: 16, color: "AEC9E4", margin: 0 });
  s.addShape(pptx.ShapeType.line, { x: 0.95, y: 4.15, w: 2.2, h: 0, line: { color: T.gold, width: 2.5 } });
  s.addText("团队成员：周晨琳　陈嘉欣　张子千　童悦家　陈静萤", { x: 0.92, y: 4.85, w: 10, h: 0.4, fontFace: FONT, fontSize: 14, color: "E6EEF6", margin: 0 });
  s.addText("杭州电子科技大学　|　2026 年 9 月", { x: 0.92, y: 5.35, w: 8, h: 0.35, fontFace: FONT, fontSize: 12, color: "AEC9E4", margin: 0 });
  // 四角装饰（正式文件式角标）
  s.addShape(pptx.ShapeType.line, { x: 0.55, y: 0.55, w: 0.45, h: 0, line: { color: "7C9ABD", width: 1.25 } });
  s.addShape(pptx.ShapeType.line, { x: 0.55, y: 0.55, w: 0, h: 0.45, line: { color: "7C9ABD", width: 1.25 } });
  s.addShape(pptx.ShapeType.line, { x: 12.33, y: 0.55, w: 0.45, h: 0, line: { color: "7C9ABD", width: 1.25 } });
  s.addShape(pptx.ShapeType.line, { x: 12.78, y: 0.55, w: 0, h: 0.45, line: { color: "7C9ABD", width: 1.25 } });
  s.addShape(pptx.ShapeType.line, { x: 0.55, y: 6.55, w: 0.45, h: 0, line: { color: "7C9ABD", width: 1.25 } });
  s.addShape(pptx.ShapeType.line, { x: 0.55, y: 6.55, w: 0, h: 0.45, line: { color: "7C9ABD", width: 1.25 } });
  s.addShape(pptx.ShapeType.line, { x: 12.33, y: 6.55, w: 0.45, h: 0, line: { color: "7C9ABD", width: 1.25 } });
  s.addShape(pptx.ShapeType.line, { x: 12.78, y: 6.55, w: 0, h: 0.45, line: { color: "7C9ABD", width: 1.25 } });
}

// ============================================================
// P2 目录
// ============================================================
{
  const s = pptx.addSlide();
  pageHeader(s, "CONTENTS", "目录");
  const items = [
    ["01", "团队分工与项目背景", "成员介绍、开发环境、需求分析"],
    ["02", "数据说明与系统设计", "数据来源、预处理流程、系统架构"],
    ["03", "统计分析与可视化", "描述统计、时空规律、图表呈现"],
    ["04", "机器学习挖掘", "KMeans 站点聚类、五模型预测对比"],
    ["05", "AI 辅助与总结展望", "AI 协作过程、创新点、未来方向"],
  ];
  items.forEach((it, i) => {
    const y = 1.55 + i * 1.02;
    s.addShape(pptx.ShapeType.line, { x: M + 1.15, y: y + 0.52, w: CW - 1.15, h: 0, line: { color: T.line, width: 0.75 } });
    token(s, it[0], { x: M, y, w: 1.15, h: 0.6, fontSize: 26, color: T.accent, align: "left" });
    s.addText(it[1], { x: M + 1.3, y: y - 0.02, w: 7, h: 0.4, fontFace: FONT, fontSize: 17, bold: true, color: T.ink, margin: 0 });
    s.addText(it[2], { x: M + 1.3, y: y + 0.34, w: 8, h: 0.3, fontFace: FONT, fontSize: 10.5, color: T.muted, margin: 0 });
  });
  s.addText("DATA | ANALYSIS | MINING", { x: 9.4, y: 2.6, w: 3.3, h: 2.6, fontFace: FONT, fontSize: 12, bold: true, color: "DDE4EC", align: "right", valign: "middle", rotate: 90, margin: 0 });
  s.addText("纽约公共自行车数据分析", { x: 9.4, y: 6.3, w: 3.3, h: 0.4, fontFace: FONT, fontSize: 9, color: T.faint, align: "right", margin: 0 });
}

// ============================================================
// P3 团队成员与分工
// ============================================================
{
  const s = pptx.addSlide();
  pageHeader(s, "01 · TEAM", "团队成员与分工");
  s.addShape(pptx.ShapeType.rect, { x: M, y: 1.28, w: CW, h: 0.52, fill: { color: T.accentSoft } });
  s.addText("开发模式：统一契约、并行开发 —— config.py 列名规范与接口契约统一制定，各模块只依赖统一标准表 clean_citibike.csv，实现零冲突对接", {
    x: M + 0.12, y: 1.28, w: CW - 0.24, h: 0.52, fontFace: FONT, fontSize: 10.5, bold: true, color: T.accent, valign: "middle", margin: 0,
  });
  const members = [
    ["周晨琳", "架构设计", "整体架构设计；列名规范与目录结构约定；数据获取脚本与全流程整合；报告与 PPT 制作"],
    ["张子千", "数据预处理", "字段归一、枚举归一、时长补算、异常过滤、抽样与派生特征工程"],
    ["陈嘉欣", "统计分析", "描述统计、热门站点分析、时段规律挖掘、输出统计汇总表与业务建议"],
    ["童悦家", "机器学习", "KMeans 站点聚类（K=4，四指标）、骑行时长与站点客流五模型对比预测"],
    ["陈静萤", "可视化", "统计分析图表：时段/星期分布、用户与车型占比、TOP10 站点、空间分布地图"],
  ];
  members.forEach((m, i) => {
    const y = 2.00 + i * 0.94;
    s.addShape(pptx.ShapeType.rect, { x: M, y, w: 12.09, h: 0.84, fill: { color: T.surface }, line: { color: T.line, width: 0.75 } });
    token(s, m[0], { x: M + 0.18, y: y + 0.14, w: 0.85, h: 0.56, fontSize: 16, color: T.accent, align: "center" });
    s.addText(m[1], { x: M + 1.10, y: y + 0.26, w: 1.6, h: 0.32, fontFace: FONT, fontSize: 10, bold: true, color: T.ink, margin: 0 });
    s.addText(m[2], { x: M + 2.85, y: y + 0.12, w: 7.6, h: 0.62, fontFace: FONT, fontSize: 9.5, color: T.muted, valign: "middle", margin: 0 });
    s.addShape(pptx.ShapeType.rect, { x: M + 10.75, y: y + 0.22, w: 1.05, h: 0.4, fill: { color: T.accentSoft } });
    token(s, "20%", { x: M + 10.75, y: y + 0.22, w: 1.05, h: 0.4, fontSize: 11, color: T.accent });
  });
  conclusion(s, "五名成员模块基于同一列名规范与接口契约实现零冲突整合，全部工作量为均分协作（每人 20%）");
}

// ============================================================
// P4 项目背景与需求分析
// ============================================================
{
  const s = pptx.addSlide();
  pageHeader(s, "01 · BACKGROUND", "项目背景与需求分析");
  s.addText("项目背景", { x: M, y: 1.32, w: 4, h: 0.32, fontFace: FONT, fontSize: 13, bold: true, color: T.ink, margin: 0 });
  const bgs = [
    ["1", "Citi Bike 是纽约市最大的公共自行车系统，日均骑行超 10 万次"],
    ["2", "海量骑行数据蕴含城市出行规律与用户行为特征"],
    ["3", "通过数据分析可优化车辆调度、提升运营效率"],
    ["4", "课程要求：数据清洗 + 统计分析 + 可视化 + 数据挖掘"],
  ];
  bgs.forEach((b, i) => {
    const y = 1.72 + i * 0.58;
    s.addShape(pptx.ShapeType.ellipse, { x: M, y: y + 0.04, w: 0.28, h: 0.28, fill: { color: T.accent } });
    token(s, b[0], { x: M, y: y + 0.04, w: 0.28, h: 0.28, fontSize: 11, color: T.white });
    s.addText(b[1], { x: M + 0.45, y, w: 5.4, h: 0.36, fontFace: FONT, fontSize: 10, color: T.ink, valign: "middle", margin: 0 });
  });
  s.addShape(pptx.ShapeType.rect, { x: M, y: 4.25, w: 5.85, h: 0.4, fill: { color: T.accentSoft } });
  s.addText("数据层：官方原始 CSV → 清洗后标准表 clean_citibike.csv（16 列）", { x: M + 0.1, y: 4.25, w: 5.65, h: 0.4, fontFace: FONT, fontSize: 9, color: T.accent, valign: "middle", margin: 0 });
  s.addShape(pptx.ShapeType.rect, { x: M, y: 4.72, w: 5.85, h: 0.4, fill: { color: T.accentSoft } });
  s.addText("输出层：统计报表 + 统计图表 + 聚类/预测模型结果", { x: M + 0.1, y: 4.72, w: 5.65, h: 0.4, fontFace: FONT, fontSize: 9, color: T.accent, valign: "middle", margin: 0 });
  // 右列：功能模块
  s.addText("系统功能模块", { x: 6.98, y: 1.32, w: 4, h: 0.32, fontFace: FONT, fontSize: 13, bold: true, color: T.ink, margin: 0 });
  const mods = [
    ["数据获取", "download_data.py"],
    ["数据预处理", "preprocess.py"],
    ["统计分析", "analysis.py"],
    ["可视化", "plots.py"],
    ["机器学习", "ml.py"],
  ];
  mods.forEach((m, i) => {
    const y = 1.72 + i * 0.55;
    s.addShape(pptx.ShapeType.rect, { x: 6.98, y, w: 2.6, h: 0.45, fill: { color: T.surface }, line: { color: T.accent, width: 1 } });
    s.addText(m[0], { x: 6.98, y, w: 2.6, h: 0.45, fontFace: FONT, fontSize: 10.5, bold: true, color: T.accent, align: "center", valign: "middle", margin: 0 });
    s.addText("→", { x: 9.68, y: y + 0.02, w: 0.5, h: 0.4, fontFace: FONT, fontSize: 13, color: T.gold, align: "center", valign: "middle", margin: 0 });
    s.addText(m[1], { x: 10.25, y, w: 2.4, h: 0.45, fontFace: FONT, fontSize: 10, color: T.muted, valign: "middle", margin: 0 });
  });
  s.addText("开发环境", { x: 6.98, y: 4.72, w: 4, h: 0.3, fontFace: FONT, fontSize: 13, bold: true, color: T.ink, margin: 0 });
  s.addText("Python 3.10 · pandas · numpy · scikit-learn · matplotlib · folium", { x: 6.98, y: 5.10, w: 5.9, h: 0.3, fontFace: FONT, fontSize: 9.5, color: T.muted, margin: 0 });
  s.addText("PyCharm / VS Code · TRAE Coding Agent", { x: 6.98, y: 5.44, w: 5.9, h: 0.3, fontFace: FONT, fontSize: 9.5, color: T.muted, margin: 0 });
  conclusion(s, "围绕「数据获取 → 清洗 → 统计 → 可视化 → 挖掘」五层闭环设计系统功能模块");
}

// ============================================================
// P5 数据说明与预处理
// ============================================================
{
  const s = pptx.addSlide();
  pageHeader(s, "02 · DATA", "数据说明与预处理");
  const gap = (CW - 0.2 * 3) / 4;
  kpi(s, M, 1.32, gap, "499 万", "原始行程记录", T.accent);
  kpi(s, M + gap + 0.2, 1.32, gap, "497.5 万", "有效记录（清洗后）", T.green);
  kpi(s, M + 2 * (gap + 0.2), 1.32, gap, "0.36%", "异常剔除率", T.amber);
  kpi(s, M + 3 * (gap + 0.2), 1.32, gap, "20 万", "分析抽样样本", T.gold);
  // 左：数据来源
  s.addText("数据来源", { x: M, y: 2.85, w: 4, h: 0.3, fontFace: FONT, fontSize: 12.5, bold: true, color: T.ink, margin: 0 });
  const srcs = [
    ["▸", "纽约 Citi Bike 官方公开数据（2026 年 7 月）"],
    ["▸", "大月份数据：5 个 CSV 分片（2026-07 压缩包约 929MB）"],
    ["▸", "时间跨度：2026-06-30 ~ 2026-07-31"],
    ["▸", "原始 13 个字段，清洗后扩展为 16 列标准表"],
  ];
  srcs.forEach((t, i) => {
    const y = 3.22 + i * 0.42;
    s.addText(t[0], { x: M, y, w: 0.4, h: 0.3, fontFace: FONT, fontSize: 11, color: T.gold, margin: 0 });
    s.addText(t[1], { x: M + 0.42, y, w: 5.3, h: 0.3, fontFace: FONT, fontSize: 9.5, color: T.ink, margin: 0 });
  });
  s.addShape(pptx.ShapeType.rect, { x: M, y: 5.05, w: 5.85, h: 1.55, fill: { color: T.accentSoft } });
  s.addText("技术亮点", { x: M + 0.15, y: 5.18, w: 3, h: 0.3, fontFace: FONT, fontSize: 11, bold: true, color: T.accent, margin: 0 });
  s.addText("① 929MB 大文件采用 chunksize=500,000 分块读取，内存占用稳定\n② 本机 zip 优先 + 三候选 URL 兜底的数据获取策略\n③ 自动合并官方大月份多分片，避免重复下载", {
    x: M + 0.15, y: 5.5, w: 5.6, h: 1.0, fontFace: FONT, fontSize: 9, color: T.ink, margin: 0, lineSpacingMultiple: 1.15,
  });
  // 右：预处理流水线
  s.addText("预处理流水线", { x: 6.98, y: 2.85, w: 4, h: 0.3, fontFace: FONT, fontSize: 12.5, bold: true, color: T.ink, margin: 0 });
  const steps = [
    ["1", "字段归一", "新旧表头映射 → 16 标准列"],
    ["2", "时间解析", "started_at → datetime64"],
    ["3", "时长补算", "end - start → ride_duration"],
    ["4", "异常过滤", "60s ≤ 时长 ≤ 24h"],
    ["5", "随机抽样", "20 万条，seed=42"],
    ["6", "特征派生", "hour / weekday / is_weekend"],
  ];
  steps.forEach((st, i) => {
    const y = 3.22 + i * 0.53;
    s.addShape(pptx.ShapeType.rect, { x: 6.98, y, w: 0.34, h: 0.34, fill: { color: i === 3 ? T.amber : T.accent } });
    token(s, st[0], { x: 6.98, y, w: 0.34, h: 0.34, fontSize: 10.5, color: T.white });
    s.addText(st[1], { x: 7.48, y, w: 1.35, h: 0.34, fontFace: FONT, fontSize: 10.5, bold: true, color: T.ink, valign: "middle", margin: 0 });
    s.addText(st[2], { x: 8.95, y, w: 3.9, h: 0.34, fontFace: FONT, fontSize: 9.5, color: T.muted, valign: "middle", margin: 0 });
  });
  conclusion(s, "清洗口径与官方一致（剔除 <60s 行程），异常剔除率仅 0.36%，数据质量可靠");
}

// ============================================================
// P6 系统架构与设计
// ============================================================
{
  const s = pptx.addSlide();
  pageHeader(s, "02 · ARCHITECTURE", "系统架构与设计");
  const box = (x, y, w, h, title, sub, fill, color) => {
    s.addShape(pptx.ShapeType.rect, { x, y, w, h, fill: { color: fill }, line: { color: T.accent, width: 1 } });
    s.addText(title, { x, y: y + 0.08, w, h: 0.34, fontFace: FONT, fontSize: 11.5, bold: true, color, align: "center", valign: "middle", margin: 0 });
    if (sub) s.addText(sub, { x: x + 0.1, y: y + 0.42, w: w - 0.2, h: 0.5, fontFace: FONT, fontSize: 8.5, color: T.muted, align: "center", valign: "middle", margin: 0 });
  };
  const arrow = (x, y) => s.addText("→", { x, y, w: 0.5, h: 0.5, fontFace: FONT, fontSize: 16, bold: true, color: T.gold, align: "center", valign: "middle", margin: 0 });

  box(M, 1.50, 3.3, 0.9, "输入层", "Citi Bike 官方公开数据\n（S3 月度 zip 分片）", T.accentSoft, T.accent);
  arrow(4.05, 1.67);
  box(4.55, 1.50, 2.6, 0.9, "数据获取", "download_data.py\n本机zip优先 + URL兜底", T.surface, T.ink);
  arrow(7.28, 1.67);
  box(7.78, 1.50, 2.6, 0.9, "数据预处理", "preprocess.py\n分块清洗 + 特征派生", T.surface, T.ink);
  arrow(10.51, 1.67);
  box(11.01, 1.50, 1.7, 0.9, "标准表", "16列", T.accent, T.white);

  s.addText("统一标准表 clean_citibike.csv（16 列，接口契约）", { x: M, y: 2.62, w: 12.09, h: 0.3, fontFace: FONT, fontSize: 10, color: T.muted, align: "center", margin: 0 });

  // 三模块并行
  const mw = 3.7;
  box(M, 3.15, mw, 1.15, "统计分析", "analysis.py\n描述统计 · 时空规律 · 统计表", T.surface, T.ink);
  box(M + mw + 0.45, 3.15, mw, 1.15, "可视化", "plots.py\n统计图表 · 空间分布地图", T.surface, T.ink);
  box(M + 2 * (mw + 0.45), 3.15, mw, 1.15, "机器学习", "ml.py\nKMeans 聚类 · 双任务预测", T.surface, T.ink);
  s.addShape(pptx.ShapeType.line, { x: M + mw / 2, y: 2.40, w: 0, h: 0.75, line: { color: T.line, width: 1.25 } });
  s.addShape(pptx.ShapeType.line, { x: M + mw + 0.45 + mw / 2, y: 2.40, w: 0, h: 0.75, line: { color: T.line, width: 1.25 } });
  s.addShape(pptx.ShapeType.line, { x: M + 2 * (mw + 0.45) + mw / 2, y: 2.40, w: 0, h: 0.75, line: { color: T.line, width: 1.25 } });
  s.addShape(pptx.ShapeType.line, { x: M, y: 2.40, w: CW, h: 0, line: { color: T.line, width: 1 } });

  // 输出层
  box(M, 4.75, 12.09, 1.15, "输出层", "统计报表（output/统计结果.txt）· 统计图表（output/figures/）· 聚类与预测模型结果（机器学习模块/output/）", T.accentSoft, T.accent);
  s.addText("一键运行  python main.py    各模块也可独立执行", { x: M, y: 6.15, w: 12.09, h: 0.35, fontFace: FONT, fontSize: 11, bold: true, color: T.gold, align: "center", margin: 0 });
}

// ============================================================
// P7 描述性统计分析
// ============================================================
{
  const s = pptx.addSlide();
  pageHeader(s, "03 · ANALYSIS", "描述性统计分析");
  const gap = (CW - 0.2 * 3) / 4;
  kpi(s, M, 1.32, gap, "13.2 min", "平均骑行时长", T.accent);
  kpi(s, M + gap + 0.2, 1.32, gap, "9.5 min", "骑行时长中位数", T.green);
  kpi(s, M + 2 * (gap + 0.2), 1.32, gap, "79.5%", "会员用户占比", T.gold);
  kpi(s, M + 3 * (gap + 0.2), 1.32, gap, "73.4%", "电动自行车占比", T.accent);
  // 两个环形图
  const donut = (x, title, labels, values, colors) => {
    s.addText(title, { x, y: 2.90, w: 5.85, h: 0.3, fontFace: FONT, fontSize: 12, bold: true, color: T.ink, align: "center", margin: 0 });
    s.addChart(pptx.ChartType.doughnut, [{ name: title, labels, values }], {
      x: x + 1.0, y: 3.30, w: 3.85, h: 2.6,
      chartColors: colors,
      showLegend: true, legendPos: "b", legendFontSize: 9, legendColor: T.ink,
      showValue: true, dataLabelColor: T.white, dataLabelFontSize: 11, dataLabelPosition: "inEnd",
      holeSize: 62, showTitle: false, showPercent: true,
    });
  };
  donut(M, "用户类型分布", ["会员 Subscriber", "游客 Customer"], [79.5, 20.5], [T.accent, "BFC9D4"]);
  donut(6.98, "车型分布", ["电动 bike", "经典 classic"], [73.4, 26.6], [T.green, "C6D8C9"]);
  conclusion(s, "核心发现：Citi Bike 以短途「最后一公里」出行为主，已形成稳定的通勤用户基本盘，电动化趋势明显");
}

// ============================================================
// P8 时空规律挖掘
// ============================================================
{
  const s = pptx.addSlide();
  pageHeader(s, "03 · PATTERNS", "时空规律挖掘");
  s.addText("时段分布（早晚双峰）", { x: M, y: 1.28, w: 5.9, h: 0.26, fontFace: FONT, fontSize: 11, bold: true, color: T.ink, align: "center", margin: 0 });
  s.addText("星期分布（周三最高）", { x: 6.98, y: 1.28, w: 5.9, h: 0.26, fontFace: FONT, fontSize: 11, bold: true, color: T.ink, align: "center", margin: 0 });
  img(s, "hour_distribution.png", M, 1.56, 5.9, 2.43);
  img(s, "weekday_distribution.png", 6.98, 1.56, 5.9, 2.92);
  // TOP5 表
  const top5 = [
    ["排名", "热门借车站点 TOP5", "骑行次数", "占比"],
    ["1", "Pier 61 at Chelsea Piers", "752", "0.38%"],
    ["2", "Cooper Square & Astor Pl", "643", "0.32%"],
    ["3", "W 21 St & 6 Ave", "636", "0.32%"],
    ["4", "Central Park S & 6 Ave", "587", "0.29%"],
    ["5", "9 Ave & W 33 St", "584", "0.29%"],
  ];
  dataTable(s, M, 4.72, 6.4, top5, { colW: [0.8, 3.7, 1.1, 0.8], rowH: 0.32, headSize: 9.5, bodySize: 9 });
  s.addText("早高峰 8 时与晚高峰 17–19 时双峰明显，峰值 18 时（17,403 次）；\n工作日骑行量为周末的 3.1 倍；热门站点集中于曼哈顿中城", {
    x: 7.3, y: 4.85, w: 5.4, h: 1.6, fontFace: FONT, fontSize: 10.5, color: T.ink, margin: 0, lineSpacingMultiple: 1.3, valign: "middle",
  });
  conclusion(s, "通勤特征显著：早晚高峰潮汐 + 工作日主导 + 核心区集中，为调度优化提供直接依据");
}

// ============================================================
// P9 可视化成果
// ============================================================
{
  const s = pptx.addSlide();
  pageHeader(s, "03 · VISUALIZATION", "可视化成果");
  s.addText("TOP10 热门站点", { x: M, y: 1.28, w: 6.0, h: 0.26, fontFace: FONT, fontSize: 11, bold: true, color: T.ink, align: "center", margin: 0 });
  s.addText("用户类型占比", { x: 7.4, y: 1.28, w: 2.6, h: 0.26, fontFace: FONT, fontSize: 11, bold: true, color: T.ink, align: "center", margin: 0 });
  s.addText("站点空间分布", { x: 7.4, y: 4.25, w: 3.0, h: 0.26, fontFace: FONT, fontSize: 11, bold: true, color: T.ink, align: "center", margin: 0 });
  img(s, "hot_station_bar.png", M, 1.56, 6.0, 2.37);
  img(s, "weekend_pie.png", 7.6, 1.58, 2.4, 2.47);
  img(s, "station_scatter.png", 7.6, 4.55, 3.0, 2.40);
  s.addShape(pptx.ShapeType.rect, { x: 10.95, y: 4.50, w: 1.75, h: 2.5, fill: { color: T.accentSoft } });
  s.addText("🗺️\nfolium 交互地图\n（HTML）\n\n支持缩放与站点\n信息查看", {
    x: 10.95, y: 4.55, w: 1.75, h: 2.4, fontFace: FONT, fontSize: 9.5, bold: true, color: T.accent, align: "center", valign: "middle", margin: 0, lineSpacingMultiple: 1.25,
  });
  s.addShape(pptx.ShapeType.rect, { x: M, y: 4.30, w: 6.0, h: 2.45, fill: { color: T.surface }, line: { color: T.line, width: 0.75 } });
  s.addText("统计图表类型与输出", { x: M + 0.15, y: 4.42, w: 4, h: 0.28, fontFace: FONT, fontSize: 11, bold: true, color: T.accent, margin: 0 });
  s.addText("① 时段分布 / 星期分布柱状图（matplotlib）\n② 用户与车型占比饼图（matplotlib）\n③ TOP10 站点柱状图（matplotlib）\n④ 站点空间分布散点图（matplotlib）\n⑤ 交互式地图（folium，HTML）", {
    x: M + 0.15, y: 4.75, w: 5.7, h: 1.85, fontFace: FONT, fontSize: 9.5, color: T.ink, margin: 0, lineSpacingMultiple: 1.25,
  });
  imgCap(s, M, 3.95, 6.0, "图：各小时骑行量分布（双峰）");
  conclusion(s, "全部统计图保存至 output/figures/，中文统一 SimHei 字体；folium 地图支持交互式缩放与站点信息查看");
}

// ============================================================
// P10 KMeans 站点聚类（1/2）
// ============================================================
{
  const s = pptx.addSlide();
  pageHeader(s, "04 · CLUSTERING", "KMeans 站点聚类分析（1/2）");
  s.addShape(pptx.ShapeType.rect, { x: M, y: 1.24, w: CW, h: 0.5, fill: { color: T.accentSoft } });
  s.addText("样本 1985 个有效站点　|　特征 10 维（流量/时长/会员/高峰/周末/平衡度/经纬度）　|　Z-score 标准化　|　K=4（SSE 13,754.9 · 轮廓 0.1630 · CH 292.61 · DB 1.8809）", {
    x: M + 0.12, y: 1.24, w: CW - 0.24, h: 0.5, fontFace: FONT, fontSize: 9.5, bold: true, color: T.accent, valign: "middle", margin: 0,
  });
  s.addText("聚类空间分布", { x: M, y: 1.90, w: 6.0, h: 0.26, fontFace: FONT, fontSize: 11, bold: true, color: T.ink, align: "center", margin: 0 });
  img(s, "ml_fig2_kmeans_spatial_distribution.png", M, 2.18, 6.0, 4.48);
  s.addText("四类站点特征", { x: 6.98, y: 1.90, w: 5.9, h: 0.26, fontFace: FONT, fontSize: 11, bold: true, color: T.ink, align: "center", margin: 0 });
  const clu = [
    ["类别", "站点数", "日均流量", "平均时长", "会员占比"],
    ["高流量·通勤型｜会员主导", "694", "374.6 次", "12.9 分", "81.1%"],
    ["中流量·通勤型｜会员主导", "443", "151.5 次", "12.6 分", "80.7%"],
    ["低流量·通勤型｜会员主导", "571", "68.1 次", "12.3 分", "79.3%"],
    ["低流量·休闲型", "277", "109.3 次", "17.8 分", "65.3%"],
  ];
  dataTable(s, 6.98, 2.18, 5.9, clu, { colW: [2.5, 0.8, 1.0, 0.9, 0.9], rowH: 0.62, headSize: 9.5, bodySize: 8.5, align: "left" });
  s.addShape(pptx.ShapeType.rect, { x: 6.98, y: 5.62, w: 5.9, h: 1.05, fill: { color: T.surface }, line: { color: T.line, width: 0.75 } });
  s.addText("业务价值：聚类结果揭示不同类型站点的用户行为差异，可为差异化运营（休闲站周末营销、通勤站高峰调度）提供数据支撑", {
    x: 7.13, y: 5.70, w: 5.6, h: 0.9, fontFace: FONT, fontSize: 9.5, color: T.ink, valign: "middle", margin: 0, lineSpacingMultiple: 1.2,
  });
  conclusion(s, "四类画像 = 通勤枢纽 + 中量通勤 + 社区微循环 + 休闲景区，站点差异化运营有了量化依据");
}

// ============================================================
// P11 聚类数确定与画像（2/2）
// ============================================================
{
  const s = pptx.addSlide();
  pageHeader(s, "04 · CLUSTERING", "聚类数确定与站点画像（2/2）");
  s.addText("肘部法则与多指标验证（K=2~10）", { x: M, y: 1.28, w: 5.6, h: 0.26, fontFace: FONT, fontSize: 11, bold: true, color: T.ink, align: "center", margin: 0 });
  s.addText("四类站点画像雷达图", { x: 7.35, y: 1.28, w: 4.6, h: 0.26, fontFace: FONT, fontSize: 11, bold: true, color: T.ink, align: "center", margin: 0 });
  img(s, "ml_fig1_kmeans_elbow_method.png", M, 1.56, 5.6, 3.90);
  img(s, "ml_fig3_kmeans_radar_chart.png", 7.35, 1.56, 4.6, 3.90);
  s.addText("SSE 下降趋缓拐点 + 轮廓系数/CH/DB 交叉验证，\n综合确定 K=4", {
    x: 12.05, y: 2.30, w: 1.1, h: 2.2, fontFace: FONT, fontSize: 8.5, color: T.accent, align: "center", valign: "middle", margin: 0, lineSpacingMultiple: 1.2,
  });
  img(s, "ml_fig4_kmeans_cluster_count.png", M, 5.52, 3.3, 1.96);
  s.addShape(pptx.ShapeType.rect, { x: 4.25, y: 5.55, w: 8.45, h: 1.5, fill: { color: T.surface }, line: { color: T.line, width: 0.75 } });
  s.addText("四类站点数量：高流量通勤 694 站 · 中流量通勤 443 站 · 低流量休闲 277 站 · 低流量通勤 571 站", {
    x: 4.42, y: 5.68, w: 8.1, h: 0.35, fontFace: FONT, fontSize: 10.5, bold: true, color: T.ink, margin: 0,
  });
  s.addText("休闲型站点平均时长最长（17.8 分）且周末占比最高（33.6%），通勤型站点会员占比普遍超 79%，两类站点运营策略应显著区分", {
    x: 4.42, y: 6.10, w: 8.1, h: 0.8, fontFace: FONT, fontSize: 9.5, color: T.muted, margin: 0, lineSpacingMultiple: 1.2,
  });
}

// ============================================================
// P12 预测模型性能对比（1/2）
// ============================================================
{
  const s = pptx.addSlide();
  pageHeader(s, "04 · PREDICTION", "预测模型性能对比（1/2）");
  s.addText("骑行时长预测（特征 17 维 · 含骑行距离 distance_km，单位：分钟）", { x: M, y: 1.24, w: 5.9, h: 0.26, fontFace: FONT, fontSize: 9.5, bold: true, color: T.accent, margin: 0 });
  s.addText("站点客流预测（特征 13 维 · 含滞后客流 lag_1h/lag_24h，单位：次/小时）", { x: 6.98, y: 1.24, w: 5.9, h: 0.26, fontFace: FONT, fontSize: 9.5, bold: true, color: T.accent, margin: 0 });
  const durTab = [
    ["模型", "R²", "MAE"],
    ["线性回归", "0.1867", "5.097"],
    ["岭回归", "0.1867", "5.097"],
    ["决策树", "0.1572", "5.033"],
    ["随机森林 ★", "0.2031", "4.802"],
    ["梯度提升", "0.1945", "4.748"],
    ["基线-均值", "—", "8.309"],
  ];
  const demTab = [
    ["模型", "R²", "MAE"],
    ["线性回归", "0.8722", "50.54"],
    ["岭回归", "0.8723", "50.46"],
    ["决策树", "0.8797", "43.31"],
    ["随机森林", "0.9441", "30.67"],
    ["梯度提升 ★", "0.9465", "29.37"],
    ["基线-均值", "—", "155.11"],
  ];
  dataTable(s, M, 1.55, 3.6, durTab, { colW: [1.6, 1.0, 1.0], rowH: 0.27, headSize: 9, bodySize: 8.5 });
  dataTable(s, 6.98, 1.55, 3.6, demTab, { colW: [1.6, 1.0, 1.0], rowH: 0.27, headSize: 9, bodySize: 8.5 });
  s.addText("含 2 组朴素基线（均值/中位数）对比，量化模型真实增益", { x: 4.35, y: 2.0, w: 2.5, h: 2.2, fontFace: FONT, fontSize: 8.5, color: T.muted, valign: "middle", margin: 0, lineSpacingMultiple: 1.2 });
  s.addText("含 2 组朴素基线（均值/中位数）对比，量化模型真实增益", { x: 10.71, y: 2.0, w: 2.5, h: 2.2, fontFace: FONT, fontSize: 8.5, color: T.muted, valign: "middle", margin: 0, lineSpacingMultiple: 1.2 });
  s.addText("五模型对比（R² / MAE / RMSE）", { x: M, y: 4.15, w: 5.9, h: 0.26, fontFace: FONT, fontSize: 11, bold: true, color: T.ink, align: "center", margin: 0 });
  s.addText("五模型对比（R² / MAE / RMSE）", { x: 6.98, y: 4.15, w: 5.9, h: 0.26, fontFace: FONT, fontSize: 11, bold: true, color: T.ink, align: "center", margin: 0 });
  img(s, "ml_fig7_duration_model_comparison.png", M, 4.45, 5.9, 1.94);
  img(s, "ml_fig10_demand_model_comparison.png", 6.98, 4.45, 5.9, 1.94);
  conclusion(s, "客流预测梯度提升最优（R²=0.9465 · MAE=29.37），时长预测随机森林最优（R²=0.2031 · MAE=4.80 分钟）");
}

// ============================================================
// P13 预测效果与特征重要性（2/2）
// ============================================================
{
  const s = pptx.addSlide();
  pageHeader(s, "04 · PREDICTION", "预测效果与特征重要性（2/2）");
  s.addText("时长预测：真实值 vs 预测值 + 残差分布（随机森林）", { x: M, y: 1.28, w: 6.2, h: 0.26, fontFace: FONT, fontSize: 11, bold: true, color: T.ink, align: "center", margin: 0 });
  s.addText("客流预测：测试集真实/预测时序（梯度提升）", { x: 7.0, y: 1.28, w: 5.9, h: 0.26, fontFace: FONT, fontSize: 11, bold: true, color: T.ink, align: "center", margin: 0 });
  img(s, "ml_fig6_duration_prediction_scatter.png", M, 1.56, 6.2, 2.30);
  img(s, "ml_fig9_demand_prediction_timeseries.png", 7.0, 1.56, 5.32, 2.30);
  s.addText("时长预测特征重要性（随机森林）", { x: M, y: 4.05, w: 3.9, h: 0.26, fontFace: FONT, fontSize: 11, bold: true, color: T.ink, align: "center", margin: 0 });
  s.addText("客流预测特征重要性（梯度提升）", { x: 4.72, y: 4.05, w: 3.9, h: 0.26, fontFace: FONT, fontSize: 11, bold: true, color: T.ink, align: "center", margin: 0 });
  img(s, "ml_fig5_duration_feature_importance.png", M, 4.33, 3.9, 2.58);
  img(s, "ml_fig8_demand_feature_importance.png", 4.72, 4.33, 3.9, 2.27);
  s.addShape(pptx.ShapeType.rect, { x: 8.85, y: 4.33, w: 3.85, h: 2.58, fill: { color: T.accentSoft } });
  s.addText("关键结论", { x: 8.85, y: 4.45, w: 3.85, h: 0.3, fontFace: FONT, fontSize: 11.5, bold: true, color: T.accent, align: "center", margin: 0 });
  s.addText("客流预测：lag_1h 滞后客流主导（79.5%），可辅助车辆调度决策\n\n时长预测：骑行距离 distance_km 第一特征（61.8%），距离越远耗时越长\n\n相对均值基线：客流 MAE 降 81.1% · 时长 MAE 降 42.2%", {
    x: 9.0, y: 4.82, w: 3.55, h: 1.95, fontFace: FONT, fontSize: 9, color: T.ink, margin: 0, lineSpacingMultiple: 1.15,
  });
  conclusion(s, "双任务均通过误差归因验证：客流误差集中于高流量时段，时长误差集中于 >60 分钟长时骑行");
}

// ============================================================
// P14 AI 辅助开发过程
// ============================================================
{
  const s = pptx.addSlide();
  pageHeader(s, "05 · AI ASSIST", "AI 辅助开发过程");
  s.addShape(pptx.ShapeType.rect, { x: M, y: 1.30, w: CW, h: 0.5, fill: { color: T.accentSoft } });
  s.addText("使用工具：字节 TRAE Coding Agent —— 接口规范初稿起草、模块代码生成与调试排错；架构设计、规范制定与结果校验由小组成员人工完成", {
    x: M + 0.12, y: 1.30, w: CW - 0.24, h: 0.5, fontFace: FONT, fontSize: 9.5, bold: true, color: T.accent, valign: "middle", margin: 0,
  });
  s.addText("AI 生成的初始内容", { x: M, y: 2.0, w: 5.9, h: 0.3, fontFace: FONT, fontSize: 12.5, bold: true, color: T.ink, margin: 0 });
  const ais = [
    ["🤖", "config.py 列名规范与 data_dict.md 接口文档初稿"],
    ["🤖", "四个功能模块的初始代码框架"],
    ["🤖", "期末报告初稿结构与内容"],
    ["🤖", "基础可视化图表代码模板"],
  ];
  ais.forEach((a, i) => {
    const y = 2.42 + i * 0.52;
    s.addShape(pptx.ShapeType.rect, { x: M, y, w: 5.9, h: 0.42, fill: { color: T.surface }, line: { color: T.line, width: 0.75 } });
    s.addText(a[0], { x: M + 0.1, y, w: 0.5, h: 0.42, fontFace: FONT, fontSize: 12, align: "center", valign: "middle", margin: 0 });
    s.addText(a[1], { x: M + 0.65, y, w: 5.15, h: 0.42, fontFace: FONT, fontSize: 9.5, color: T.ink, valign: "middle", margin: 0 });
  });
  s.addText("关键迭代修改（人工主导）", { x: 6.98, y: 2.0, w: 5.9, h: 0.3, fontFace: FONT, fontSize: 12.5, bold: true, color: T.ink, margin: 0 });
  const its = [
    ["1", "内存优化", "一次性 read_csv → chunksize=50 万分块读取"],
    ["2", "编码兼容", "Windows 控制台 GBK 乱码 → utf-8 输出包装"],
    ["3", "接口统一", "可视化与 main.py 参数类型不一致 → 统一 value_counts"],
    ["4", "路径规范", "各模块写死路径 → 统一收敛到 config 常量"],
  ];
  its.forEach((it, i) => {
    const y = 2.42 + i * 0.52;
    s.addShape(pptx.ShapeType.rect, { x: 6.98, y, w: 5.9, h: 0.42, fill: { color: T.surface }, line: { color: T.line, width: 0.75 } });
    s.addShape(pptx.ShapeType.ellipse, { x: 7.08, y: y + 0.06, w: 0.3, h: 0.3, fill: { color: T.accent } });
    token(s, it[0], { x: 7.08, y: y + 0.06, w: 0.3, h: 0.3, fontSize: 9.5, color: T.white });
    s.addText(it[1], { x: 7.48, y, w: 1.0, h: 0.42, fontFace: FONT, fontSize: 10, bold: true, color: T.ink, valign: "middle", margin: 0 });
    s.addText(it[2], { x: 8.5, y, w: 4.28, h: 0.42, fontFace: FONT, fontSize: 9, color: T.muted, valign: "middle", margin: 0 });
  });
  conclusion(s, "AI 生成模块初始框架，全部经人工运行验证与修改；接口契约、路径规范、异常兜底等关键环节均由人工主导");
}

// ============================================================
// P15 项目创新点
// ============================================================
{
  const s = pptx.addSlide();
  pageHeader(s, "05 · INNOVATION", "项目创新点");
  const inn = [
    ["01", "📥", "智能数据获取策略", "本机 zip 优先 + 三候选 URL 兜底，自动检测并合并官方大月份多分片，避免重复下载 900MB+ 数据"],
    ["02", "⚡", "内存友好清洗流水线", "929MB 大文件采用 50 万行分块读取 + 流式清洗，内存占用稳定，普通笔记本即可运行"],
    ["03", "🤝", "统一契约并行开发", "五名成员基于同一列名规范与接口契约并行开发，实现零冲突整合，体现软件工程最佳实践"],
    ["04", "🎯", "聚类 + 多模型对比预测", "客流预测（梯度提升 R²=0.9465 · MAE=29.37）与时长预测（随机森林 R²=0.2031 · MAE=4.80）"],
  ];
  inn.forEach((n, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = M + col * (CW / 2 + 0.15);
    const y = 1.40 + row * 2.62;
    s.addShape(pptx.ShapeType.rect, { x, y, w: 5.97, h: 2.42, fill: { color: T.surface }, line: { color: T.line, width: 0.75 }, shadow: { type: "outer", color: "D8DEE5", blur: 4, offset: 1.5, angle: 90, opacity: 0.3 } });
    s.addShape(pptx.ShapeType.rect, { x, y, w: 5.97, h: 0.07, fill: { color: T.accent } });
    token(s, n[0], { x: x + 0.18, y: y + 0.20, w: 0.85, h: 0.5, fontSize: 20, color: T.accent, align: "left" });
    s.addText(n[2], { x: x + 0.18, y: y + 0.95, w: 5.6, h: 0.34, fontFace: FONT, fontSize: 13.5, bold: true, color: T.ink, margin: 0 });
    s.addText(n[3], { x: x + 0.18, y: y + 1.35, w: 5.6, h: 0.95, fontFace: FONT, fontSize: 9.5, color: T.muted, margin: 0, lineSpacingMultiple: 1.2 });
  });
}

// ============================================================
// P16 总结与展望
// ============================================================
{
  const s = pptx.addSlide();
  pageHeader(s, "05 · SUMMARY", "总结与展望");
  s.addText("项目总结", { x: M, y: 1.32, w: 5.9, h: 0.3, fontFace: FONT, fontSize: 13, bold: true, color: T.ink, margin: 0 });
  const sums = [
    "打通「数据获取 → 清洗 → 统计 → 可视化 → 挖掘」完整闭环",
    "在 499 万行真实数据上验证了统一架构约定的有效性",
    "五名成员模块基于同一规范实现零冲突整合",
    "产出统计分析图表 + 站点聚类 + 客流/时长多模型对比预测",
    "客流预测（梯度提升 R²=0.9465 · MAE=29.37 次/小时）可辅助车辆投放调度",
    "时长预测（随机森林 R²=0.2031 · MAE=4.80 分钟）以骑行距离为核心特征",
  ];
  sums.forEach((t, i) => {
    const y = 1.72 + i * 0.52;
    s.addShape(pptx.ShapeType.ellipse, { x: M, y: y + 0.05, w: 0.24, h: 0.24, fill: { color: T.green } });
    s.addText("✓", { x: M, y: y + 0.05, w: 0.24, h: 0.24, fontFace: FONT, fontSize: 9, bold: true, color: T.white, align: "center", valign: "middle", margin: 0 });
    s.addText(t, { x: M + 0.4, y, w: 5.5, h: 0.36, fontFace: FONT, fontSize: 9.5, color: T.ink, valign: "middle", margin: 0 });
  });
  s.addText("未来改进方向", { x: 6.98, y: 1.32, w: 5.9, h: 0.3, fontFace: FONT, fontSize: 13, bold: true, color: T.ink, margin: 0 });
  const futs = [
    ["📊", "特征工程增强", "引入天气、节假日、实时路况特征，继续提升时长预测 R²"],
    ["🕸️", "时空图模型", "聚类扩展为 ST-GCN 等时空图模型，刻画站点间依赖关系"],
    ["🖥️", "交互调度大屏", "接入 folium 交互大屏与调度仿真回放，形成决策闭环"],
    ["🔄", "实时数据流", "接入实时骑行数据 API，实现流式分析与动态预测"],
  ];
  futs.forEach((f, i) => {
    const y = 1.72 + i * 0.82;
    s.addShape(pptx.ShapeType.rect, { x: 6.98, y, w: 5.9, h: 0.68, fill: { color: T.surface }, line: { color: T.line, width: 0.75 } });
    s.addText(f[0], { x: 7.08, y, w: 0.5, h: 0.68, fontFace: FONT, fontSize: 14, align: "center", valign: "middle", margin: 0 });
    s.addText(f[1], { x: 7.62, y: y + 0.06, w: 5.1, h: 0.3, fontFace: FONT, fontSize: 10.5, bold: true, color: T.ink, margin: 0 });
    s.addText(f[2], { x: 7.62, y: y + 0.36, w: 5.1, h: 0.28, fontFace: FONT, fontSize: 8.5, color: T.muted, margin: 0 });
  });
  conclusion(s, "本项目在真实海量数据上验证了「统一契约 + 并行开发 + 数据挖掘」的完整工程实践");
}

// ============================================================
// P17 结束页（深蓝）
// ============================================================
{
  const s = pptx.addSlide();
  s.background = { color: T.accent };
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 7.10, w: 13.33, h: 0.40, fill: { color: T.gold } });
  s.addShape(pptx.ShapeType.rect, { x: 0, y: 0, w: 13.33, h: 0.12, fill: { color: "FFFFFF" } });
  s.addText("感谢聆听", { x: 0.9, y: 2.35, w: 11.5, h: 1.0, fontFace: FONT, fontSize: 44, bold: true, color: T.white, margin: 0 });
  s.addText("Thank You for Your Attention", { x: 0.92, y: 3.45, w: 8, h: 0.4, fontFace: FONT, fontSize: 16, color: "AEC9E4", margin: 0 });
  s.addShape(pptx.ShapeType.line, { x: 0.95, y: 4.20, w: 2.2, h: 0, line: { color: T.gold, width: 2.5 } });
  s.addText("Q & A", { x: 0.92, y: 4.75, w: 4, h: 0.5, fontFace: FONT, fontSize: 22, bold: true, color: T.gold, margin: 0 });
  s.addText("纽约公共自行车数据分析 · Citi Bike Data Analysis", { x: 0.92, y: 5.55, w: 10, h: 0.35, fontFace: FONT, fontSize: 12, color: "E6EEF6", margin: 0 });
  s.addText("杭州电子科技大学 · 《软件开发实践1》期末答辩 · 2026 年 9 月", { x: 0.92, y: 5.95, w: 10, h: 0.35, fontFace: FONT, fontSize: 11, color: "AEC9E4", margin: 0 });
  // 四角装饰（与封面呼应）
  s.addShape(pptx.ShapeType.line, { x: 0.55, y: 0.55, w: 0.45, h: 0, line: { color: "7C9ABD", width: 1.25 } });
  s.addShape(pptx.ShapeType.line, { x: 0.55, y: 0.55, w: 0, h: 0.45, line: { color: "7C9ABD", width: 1.25 } });
  s.addShape(pptx.ShapeType.line, { x: 12.33, y: 0.55, w: 0.45, h: 0, line: { color: "7C9ABD", width: 1.25 } });
  s.addShape(pptx.ShapeType.line, { x: 12.78, y: 0.55, w: 0, h: 0.45, line: { color: "7C9ABD", width: 1.25 } });
  s.addShape(pptx.ShapeType.line, { x: 0.55, y: 6.55, w: 0.45, h: 0, line: { color: "7C9ABD", width: 1.25 } });
  s.addShape(pptx.ShapeType.line, { x: 0.55, y: 6.55, w: 0, h: 0.45, line: { color: "7C9ABD", width: 1.25 } });
  s.addShape(pptx.ShapeType.line, { x: 12.33, y: 6.55, w: 0.45, h: 0, line: { color: "7C9ABD", width: 1.25 } });
  s.addShape(pptx.ShapeType.line, { x: 12.78, y: 6.55, w: 0, h: 0.45, line: { color: "7C9ABD", width: 1.25 } });
}

pptx.writeFile({ fileName: OUT }).then(() => {
  console.log("已生成:", OUT);
  console.log("页数:", slideIndex);
}).catch(e => { console.error("生成失败:", e); process.exit(1); });
