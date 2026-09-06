# -*- coding: utf-8 -*-
"""重新打包提交材料：生成新代码.zip 并组装外层 [01]xxx.zip。"""
import os
import zipfile

BASE = r"E:\citi-bike"
DESKTOP = r"D:\OneDrive\Desktop\项目提交材料"
TMP = r"E:\citi-bike\_archives\repack"

# ---------- 1) 新代码.zip 文件清单（对齐旧包 + 新增 cleaning 与机器学习模块）----------
CODE_FILES = [
    "main.py",
    "config.py",
    "download_data.py",
    "requirements.txt",
    "requirements-optional.txt",
    "README.md",
    ".gitignore",
    "storage/preprocess.py",
    "storage/__init__.py",
    "cleaning/preprocess.py",
    "analysis/analysis.py",
    "analysis/__init__.py",
    "model/analyze.py",
    "model/__init__.py",
    "visualization/plots.py",
    "visualization/__init__.py",
    "docs/data_dict.md",
    "机器学习模块/src/ml.py",
    "机器学习模块/机器学习分析报告.md",
]

# ---------- 2) 外层 zip 条目：目标名 -> (源路径) ----------
OUTER_ITEMS = [
    ("代码.zip", os.path.join(TMP, "代码.zip")),
    ("小组期末报告.docx", os.path.join(DESKTOP, "期末报告-纽约公共自行车数据分析.docx")),
    ("答辩PPT.pptx", os.path.join(DESKTOP, "答辩PPT-纽约公共自行车数据分析.pptx")),
    ("调研报告/调研报告-周晨琳.docx", os.path.join(DESKTOP, "调研报告-周晨琳.docx")),
    ("调研报告/调研报告-陈嘉欣.docx", os.path.join(DESKTOP, "调研报告-陈嘉欣.docx")),
]

OUTER_ZIP = os.path.join(DESKTOP, "[01]周晨琳_陈嘉欣_张子千_童悦家_陈静萤_自行车.zip")
TMP_OUTER = os.path.join(TMP, "[01]周晨琳_陈嘉欣_张子千_童悦家_陈静萤_自行车.zip")


def make_code_zip():
    os.makedirs(TMP, exist_ok=True)
    out = os.path.join(TMP, "代码.zip")
    if os.path.exists(out):
        os.remove(out)
    missing = []
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        for rel in CODE_FILES:
            src = os.path.join(BASE, rel.replace("/", os.sep))
            if not os.path.exists(src):
                missing.append(rel)
                continue
            z.write(src, rel)
    print(f"[代码包] 已生成: {out}  ({os.path.getsize(out)/1024:.1f} KB, {len(CODE_FILES)-len(missing)} 个文件)")
    if missing:
        print(f"[代码包] 缺失: {missing}")
    return out


def make_outer_zip(code_zip):
    if os.path.exists(TMP_OUTER):
        os.remove(TMP_OUTER)
    missing = []
    with zipfile.ZipFile(TMP_OUTER, "w", zipfile.ZIP_DEFLATED) as z:
        for arc, src in OUTER_ITEMS:
            if not os.path.exists(src):
                missing.append(arc)
                continue
            z.write(src, arc)
    print(f"[外层包] 已生成: {TMP_OUTER}  ({os.path.getsize(TMP_OUTER)/1024:.1f} KB)")
    if missing:
        print(f"[外层包] 缺失: {missing}")
    return TMP_OUTER


if __name__ == "__main__":
    code_zip = make_code_zip()
    tmp_outer = make_outer_zip(code_zip)
    # 替换桌面旧包（先备份旧包）
    backup = os.path.join(DESKTOP, "[01]_旧包备份.zip")
    if os.path.exists(OUTER_ZIP) and not os.path.exists(backup):
        os.replace(OUTER_ZIP, backup)
        print(f"[备份] 旧包已备份为: {backup}")
    os.replace(tmp_outer, OUTER_ZIP)
    print(f"[完成] 新提交包已就位: {OUTER_ZIP}")
