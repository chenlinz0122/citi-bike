# -*- coding: utf-8 -*-
import copy
from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

path = r'D:\OneDrive\Desktop\项目提交材料\调研报告-周晨琳.docx'
doc = Document(path)
ps = doc.paragraphs

h_idx = next(i for i, p in enumerate(ps) if '参考文献' in p.text)
tmpl = ps[h_idx + 1]
tmpl_pPr = copy.deepcopy(tmpl._p.pPr) if tmpl._p.pPr is not None else None
tmpl_rPr = None
for r in tmpl.runs:
    if r._r.rPr is not None:
        tmpl_rPr = copy.deepcopy(r._r.rPr)
        break

refs = [p for p in ps[h_idx + 1:] if p.text.strip().startswith('[')]
print('删除旧文献条数:', len(refs))
for p in refs:
    p._p.getparent().remove(p._p)

new_refs = [
    '[1]乔少杰,韩楠,岳昆,等.基于数据场聚类的共享单车需求预测模型[J].软件学报,2022,33(04):1451\u20111476.',
    '[2]郭洪飞,赵淑曼,任亚平,等.基于自适应聚类的共享单车需求预测与投放决策[J].计算机集成制造系统,2023,29(05):1747\u20111757.',
    '[3]柯日宏,吴升,柯玮文.一种识别共享单车潮汐点的时空模型和基于KNN\u2011LightGBM的租还需求预测方法[J].地球信息科学学报,2023,25(04):741\u2011753.',
    '[4]徐悦甡,周奕杉,黄健斌,等.面向共享单车服务调度的流程规划算法[J].计算机集成制造系统,2022,28(10):3284\u20113294.',
    '[5]仝照民,刘耀林,张紫怡,等.骑行流密度聚类下的共享单车源汇空间识别[J].武汉大学学报(信息科学版),2025,50(01):184\u2011196.',
    '[6]姜晓,白璐斌,楼夏寅,等.基于多尺度时空聚类的共享单车潮汐特征挖掘与需求预测研究[J].地球信息科学学报,2022,24(06):1047\u20111060.',
    '[7]戢晓峰,陈方.建成环境对共享单车时间集聚模式的非线性影响[J].吉林大学学报(工学版),2024,54(03):721\u2011731.',
    '[8]李福.共享单车用户骑行起讫点时空特征分析[J].交通信息与安全,2022,40(03):112\u2011120.',
]

anchor = ps[h_idx]._p
for text in new_refs:
    p_el = OxmlElement('w:p')
    anchor.addnext(p_el)
    anchor = p_el
    if tmpl_pPr is not None:
        p_el.append(copy.deepcopy(tmpl_pPr))
    r_el = OxmlElement('w:r')
    if tmpl_rPr is not None:
        r_el.append(copy.deepcopy(tmpl_rPr))
    t_el = OxmlElement('w:t')
    t_el.set(qn('xml:space'), 'preserve')
    t_el.text = text
    r_el.append(t_el)
    p_el.append(r_el)

doc.save(path)
print('已保存，新文献条数:', len(new_refs))
