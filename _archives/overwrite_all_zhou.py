# -*- coding: utf-8 -*-
import os, shutil, zipfile, hashlib, time

desk = r'D:\OneDrive\Desktop\项目提交材料\调研报告-周晨琳.docx'

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for chunk in iter(lambda: f.read(65536), b''):
            h.update(chunk)
    return h.hexdigest()[:16]

targets = [
    (r'E:\python\citi-bike\output\reports\调研报告-周晨琳.docx', 'E:\\python\\citi-bike\\output\\reports'),
    (r'C:\Users\Lenovo\nyc_citibike\docs\调研报告-周晨琳.docx', 'nyc_citibike'),
    (r'C:\Users\Lenovo\Local Settings\Temp\citibike_run\citi-bike\docs\调研报告-周晨琳.docx', 'temp citibike_run'),
    (r'C:\Users\Lenovo\Local Settings\Temp\调研报告-周晨琳[1]_{7c8d88fa-5b91-49b2-b3dd-99367eadac26}.docx', 'temp dl1'),
    (r'C:\Users\Lenovo\Local Settings\Temp\调研报告-周晨琳[1]_{a449a9e6-6fca-4d7a-a56e-9583c204f916}.docx', 'temp dl2'),
    (r'C:\Users\Lenovo\Local Settings\Temp\调研报告-周晨琳_{aa41b0b1-2555-4884-9c1e-3a903422021a}.docx', 'temp dl3'),
    (r'C:\Users\Lenovo\WPS Cloud Files\.776968873\cachedata\00B54E9B799041A8B204B34F4CBEF8F2\调研报告-周晨琳.docx', 'wps cache1'),
    (r'C:\Users\Lenovo\WPS Cloud Files\.776968873\cachedata\31F18A504CCC493492E2295C84F487AE\调研报告-周晨琳.docx', 'wps cache2'),
    (r'C:\Users\Lenovo\WPS Cloud Files\.776968873\cachedata\9F020B9D8F93446C821EC173ED01EE3C\调研报告-周晨琳.docx', 'wps cache3'),
    (r'C:\Users\Lenovo\WPS Cloud Files\.776968873\cachedata\B6BECFED8C644E339DD67FD20C583426\调研报告-周晨琳.docx', 'wps cache4'),
]

print('== 直接副本覆盖 ==')
for dst, name in targets:
    try:
        if not os.path.isdir(os.path.dirname(dst)):
            os.makedirs(os.path.dirname(dst))
        shutil.copy2(desk, dst)
        ok = sha(desk) == sha(dst)
        print('  [%s] %s (%s)' % ('OK' if ok else '校验不一致!', name, os.path.getsize(dst)))
    except Exception as e:
        print('  [失败] %s : %s' % (name, e))

print()
print('== zip 1: 桌面提交包 ==')
# 用统一脚本重建（同步全部4个交付物）
os.system(r'python "E:\citi-bike\_archives\update_pkg.py"')

print()
print('== zip 2: C:\\Users\\Lenovo\\citi-bike-提交包.zip ==')
z2 = r'C:\Users\Lenovo\citi-bike-提交包.zip'
stage2 = r'E:\citi-bike\_archives\stage_zip2'
if os.path.isdir(stage2):
    shutil.rmtree(stage2)
os.makedirs(stage2)
with zipfile.ZipFile(z2) as z:
    z.extractall(stage2)
# 定位包内周晨琳报告
hit = None
for root, dirs, files in os.walk(stage2):
    for f in files:
        if '周晨琳' in f and f.endswith('.docx'):
            hit = os.path.join(root, f)
if hit:
    shutil.copy2(desk, hit)
    with zipfile.ZipFile(z2, 'w', zipfile.ZIP_DEFLATED) as z:
        for root, dirs, files in os.walk(stage2):
            for f in sorted(files):
                p = os.path.join(root, f)
                z.write(p, os.path.relpath(p, stage2))
    print('  已重建，包内周晨琳报告已更新')
    with zipfile.ZipFile(z2) as z:
        for i in z.infolist():
            print('    %10d  %s' % (i.file_size, i.filename))
    # 校验
    v2 = r'E:\citi-bike\_archives\verify_zip2'
    if os.path.isdir(v2):
        shutil.rmtree(v2)
    os.makedirs(v2)
    with zipfile.ZipFile(z2) as z:
        z.extractall(v2)
    for root, dirs, files in os.walk(v2):
        for f in files:
            if '周晨琳' in f:
                p = os.path.join(root, f)
                print('  包内校验:', '一致' if sha(desk) == sha(p) else '不一致!', sha(p))
    shutil.rmtree(v2)
else:
    print('  包内未找到周晨琳报告!')
shutil.rmtree(stage2)
print('完成')
