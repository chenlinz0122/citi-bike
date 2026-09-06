import zipfile, hashlib, os, shutil

out = r'D:\OneDrive\Desktop\项目提交材料\[01]周晨琳_陈嘉欣_张子千_童悦家_陈静萤_自行车.zip'
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
    (r'D:\OneDrive\Desktop\项目提交材料\期末报告-纽约公共自行车数据分析.docx',
     os.path.join(verify, '小组期末报告.docx'), '报告'),
    (r'D:\OneDrive\Desktop\项目提交材料\答辩PPT-纽约公共自行车数据分析.pptx',
     os.path.join(verify, '答辩PPT.pptx'), 'PPT'),
]
all_ok = True
for src, dst, name in checks:
    a, b = sha(src), sha(dst)
    ok = a == b
    all_ok = all_ok and ok
    label = '一致' if ok else '不一致!'
    print(name + ': ' + label + '  ' + a)

shutil.rmtree(verify)
shutil.rmtree(r'E:\citi-bike\_archives\pkg_stage')
print('临时目录已清理')
print('全部一致' if all_ok else '存在不一致!')
