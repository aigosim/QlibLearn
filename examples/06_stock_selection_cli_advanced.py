#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
增强版命令行选股工具

本工具提供完整的选股功能，包括：
- 模型训练（可选）
- 模型预测
- 选股策略执行
- 回测评估（可选）

使用方法:
    python examples/06_stock_selection_cli_advanced.py \
        --start_date 2023-01-01 \
        --end_date 2023-12-31 \
        --topk 10 \
        --train_start 2020-01-01 \
        --train_end 2022-12-31
"""

import argparse
import sys
import pickle
import qlib
from qlib.constant import REG_CN, REG_US
from qlib.contrib.model.gbdt import LGBModel
from qlib.data.dataset import DatasetH
from qlib.contrib.data.handler import Alpha158
from qlib.contrib.strategy.strategy import TopkDropoutStrategy
from qlib.workflow.record_temp import PortAnaRecord


def train_model(provider_uri, region, market, train_start, train_end):
    """训练模型"""
    print("正在训练模型...")

    handler = Alpha158(
        start_time=train_start,
        end_time=train_end,
        fit_start_time=train_start,
        fit_end_time=train_end,
        instruments=market
    )

    dataset = DatasetH(
        handler=handler,
        segments={
            'train': (train_start, train_end)
        }
    )

    model = LGBModel(
        loss='mse',
        learning_rate=0.05,
        num_leaves=31,
        max_depth=5,
        num_threads=20
    )

    model.fit(dataset)
    print("✅ 模型训练完成")

    return model


def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(
        description='增强版命令行选股工具 - 包含模型预测和回测评估',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 训练模型并选股
  python %(prog)s --start_date 2023-01-01 --end_date 2023-12-31 \\
      --topk 10 --train_start 2020-01-01 --train_end 2022-12-31

  # 使用预训练模型选股
  python %(prog)s --start_date 2023-01-01 --end_date 2023-12-31 \\
      --topk 10 --model_path ./models/lgb_model.pkl

  # 选股并执行回测
  python %(prog)s --start_date 2023-01-01 --end_date 2023-12-31 \\
      --topk 10 --train_start 2020-01-01 --train_end 2022-12-31 \\
      --enable_backtest --initial_capital 100000000
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
        help='股票池，默认: csi300'
    )
    parser.add_argument(
        '--start_date',
        type=str,
        required=True,
        help='选股开始日期，格式: YYYY-MM-DD（必需）'
    )
    parser.add_argument(
        '--end_date',
        type=str,
        required=True,
        help='选股结束日期，格式: YYYY-MM-DD（必需）'
    )
    parser.add_argument(
        '--topk',
        type=int,
        default=10,
        help='选择股票数量，默认: 10'
    )
    parser.add_argument(
        '--train_start',
        type=str,
        default=None,
        help='模型训练开始日期，格式: YYYY-MM-DD（可选）'
    )
    parser.add_argument(
        '--train_end',
        type=str,
        default=None,
        help='模型训练结束日期，格式: YYYY-MM-DD（可选）'
    )
    parser.add_argument(
        '--model_path',
        type=str,
        default=None,
        help='预训练模型路径（可选）'
    )
    parser.add_argument(
        '--enable_backtest',
        action='store_true',
        help='是否启用回测（默认: False）'
    )
    parser.add_argument(
        '--initial_capital',
        type=float,
        default=100000000,
        help='回测初始资金，默认: 100000000（1亿）'
    )

    args = parser.parse_args()

    # 初始化 Qlib
    try:
        region = REG_CN if args.region == 'cn' else REG_US
        qlib.init(provider_uri=args.provider_uri, region=region)
        print(f"✅ Qlib 初始化成功（区域: {args.region}）\n")
    except Exception as e:
        print(f"❌ Qlib 初始化失败: {e}")
        sys.exit(1)

    # 加载或训练模型
    model = None
    if args.model_path:
        try:
            print(f"正在加载模型: {args.model_path}")
            with open(args.model_path, 'rb') as f:
                model = pickle.load(f)
            print("✅ 模型加载成功\n")
        except Exception as e:
            print(f"❌ 模型加载失败: {e}")
            sys.exit(1)
    elif args.train_start and args.train_end:
        try:
            model = train_model(
                args.provider_uri, args.region, args.market,
                args.train_start, args.train_end
            )
            print()
        except Exception as e:
            print(f"❌ 模型训练失败: {e}")
            sys.exit(1)
    else:
        print("❌ 错误: 必须提供 --model_path 或 --train_start 和 --train_end")
        sys.exit(1)

    # 生成预测信号
    try:
        print("正在生成预测信号...")
        handler = Alpha158(
            start_time=args.start_date,
            end_time=args.end_date,
            fit_start_time=args.start_date,
            fit_end_time=args.end_date,
            instruments=args.market
        )

        dataset = DatasetH(
            handler=handler,
            segments={
                'test': (args.start_date, args.end_date)
            }
        )

        test_data = dataset.prepare('test')
        pred = model.predict(test_data)
        print(f"✅ 预测信号生成成功，形状: {pred.shape}\n")
    except Exception as e:
        print(f"❌ 生成预测信号失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 选股（显示每日选股结果）
    try:
        print("=" * 60)
        print(f"选股结果 ({args.start_date} 至 {args.end_date})")
        print("=" * 60)

        # 按日期分组，显示每日 Top-K
        pred_df = pred.reset_index()
        pred_df.columns = ['instrument', 'datetime', 'score']

        # 获取每个日期的 Top-K
        dates = sorted(pred_df['datetime'].unique())[:5]  # 只显示前5个交易日

        for date in dates:
            date_data = pred_df[pred_df['datetime'] == date].sort_values('score', ascending=False)
            topk_stocks = date_data.head(args.topk)

            print(f"\n日期: {date}")
            print(f"{'排名':<6} {'股票代码':<15} {'预测分数':<15}")
            print("-" * 60)
            for idx, row in enumerate(topk_stocks.iterrows(), 1):
                print(f"{idx:<6} {row[1]['instrument']:<15} {row[1]['score']:>14.6f}")

        print("\n" + "=" * 60)

    except Exception as e:
        print(f"❌ 选股过程失败: {e}")
        import traceback
        traceback.print_exc()

    # 回测（如果启用）
    if args.enable_backtest:
        try:
            print("\n" + "=" * 60)
            print("执行回测")
            print("=" * 60)

            strategy_config = {
                'class': 'TopkDropoutStrategy',
                'module_path': 'qlib.contrib.strategy.strategy',
                'kwargs': {
                    'topk': args.topk,
                    'n_drop': max(1, args.topk // 10),
                    'signal': pred
                }
            }

            benchmark = 'SH000300' if args.region == 'cn' else '^GSPC'
            backtest_config = {
                'start_time': args.start_date,
                'end_time': args.end_date,
                'account': args.initial_capital,
                'benchmark': benchmark,
                'exchange_kwargs': {
                    'limit_threshold': 0.095,
                    'deal_price': 'close',
                    'open_cost': 0.0005,
                    'close_cost': 0.0015,
                    'min_cost': 5
                }
            }

            port_analysis_config = {
                'strategy': strategy_config,
                'backtest': backtest_config
            }

            print("开始回测（这可能需要几分钟）...")
            record = PortAnaRecord(**port_analysis_config)
            record.generate()

            report = record.load()
            print("\n回测结果:")
            print(f"  年化收益率: {report.get('return', 'N/A')}")
            print(f"  信息比率: {report.get('information_ratio', 'N/A')}")
            print(f"  最大回撤: {report.get('max_drawdown', 'N/A')}")

        except Exception as e:
            print(f"❌ 回测失败: {e}")
            import traceback
            traceback.print_exc()

    print("\n✅ 选股工具执行完成！")


if __name__ == '__main__':
    main()
