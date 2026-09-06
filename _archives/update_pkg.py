# -*- coding: utf-8 -*-
import zipfile, shutil, os, hashlib

src = r'D:\OneDrive\Desktop\项目提交材料\[01]周晨琳_陈嘉欣_张子千_童悦家_陈静萤_自行车.zip'
stage = r'E:\citi-bike\_archives\pkg_stage'
out = src

if os.path.isdir(stage):
    shutil.rmtree(stage)
os.makedirs(stage)
with zipfile.ZipFile(src) as z:
    z.extractall(stage)

new_zhou = r'D:\OneDrive\Desktop\项目提交材料\调研报告-周晨琳.docx'
shutil.copy2(new_zhou, os.path.join(stage, '调研报告', '调研报告-周晨琳.docx'))
shutil.copy2(r'D:\OneDrive\Desktop\项目提交材料\调研报告-陈嘉欣.docx',
             os.path.join(stage, '调研报告', '调研报告-陈嘉欣.docx'))
shutil.copy2(r'D:\OneDrive\Desktop\项目提交材料\期末报告-纽约公共自行车数据分析.docx',
             os.path.join(stage, '小组期末报告.docx'))
shutil.copy2(r'D:\OneDrive\Desktop\项目提交材料\答辩PPT-纽约公共自行车数据分析.pptx',
             os.path.join(stage, '答辩PPT.pptx'))

with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(stage):
        for f in sorted(files):
            p = os.path.join(root, f)
            z.write(p, os.path.relpath(p, stage))

print('新包已生成')
with zipfile.ZipFile(out) as z:
    for i in z.infolist():
        print('  %10d  %s' % (i.file_size, i.filename))
print('包大小:', os.path.getsize(out))

verify = r'E:\citi-bike\_archives\pkg_verify'
if os.path.isdir(verify):
    shutil.rmtree(verify)
os.makedirs(verify)
with zipfile.ZipFile(out) as z:
    z.extractall(verify)

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()[:16]

checks = [
    (new_zhou, os.path.join(verify, '调研报告', '调研报告-周晨琳.docx'), '周晨琳调研报告'),
    (r'D:\OneDrive\Desktop\项目提交材料\期末报告-纽约公共自行车数据分析.docx',
     os.path.join(verify, '小组期末报告.docx'), '期末报告'),
    (r'D:\OneDrive\Desktop\项目提交材料\答辩PPT-纽约公共自行车数据分析.pptx',
     os.path.join(verify, '答辩PPT.pptx'), '答辩PPT'),
]
all_ok = True
for src_f, dst_f, name in checks:
    a, b = sha(src_f), sha(dst_f)
    ok = a == b
    all_ok = all_ok and ok
    label = '一致' if ok else '不一致!'
    print(name + ': ' + label + '  ' + a)

shutil.rmtree(verify)
shutil.rmtree(stage)
print('临时目录已清理')
print('全部一致' if all_ok else '存在不一致!')
