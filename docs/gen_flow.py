# -*- coding: utf-8 -*-
"""生成功能模块/业务流程图（用于报告第4节 需求分析）。"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import config

fig, ax = plt.subplots(figsize=(11, 4.2))
ax.set_xlim(0, 11); ax.set_ylim(0, 4.2); ax.axis("off")

def box(x, y, w, h, text, fc="#dbe9f6"):
    ax.add_patch(mpatches.FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0.06",
        fc=fc, ec="#2f5b8f", lw=1.2))
    ax.text(x + w/2, y + h/2, text, ha="center", va="center",
            fontsize=10.5, fontfamily=config.CHINESE_FONT or "SimHei")

def arrow(x1, y1, x2, y2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="-|>", color="#2f5b8f", lw=1.4))

# 主流程
box(0.3, 2.6, 1.9, 1.0, "① 数据获取\ndownload_data.py")
box(2.6, 2.6, 1.9, 1.0, "② 数据预处理\npreprocess.py")
box(4.9, 2.6, 1.9, 1.0, "③ 统计分析\nanalysis.py")
box(7.2, 2.6, 1.9, 1.0, "④ 可视化\nplots.py")
box(9.0, 2.6, 1.8, 1.0, "⑤ 机器学习\nml.py / analyze.py")
arrow(2.2, 3.1, 2.6, 3.1); arrow(4.5, 3.1, 4.9, 3.1)
arrow(6.8, 3.1, 7.2, 3.1); arrow(9.1, 3.1, 9.0, 3.1)

# 下层：数据与输出
box(0.3, 0.6, 4.2, 1.2, "数据层\n官方zip(974MB/499万行) → clean_citibike.csv\n(20万条统一标准表)", "#e8f3e6")
box(5.2, 0.6, 5.6, 1.2, "输出层\noutput/统计结果.txt · 28张图表(png) · 模型指标\nstation_clusters.csv · KMeans/回归评估指标", "#fdf1dc")
arrow(2.4, 2.6, 2.4, 1.8); arrow(7.9, 2.6, 7.9, 1.8)

# 统一规范侧
box(3.0, 0.6, 1.6, 1.2, "config.py\n统一规范", "#f6dede")
ax.set_title("图4-1 系统功能模块与业务流程图", fontsize=12,
             fontfamily=config.CHINESE_FONT or "SimHei")
out = os.path.join(config.FIG_DIR, "flow_diagram.png")
fig.tight_layout(); fig.savefig(out, dpi=150); plt.close(fig)
print("saved:", out)
