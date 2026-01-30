#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据加载示例

本示例展示如何加载不同市场的数据，包括：
1. A 股数据加载
2. 美股数据加载
3. 不同股票池的数据加载

注意：运行本示例前，请确保已下载数据（参考 docs/02-数据准备.md）
"""

import qlib
from qlib.constant import REG_CN, REG_US
from qlib.data import D


def load_cn_data():
    """加载 A 股数据示例"""
    print("=" * 50)
    print("A 股数据加载示例")
    print("=" * 50)

    try:
        # 初始化 A 股数据
        qlib.init(provider_uri='~/.qlib/qlib_data/cn_data', region=REG_CN)
        print("✅ A 股数据初始化成功\n")

        # 获取不同的股票池
        print("1. CSI300 股票池:")
        instruments_300 = D.instruments(market='csi300')
        # 使用 list_instruments 获取股票列表（更高效）
        stocks_300_dict = D.list_instruments(instruments=instruments_300)
        stocks_300 = list(stocks_300_dict.keys())
        print(f"   股票数量（全部）: {len(stocks_300)}")
        print(f"   前5只股票: {stocks_300[:5]}\n")

        # 使用日期筛选获取特定时间段的股票
        print("   1.1. CSI300 股票池（带日期筛选）:")
        stocks_300_filtered_dict = D.list_instruments(
            instruments=instruments_300,
            start_time='2020-09-20',
            end_time='2020-09-25'
        )
        stocks_300_filtered = list(stocks_300_filtered_dict.keys())
        print(f"   股票数量（2020-09-20 至 2020-09-25）: {len(stocks_300_filtered)}")
        print(f"   前5只股票: {stocks_300_filtered[:5]}\n")

        print("2. CSI500 股票池:")
        try:
            instruments_500 = D.instruments(market='csi500')
            # 使用 list_instruments 获取股票列表（更高效，带日期筛选）
            stocks_500_dict = D.list_instruments(
                instruments=instruments_500,
                start_time='2020-01-01',
                end_time='2020-01-10'
            )
            stocks_500 = list(stocks_500_dict.keys())
            print(f"   股票数量（2020-01-01 至 2020-01-10）: {len(stocks_500)}")
            print(f"   前5只股票: {stocks_500[:5]}\n")
        except Exception as e:
            print(f"   ⚠️ CSI500 数据可能不存在: {e}\n")

        print("3. 全市场股票池:")
        try:
            instruments_all = D.instruments(market='all')
            # 使用 list_instruments 获取股票列表（更高效，带日期筛选）
            stocks_all_dict = D.list_instruments(
                instruments=instruments_all,
                start_time='2020-01-01',
                end_time='2020-01-10'
            )
            stocks_all = list(stocks_all_dict.keys())
            print(f"   股票数量（2020-01-01 至 2020-01-10）: {len(stocks_all)}")
            print(f"   前5只股票: {stocks_all[:5]}\n")
        except Exception as e:
            print(f"   ⚠️ 全市场数据可能不存在: {e}\n")

        # 查询数据
        print("4. 查询 CSI300 数据:")
        sample_stocks = list(stocks_300)[:3]
        data = D.features(
            instruments=sample_stocks,
            fields=['$close', '$volume'],
            start_time='2020-01-01',
            end_time='2020-01-10'
        )
        print(f"   数据形状: {data.shape}")
        print(f"   数据预览:\n{data.head()}\n")

    except Exception as e:
        print(f"❌ A 股数据加载失败: {e}")
        print("请检查数据路径是否正确，或参考 docs/02-数据准备.md 下载数据\n")


def load_us_data():
    """加载美股数据示例"""
    print("=" * 50)
    print("美股数据加载示例")
    print("=" * 50)

    try:
        # 初始化美股数据
        qlib.init(provider_uri='~/.qlib/qlib_data/us_data', region=REG_US)
        print("✅ 美股数据初始化成功\n")

        # 获取股票池
        print("1. 全市场股票池:")
        instruments_all = D.instruments(market='all')
        # 使用 list_instruments 获取股票列表（更高效，带日期筛选）
        stocks_all_dict = D.list_instruments(
            instruments=instruments_all,
            start_time='2020-01-01',
            end_time='2020-01-10'
        )
        stocks_all = list(stocks_all_dict.keys())
        print(f"   股票数量（2020-01-01 至 2020-01-10）: {len(stocks_all)}")
        print(f"   前5只股票: {stocks_all[:5]}\n")

        # 查询数据
        print("2. 查询美股数据:")
        sample_stocks = list(stocks_all)[:3]
        data = D.features(
            instruments=sample_stocks,
            fields=['$close', '$volume'],
            start_time='2020-01-01',
            end_time='2020-01-10'
        )
        print(f"   数据形状: {data.shape}")
        print(f"   数据预览:\n{data.head()}\n")

    except Exception as e:
        print(f"❌ 美股数据加载失败: {e}")
        print("请检查数据路径是否正确，或参考 docs/02-数据准备.md 下载数据\n")


def main():
    """主函数"""
    print("数据加载示例\n")

    # 加载 A 股数据
    load_cn_data()

    # 加载美股数据（如果已下载）
    print("\n" + "=" * 50)
    try:
        load_us_data()
    except Exception as e:
        print(f"⚠️ 美股数据未下载或加载失败: {e}")
        print("如需使用美股数据，请参考 docs/02-数据准备.md 下载\n")

    print("=" * 50)
    print("✅ 数据加载示例完成！")
    print("=" * 50)
    print("\n提示：")
    print("- 更多数据使用方法请参考 docs/03-基础使用.md")
    print("- 下一步可以学习特征工程，参考 docs/04-特征工程.md")


if __name__ == '__main__':
    main()
