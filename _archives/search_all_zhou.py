# -*- coding: utf-8 -*-
import os, zipfile

found_docx = []
found_zip = []
roots = [r'D:\OneDrive', 'E:/', r'C:\Users\Lenovo']
skip_dirs = ['AppData', '.trae-cn', 'System Volume Information', 'node_modules', '$Recycle']
for root in roots:
    if not os.path.isdir(root):
        continue
    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if not any(s in d for s in skip_dirs)]
        try:
            for f in files:
                low = f.lower()
                if low.endswith('.docx') and '周晨琳' in f and '调研报告' in f:
                    found_docx.append(os.path.join(dirpath, f))
                elif low.endswith('.zip') and any(k in f for k in ['提交', '周晨琳', '自行车']):
                    found_zip.append(os.path.join(dirpath, f))
        except OSError:
            pass
print('== 周晨琳调研报告 docx 副本 ==')
for f in found_docx:
    print(' ', f, os.path.getsize(f))
print('== 候选zip（检查内含周晨琳报告）==')
for z in found_zip:
    try:
        with zipfile.ZipFile(z) as zf:
            hits = [i.filename for i in zf.infolist() if '周晨琳' in i.filename and '调研报告' in i.filename]
        if hits:
            print(' ', z, '->', hits)
    except Exception as e:
        print(' ', z, '读取失败:', e)
