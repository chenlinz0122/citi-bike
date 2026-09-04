# -*- coding: utf-8 -*-
"""生成功能模块/业务流程图（用于报告第4节 需求分析）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import config

FONT = config.CHINESE_FONT or "SimHei"
fig, ax = plt.subplots(figsize=(12, 5.2))
ax.set_xlim(0, 12); ax.set_ylim(0, 5.2); ax.axis("off")

def box(x, y, w, h, text, fc="#dbe9f6", fs=10):
    ax.add_patch(mpatches.FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.08",
        fc=fc, ec="#2f5b8f", lw=1.2))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center",
            fontsize=fs, fontfamily=FONT, linespacing=1.5)

def arrow(x1, y1, x2, y2, style="-|>"):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color="#2f5b8f", lw=1.4))

# ---- 顶层：五个功能模块（等宽等距，不重叠）----
W, H, Y = 2.0, 1.0, 3.6
xs = [0.4, 2.9, 5.4, 7.9, 10.0]
labels = ["① 数据获取\ndownload_data.py",
          "② 数据预处理\npreprocess.py",
          "③ 统计分析\nanalysis.py",
          "④ 可视化\nplots.py",
          "⑤ 机器学习\nml.py / analyze.py"]
for x, t in zip(xs, labels):
    box(x, Y, W, H, t)
for i in range(4):
    x1 = xs[i] + W
    x2 = xs[i + 1] if i < 3 else xs[4]
    arrow(min(x1, x2 - 0.05) if i == 3 else x1, Y + H/2, x2, Y + H/2)

# ---- 底层：数据层 / 统一规范 / 输出层（三块互不重叠）----
B2Y, B2H = 0.4, 1.6
box(0.4, B2Y, 4.2, B2H,
    "数据层\n官方 zip（974MB / 499 万行）\n→ clean_citibike.csv（20 万条标准表）",
    "#e8f3e6", fs=9.5)
box(5.0, B2Y, 2.0, B2H, "统一规范\nconfig.py\n接口契约", "#f6dede", fs=9.5)
box(7.6, B2Y, 4.4, B2H,
    "输出层\noutput/ 统计结果 · 28 张图表\n聚类结果 CSV · 模型评估指标",
    "#fdf1dc", fs=9.5)

# 箭头：②↓数据层、⑤↓输出层、统一规范↑支撑全流程
arrow(3.9, Y, 2.5, B2Y + B2H)
arrow(11.0, Y, 9.8, B2Y + B2H)
for tx in (1.5, 6.0, 9.3):
    arrow(6.0, B2Y + B2H, tx, Y, style="-|>")
ax.annotate("", xy=(6.0, B2Y + B2H), xytext=(6.0, Y),
            arrowprops=dict(arrowstyle="-", color="#b0413e",
                            lw=1.2, linestyle="--"))
ax.text(6.15, (Y + B2Y + B2H)/2, "统一约定路径/列名/参数",
        fontsize=9, fontfamily=FONT, color="#b0413e", va="center")

ax.set_title("系统功能模块与业务流程图", fontsize=13, fontfamily=FONT, pad=12)
out = os.path.join(config.FIG_DIR, "flow_diagram.png")
fig.tight_layout()
fig.savefig(out, dpi=150)
plt.close(fig)
print("saved:", out)

