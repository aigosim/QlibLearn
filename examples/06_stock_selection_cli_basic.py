#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
基础版命令行选股工具

本工具提供简单的因子筛选选股功能，根据指定的因子条件选择股票。

使用方法:
    python examples/06_stock_selection_cli_basic.py \
        --provider_uri ~/.qlib/qlib_data/cn_data \
        --market csi300 \
        --start_date 2023-01-01 \
        --end_date 2023-12-31 \
        --topk 10
"""

import argparse
import sys
import qlib
from qlib.constant import REG_CN, REG_US
from qlib.data import D


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='基础版命令行选股工具 - 简单的因子筛选选股',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # A 股 CSI300 选股
  python %(prog)s --market csi300 --start_date 2023-01-01 --end_date 2023-12-31 --topk 10

  # 美股选股
  python %(prog)s --provider_uri ~/.qlib/qlib_data/us_data --region us \\
      --market all --start_date 2023-01-01 --end_date 2023-12-31 --topk 20
        """
    )

    parser.add_argument(
        '--provider_uri',
        type=str,
        default='~/.qlib/qlib_data/cn_data',
        help='数据路径（默认: ~/.qlib/qlib_data/cn_data）'
    )
    parser.add_argument(
        '--region',
        type=str,
        choices=['cn', 'us'],
        default='cn',
        help='市场区域: cn (A股) 或 us (美股)，默认: cn'
    )
    parser.add_argument(
        '--market',
        type=str,
        default='csi300',
        help='股票池，A股可选: csi300, csi500, all 等，默认: csi300'
    )
    parser.add_argument(
        '--start_date',
        type=str,
        required=True,
        help='开始日期，格式: YYYY-MM-DD（必需）'
    )
    parser.add_argument(
        '--end_date',
        type=str,
        required=True,
        help='结束日期，格式: YYYY-MM-DD（必需）'
    )
    parser.add_argument(
        '--topk',
        type=int,
        default=10,
        help='选择股票数量，默认: 10'
    )

    args = parser.parse_args()

    # 初始化 Qlib
    try:
        region = REG_CN if args.region == 'cn' else REG_US
        qlib.init(provider_uri=args.provider_uri, region=region)
        print(f"✅ Qlib 初始化成功（区域: {args.region}）\n")
    except Exception as e:
        print(f"❌ Qlib 初始化失败: {e}")
        print("请检查数据路径是否正确，或参考 docs/02-数据准备.md 下载数据")
        sys.exit(1)

    # 获取股票池
    try:
        instruments = D.instruments(market=args.market)
        print(f"✅ 股票池获取成功: {args.market}，共 {len(instruments)} 只股票\n")
    except Exception as e:
        print(f"❌ 获取股票池失败: {e}")
        sys.exit(1)

    # 计算因子（使用简单的收益率因子作为示例）
    try:
        print(f"正在计算因子（{args.start_date} 至 {args.end_date}）...")

        # 使用5日收益率作为选股因子
        factor_field = '($close - Ref($close, 5)) / Ref($close, 5)'

        # 获取因子数据
        factor_data = D.features(
            instruments=instruments,
            fields=[factor_field],
            start_time=args.start_date,
            end_time=args.end_date
        )

        # 计算平均因子值（跨时间平均）
        factor_mean = factor_data.groupby(level='instrument').mean()
        factor_mean.columns = ['factor_value']

        # 排序并选择 Top-K
        factor_sorted = factor_mean.sort_values('factor_value', ascending=False)
        selected_stocks = factor_sorted.head(args.topk)

        print(f"✅ 选股完成\n")

        # 输出结果
        print("=" * 60)
        print(f"选股结果 ({args.start_date} 至 {args.end_date})")
        print("=" * 60)
        print(f"{'排名':<6} {'股票代码':<15} {'因子值':<15}")
        print("-" * 60)

        for idx, (stock, row) in enumerate(selected_stocks.iterrows(), 1):
            print(f"{idx:<6} {stock:<15} {row['factor_value']:>14.6f}")

        print("=" * 60)
        print(f"\n共选择 {len(selected_stocks)} 只股票")

    except Exception as e:
        print(f"❌ 选股过程失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
