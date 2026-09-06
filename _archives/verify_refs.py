# -*- coding: utf-8 -*-
from docx import Document

path = r'D:\OneDrive\Desktop\项目提交材料\调研报告-周晨琳.docx'
doc = Document(path)
ps = doc.paragraphs
total = len([p for p in ps if p.text.strip()])
print('非空段落数:', total)
ref_start = next(i for i, p in enumerate(ps) if '参考文献' in p.text)
print('--- 参考文献之后的内容 ---')
for i in range(ref_start, len(ps)):
    p = ps[i]
    if not p.text.strip():
        continue
    font = None
    if p.runs:
        r = p.runs[0]
        font = (r.font.name, r.font.size.pt if r.font.size else None)
    print(i, '|', font, '|', p.text[:60])
print('--- 全文前3段（确认正文未受影响）---')
n = 0
for p in ps:
    if p.text.strip() and n < 3:
        print(' *', p.text[:40])
        n += 1
