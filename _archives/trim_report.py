# -*- coding: utf-8 -*-
from docx import Document

path = r'D:\OneDrive\Desktop\项目提交材料\调研报告-周晨琳.docx'
doc = Document(path)
p = doc.paragraphs[18]
t = p.runs[0].text

assert '③机器学习挖掘——' in t and '④可视化呈现' in t
start = t.index('③机器学习挖掘——')
end = t.index('④可视化呈现')
assert start < end

new_iii = ('③机器学习挖掘——K-Means 站点聚类依据骑行流量、平均时长、高峰时段、会员占比与经纬度等 10 维特征，'
           '将 1,985 个有效站点划分为高流量通勤型（694 站）、中流量通勤型（443 站）、低流量通勤型（571 站）与低流量休闲型（277 站）四类，'
           '前三类均呈会员主导的通勤特征，休闲型站点周末出行占比偏高；'
           '回归预测采用线性回归、岭回归、决策树、随机森林、梯度提升 5 种模型对比，'
           '客流预测以梯度提升最优（R²≈0.95、MAE≈29 次/小时），骑行时长预测以随机森林最优（R²≈0.20、MAE≈4.8 分钟），'
           '特征重要性显示骑行距离与前 1 小时客流滞后项分别是最关键特征，'
           '印证了前沿研究引入距离、天气与时空图特征的必要性。')

new_t = t[:start] + new_iii + t[end:]
p.runs[0].text = new_t
doc.save(path)
print('精简完成，段落长度 %d -> %d' % (len(t), len(new_t)))
