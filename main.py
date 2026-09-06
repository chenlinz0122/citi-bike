# -*- coding: utf-8 -*-
"""
main.py —— 项目主程序入口
========================================
一键依次执行完整流程：
  1. 数据预处理  ->  storage/preprocess.run()
  2. 统计分析    ->  analysis/analysis.run()
  3. 可视化图表  ->  visualization/plots 系列
  4. 机器学习    ->  model/analyze.run()

运行：  python main.py
若只想跑某一环节，见 README 分模块说明。

说明：本脚本通过 utf-8 输出，避免 Windows 控制台的编码问题。
"""

import os
import sys
import io

# --- 解决 Windows 控制台 GBK 编码问题（中文/特殊字符正常显示）---
try:
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
except Exception:
    pass

# 保证能找到项目内的模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import config


def step0_get_data():
    """0. 数据获取（组长：download_data.py）"""
    print("\n" + "=" * 60)
    print("步骤0：数据获取（download_data.py，本机zip优先）")
    print("=" * 60)
    from download_data import download_period
    path, n = download_period(config.DEFAULT_MONTH)
    print(f"  原始数据：{path}")
    print(f"  记录行数：约 {n:,} 行")
    return


def step1_preprocess():
    """1. 数据预处理"""
    print("\n" + "=" * 60)
    print("步骤1：数据预处理（清洗、抽样、构造特征）")
    print("=" * 60)
    from storage.preprocess import run
    df = run()
    print(f"  清洗后记录数：{len(df):,} 条")
    return df


def step2_analysis(df):
    """2. 描述统计与时空分析"""
    print("\n" + "=" * 60)
    print("步骤2：统计分析（描述性统计 + 时空规律）")
    print("=" * 60)
    from analysis.analysis import run
    run()
    return df


def step3_visualize(df):
    """3. 可视化（含图表，可含地图）"""
    print("\n" + "=" * 60)
    print("步骤3：可视化图表")
    print("=" * 60)
    from analysis.analysis import hot_stations, station_summary
    from visualization.plots import (hour_distribution, weekday_distribution,
                                     weekend_pie, hot_station_bar,
                                     station_scatter, station_folium_map)
    start, end = hot_stations(df)
    ss = station_summary(df)
    hour_distribution(df)
    weekday_distribution(df)
    weekend_pie(df)
    hot_station_bar(start, end)
    station_scatter(ss)
    station_folium_map(ss)   # 若未装 folium 会提示跳过，不影响
    return ss


def step4_model(df):
    """4. 机器学习（聚类 + 预测）"""
    print("\n" + "=" * 60)
    print("步骤4：机器学习挖掘（站点聚类 + 骑行时长/客流预测）")
    print("=" * 60)
    from model.analyze import run
    run()
    return df


def _collect_outputs():
    """汇总全部输出：统计图、机器学习图、模型文件，统一展示清单。"""
    import shutil

    figures_dir = os.path.join(config.OUTPUT_DIR, "figures")
    ml_fig_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              "机器学习模块", "output", "fig")
    ml_model_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                "机器学习模块", "output", "model")

    # 把机器学习 10 张图汇总到主输出目录 output/figures/，便于统一查看与引用
    if os.path.isdir(ml_fig_dir):
        copied = 0
        for f in sorted(os.listdir(ml_fig_dir)):
            if f.startswith("ml_") and f.endswith(".png"):
                shutil.copy2(os.path.join(ml_fig_dir, f),
                             os.path.join(figures_dir, f))
                copied += 1
        print(f"  [汇总] 机器学习图已复制到 output/figures/（{copied} 张）")

    print("\n" + "=" * 60)
    print("✅ 全流程执行完成！全部输出清单：")
    print("-" * 60)
    print("  统计报告:  output/统计结果.txt")
    print("  站点表:    output/station_summary.csv")
    print("-" * 60)
    print("  统计可视化（6 张，output/figures/）:")
    stat_figs = sorted(f for f in os.listdir(figures_dir)
                       if f.endswith(".png") and not f.startswith("ml_"))
    for f in stat_figs:
        print(f"    - output/figures/{f}")
    print("-" * 60)
    print("  机器学习可视化（10 张，output/figures/ 与 机器学习模块/output/fig/）:")
    ml_figs = sorted(f for f in os.listdir(figures_dir) if f.startswith("ml_"))
    for f in ml_figs:
        print(f"    - output/figures/{f}")
    print("-" * 60)
    print("  机器学习结果文件（机器学习模块/output/model/）:")
    if os.path.isdir(ml_model_dir):
        for f in sorted(os.listdir(ml_model_dir)):
            print(f"    - 机器学习模块/output/model/{f}")
    print("  模型报告:  机器学习模块/output/model/ml_summary_report.txt")
    print("=" * 60)


def main():
    print("=" * 60)
    print("  纽约公共自行车(Citi Bike) 数据分析与可视化 系统")
    print("=" * 60)

    step0_get_data()
    df = step1_preprocess()
    step2_analysis(df)
    ss = step3_visualize(df)
    step4_model(df)
    _collect_outputs()


if __name__ == "__main__":
    main()