# -*- coding: utf-8 -*-
"""打包提交 zip（排除 __pycache__ 与大数据，绕过被占用的 docx）。"""
import os, shutil, zipfile, tempfile

src = r'C:/Users/Lenovo/nyc_citibike'
staging = os.path.join(tempfile.gettempdir(), 'citi_stage')
os.makedirs(staging, exist_ok=True)
shutil.rmtree(staging); os.makedirs(staging)

items = ['main.py', 'config.py', 'download_data.py', 'requirements.txt',
         'requirements-optional.txt', 'README.md', '.gitignore',
         'storage', 'analysis', 'model', 'visualization', 'cleaning',
         'docs', 'output']
ig = shutil.ignore_patterns('__pycache__')
for it in items:
    s, d = os.path.join(src, it), os.path.join(staging, it)
    if os.path.isdir(s):
        shutil.copytree(s, d, ignore=ig)
    else:
        shutil.copy2(s, d)

zippath = r'C:/Users/Lenovo/citi-bike-提交包.zip'
if os.path.exists(zippath):
    os.remove(zippath)
with zipfile.ZipFile(zippath, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(staging):
        for f in files:
            p = os.path.join(root, f)
            z.write(p, os.path.relpath(p, staging))
shutil.rmtree(staging)
z = zipfile.ZipFile(zippath)
print('文件数:', len(z.namelist()),
      '| pycache残留:', [n for n in z.namelist() if '__pycache__' in n])
print('大小MB:', round(os.path.getsize(zippath) / 1048576, 2))
