# -*- coding: utf-8 -*-
"""
model/analyze.py —— 机器学习模块统一入口（成员4）
=================================================
包装 机器学习模块/src/ml.py 的完整流程（KMeans 站点聚类 + 骑行时长预测 + 客流预测），
为 main.py 提供统一的 run() 接口。

运行：main.py 步骤4 调用本模块
输出：机器学习模块/output/model/ 模型指标 CSV + 机器学习模块/output/fig/ 图表
"""

import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ML_SRC = os.path.join(BASE_DIR, "机器学习模块", "src")


def run():
    """执行机器学习全流程（聚类 + 两个预测任务 + 总结报告）。"""
    if ML_SRC not in sys.path:
        sys.path.insert(0, ML_SRC)
    from ml import main as _ml_main
    _ml_main()


if __name__ == "__main__":
    run()
