# -*- coding: utf-8 -*-
"""生成最终提交压缩包，结构：
提交包.zip
├── 代码.zip                      # 项目代码（排除数据/缓存）
├── 答辩PPT-纽约公共自行车数据分析.pptx
├── 小组期末报告-纽约公共自行车数据分析.docx
└── 调研报告/                     # 各成员调研报告（姓名-调研报告.docx）
    └── 调研报告-周晨琳.docx
"""
import os, shutil, zipfile

SRC = r'C:/Users/Lenovo/nyc_citibike'
STAGE = os.path.join(os.environ.get('TEMP', '/tmp'), 'citi_submit')
OUT_ZIPS = [r'C:/Users/Lenovo/citi-bike-提交包.zip',
            r'D:/OneDrive/Desktop/项目提交材料/citi-bike-提交包.zip']

# ---------- 1. 组装暂存目录 ----------
shutil.rmtree(STAGE, ignore_errors=True)
os.makedirs(os.path.join(STAGE, '调研报告'))

# 1.1 代码包（排除数据/缓存/大文件）
code_stage = os.path.join(STAGE, '_code')
items = ['main.py', 'config.py', 'download_data.py', 'requirements.txt',
         'requirements-optional.txt', 'README.md', '.gitignore',
         'storage', 'analysis', 'model', 'visualization', 'cleaning',
         'docs/data_dict.md']
ig = shutil.ignore_patterns('__pycache__')
for it in items:
    s, d = os.path.join(SRC, it), os.path.join(code_stage, it)
    parent = os.path.dirname(d)
    os.makedirs(parent, exist_ok=True)
    if os.path.isdir(s):
        shutil.copytree(s, d, ignore=ig)
    else:
        shutil.copy2(s, d)
code_zip = os.path.join(STAGE, '代码.zip')
with zipfile.ZipFile(code_zip, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(code_stage):
        for f in files:
            p = os.path.join(root, f)
            z.write(p, os.path.relpath(p, code_stage))
shutil.rmtree(code_stage)

# 1.2 PPT / 期末报告 / 调研报告
shutil.copy2(os.path.join(SRC, 'docs', '答辩PPT-纽约公共自行车数据分析.pptx'),
             os.path.join(STAGE, '答辩PPT-纽约公共自行车数据分析.pptx'))
shutil.copy2(os.path.join(SRC, 'docs', '期末报告-纽约公共自行车数据分析.docx'),
             os.path.join(STAGE, '小组期末报告-纽约公共自行车数据分析.docx'))
shutil.copy2(os.path.join(SRC, 'docs', '调研报告-周晨琳.docx'),
             os.path.join(STAGE, '调研报告', '调研报告-周晨琳.docx'))
# 其他成员调研报告放入：STAGE/调研报告/调研报告-姓名.docx 后重跑本脚本

# ---------- 2. 压缩 ----------
for zp in OUT_ZIPS:
    d = os.path.dirname(zp)
    os.makedirs(d, exist_ok=True)
    if os.path.exists(zp):
        os.remove(zp)
    with zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(STAGE):
            for f in files:
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, STAGE))
    print(f'saved: {zp}  ({os.path.getsize(zp)/1048576:.2f} MB)')
shutil.rmtree(STAGE)

