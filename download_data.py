# -*- coding: utf-8 -*-
"""
download_data.py —— 数据下载脚本（组长负责）
================================================
把 Citi Bike 官方原始骑行数据下载到 data/raw/ 目录，供后续清洗使用。

用 法：
    python download_data.py                         # 下载 config.DEFAULT_MONTH 对应月份
    python download_data.py --month 202508          # 下载指定月份 2025-08
    python download_data.py --month 202508 --force  # 强制重新下载

输 出：
    data/raw/{period}-citibike-tripdata.csv         # 合并后的原始 CSV

说 明：
    - 官方页面：https://www.citibikenyc.com/system-data
    - 实际服务器：https://s3.amazonaws.com/tripdata/
    - 官方说明：小于 60 秒的行程已剔除；大月份压缩包内会拆成多个 CSV，
      本脚本会自动合并为一份（保留第 1 个文件的表头）。
"""

import argparse
import glob
import os
import shutil
import sys
import urllib.request
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import config

BASE_URL = "https://s3.amazonaws.com/tripdata/"


# ----------------------------------------------------------------------
# 候选下载地址：官方命名随发布略有变化，按优先级依次尝试
# ----------------------------------------------------------------------
def candidate_urls(period):
    return [
        f"{BASE_URL}{period}-citibike-tripdata.csv.zip",
        f"{BASE_URL}{period}-citibike-tripdata.zip",
        f"{BASE_URL}{period}-citibike-tripdata.csv",
    ]


def _download(url, dest):
    """下载单个文件；若已存在且未强制，则跳过。"""
    if not config.FORCE_DOWNLOAD and os.path.exists(dest) and os.path.getsize(dest) > 0:
        print(f"[下载] 已存在，跳过: {os.path.basename(dest)}")
        return
    print(f"[下载] {url} -> {os.path.basename(dest)}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 nyc-citibike"})
    with urllib.request.urlopen(req, timeout=config.DOWNLOAD_TIMEOUT) as resp:
        with open(dest, "wb") as f:
            shutil.copyfileobj(resp, f, length=1024 * 512)
    print(f"[下载] 完成 {os.path.getsize(dest) / 1024 / 1024:.1f} MB")
def _merge_csvs(csv_files, out_path):
    """把压缩包内的多个 CSV 合并为一份（大月份拆分场景）。"""
    import pandas as pd

    frames = [pd.read_csv(c) for c in csv_files]
    merged = pd.concat(frames, ignore_index=True)
    merged.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"[合并] {len(frames)} 个分片 -> {len(merged):,} 行 -> {os.path.basename(out_path)}")


def _line_count(path):
    """粗略统计行数（不含表头）。"""
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        n = sum(1 for _ in f)
    return max(n - 1, 0)


def _process_archive(archive, period):
    """解压合并一个压缩包/CSV 到 data/raw/{period}-citibike-tripdata.csv，返回(路径,行数)。"""
    out_path = os.path.join(config.RAW_DIR, f"{period}-citibike-tripdata.csv")

    if archive.lower().endswith(".zip"):
        extract_dir = os.path.join(config.RAW_DIR, f"_unzip_{period}")
        os.makedirs(extract_dir, exist_ok=True)
        with zipfile.ZipFile(archive) as z:
            z.extractall(extract_dir)
        csv_files = glob.glob(os.path.join(extract_dir, "*.csv"))
        if not csv_files:
            raise RuntimeError(f"[解压] 压缩包内未找到 .csv: {archive}")
        _merge_csvs(csv_files, out_path)
        shutil.rmtree(extract_dir, ignore_errors=True)
        return out_path, _line_count(out_path)

    # 已是单个 CSV：直接采用/改名
    if os.path.abspath(archive) != os.path.abspath(out_path):
        os.replace(archive, out_path)
    return out_path, _line_count(out_path)


def download_period(period):
    """
    获取并处理指定月份原始数据，返回 (csv 绝对路径, 行数)。

    数据源优先级：
      1. 本机已下载好的官方 zip（匹配 config.DEFAULT_MONTH 命名）
      2. 网络下载（s3.amazonaws.com/tripdata/）
    """
    os.makedirs(config.RAW_DIR, exist_ok=True)
    out_path = os.path.join(config.RAW_DIR, f"{period}-citibike-tripdata.csv")

    # 已存在且未强制，直接复用
    if not config.FORCE_DOWNLOAD and os.path.exists(out_path) and os.path.getsize(out_path) > 0:
        print(f"[下载] 已存在合并结果，跳过: {out_path}")
        return out_path, _line_count(out_path)

    # 1) 优先使用本机已下载的官方 zip
    for local in config.LOCAL_ZIP_PATHS:
        if os.path.exists(local) and f"{period}-citibike-tripdata" in os.path.basename(local):
            print(f"[下载] 使用本机压缩包: {local}")
            return _process_archive(local, period)

    # 2) 兜底：网络下载
    archive = None
    for url in candidate_urls(period):
        dest = os.path.join(config.RAW_DIR, os.path.basename(url))
        try:
            _download(url, dest)
            archive = dest
            break
        except Exception as e:
            print(f"[下载] 失败({url}): {e}")
            if os.path.exists(dest):
                os.remove(dest)
    if archive is None:
        raise RuntimeError(f"[下载] 所有候选地址均失败: {candidate_urls(period)}")

    return _process_archive(archive, period)


def main():
    p = argparse.ArgumentParser(description="Citi Bike 官方数据下载脚本")
    p.add_argument("--month", default=None,
                   help="下载某月数据，格式 YYYYMM，例如 202508；缺省用 config.DEFAULT_MONTH")
    p.add_argument("--force", action="store_true", help="强制重新下载（覆盖已有文件）")
    args = p.parse_args()

    if args.force:
        config.FORCE_DOWNLOAD = True
    period = args.month or config.DEFAULT_MONTH

    print(f"\n[== 下载 Citi Bike 数据：{period} ==]")
    path, n = download_period(period)
    print("\n[下载完成]")
    print(f"  数据文件: {path}")
    print(f"  记录行数: 约 {n:,} 行")


if __name__ == "__main__":
    main()