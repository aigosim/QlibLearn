#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Qlib 基础使用示例

本示例展示 Qlib 的基本使用方法，包括：
1. Qlib 初始化
2. 获取交易日历
3. 获取股票池
4. 查询特征数据

注意：运行本示例前，请确保已下载数据（参考 docs/02-数据准备.md）
"""

import qlib
from qlib.constant import REG_CN
from qlib.data import D


def main():
    """主函数"""
    # 1. 初始化 Qlib
    print("=" * 50)
    print("步骤1: 初始化 Qlib")
    print("=" * 50)

    try:
        qlib.init(
            provider_uri='~/.qlib/qlib_data/cn_data',  # 数据路径
            region=REG_CN  # 市场区域：A 股
        )
        print("✅ Qlib 初始化成功\n")
    except Exception as e:
        print(f"❌ Qlib 初始化失败: {e}")
        print("请检查数据路径是否正确，或参考 docs/02-数据准备.md 下载数据")
        return

    # 2. 获取交易日历
    print("=" * 50)
    print("步骤2: 获取交易日历")
    print("=" * 50)

    try:
        calendar = D.calendar(start_time='2020-01-01', end_time='2020-12-31')
        print(f"✅ 交易日历获取成功")
        print(f"   2020年交易日数量: {len(calendar)}")
        print(f"   第一个交易日: {calendar[0]}")
        print(f"   最后一个交易日: {calendar[-1]}\n")
    except Exception as e:
        print(f"❌ 获取交易日历失败: {e}\n")

    # 3. 获取股票池
    print("=" * 50)
    print("步骤3: 获取股票池")
    print("=" * 50)

    try:
        instruments = D.instruments(market='csi300')
        print(f"✅ 股票池获取成功")
        print(f"   CSI300 股票数量: {len(instruments)}")
        print(f"   前5只股票: {list(instruments)[:5]}\n")
    except Exception as e:
        print(f"❌ 获取股票池失败: {e}\n")

    # 4. 获取特征数据
    print("=" * 50)
    print("步骤4: 获取特征数据")
    print("=" * 50)

    try:
        # 获取前3只股票的数据
        instruments = D.instruments(market='csi300')
        sample_stocks = list(instruments)[:3]

        # 查询收盘价和成交量
        data = D.features(
            instruments=sample_stocks,
            fields=['$close', '$volume'],  # 字段列表
            start_time='2020-01-01',
            end_time='2020-01-10'  # 只查询前10个交易日
        )

        print(f"✅ 特征数据获取成功")
        print(f"   数据形状: {data.shape}")
        print(f"   数据列: {list(data.columns)}")
        print(f"\n   数据预览:")
        print(data.head(10))
        print()
    except Exception as e:
        print(f"❌ 获取特征数据失败: {e}\n")

    print("=" * 50)
    print("✅ 基础使用示例完成！")
    print("=" * 50)
    print("\n提示：")
    print("- 更多使用方法请参考 docs/03-基础使用.md")
    print("- 下一步可以学习特征工程，参考 docs/04-特征工程.md")


if __name__ == '__main__':
    main()
