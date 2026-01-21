#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
回测与评估示例

本示例展示如何进行策略回测和绩效评估，包括：
1. 准备模型和预测信号
2. 配置回测参数
3. 执行回测
4. 查看回测结果

注意：运行本示例前，请确保已下载数据（参考 docs/02-数据准备.md）
本示例需要较长时间运行，因为包含模型训练和回测
"""

import qlib
from qlib.constant import REG_CN
from qlib.contrib.model.gbdt import LGBModel
from qlib.data.dataset import DatasetH
from qlib.contrib.data.handler import Alpha158
from qlib.contrib.strategy.strategy import TopkDropoutStrategy
from qlib.workflow.record_temp import PortAnaRecord


def main():
    """主函数"""
    # 初始化 Qlib
    print("=" * 50)
    print("步骤1: 初始化 Qlib")
    print("=" * 50)

    try:
        qlib.init(provider_uri='~/.qlib/qlib_data/cn_data', region=REG_CN)
        print("✅ Qlib 初始化成功\n")
    except Exception as e:
        print(f"❌ Qlib 初始化失败: {e}")
        print("请检查数据路径是否正确，或参考 docs/02-数据准备.md 下载数据")
        return

    # 1. 准备数据和模型
    print("=" * 50)
    print("步骤2: 准备数据和模型")
    print("=" * 50)

    try:
        handler = Alpha158(
            start_time='2008-01-01',
            end_time='2020-12-31',
            fit_start_time='2008-01-01',
            fit_end_time='2020-12-31',
            instruments='csi300'
        )

        dataset = DatasetH(
            handler=handler,
            segments={
                'train': ('2008-01-01', '2014-12-31'),
                'valid': ('2015-01-01', '2016-12-31'),
                'test': ('2017-01-01', '2020-12-31')
            }
        )

        print("✅ 数据集准备成功")
        print("   开始训练模型（这可能需要几分钟）...\n")

        # 训练模型
        model = LGBModel(
            loss='mse',
            learning_rate=0.05,
            num_leaves=31,
            max_depth=5,
            num_threads=20
        )
        model.fit(dataset)
        print("✅ 模型训练完成\n")

        # 获取测试集预测
        test_data = dataset.prepare('test')
        pred = model.predict(test_data)
        print(f"✅ 预测信号生成成功")
        print(f"   预测信号形状: {pred.shape}\n")

    except Exception as e:
        print(f"❌ 数据和模型准备失败: {e}\n")
        return

    # 2. 配置回测
    print("=" * 50)
    print("步骤3: 配置回测")
    print("=" * 50)

    try:
        # 配置策略
        strategy_config = {
            'class': 'TopkDropoutStrategy',
            'module_path': 'qlib.contrib.strategy.strategy',
            'kwargs': {
                'topk': 50,           # 持仓 50 只股票
                'n_drop': 5,         # 每次至少换 5 只
                'signal': pred       # 预测信号
            }
        }

        # 配置回测参数
        backtest_config = {
            'start_time': '2017-01-01',
            'end_time': '2020-12-31',
            'account': 100000000,    # 初始资金 1 亿
            'benchmark': 'SH000300',  # 基准：沪深300
            'exchange_kwargs': {
                'limit_threshold': 0.095,  # 涨跌停限制 9.5%
                'deal_price': 'close',     # 以收盘价成交
                'open_cost': 0.0005,      # 买入佣金 0.05%
                'close_cost': 0.0015,      # 卖出佣金 0.15%
                'min_cost': 5              # 最小佣金 5 元
            }
        }

        port_analysis_config = {
            'strategy': strategy_config,
            'backtest': backtest_config
        }

        print("✅ 回测配置完成")
        print(f"   回测时间: {backtest_config['start_time']} 至 {backtest_config['end_time']}")
        print(f"   初始资金: {backtest_config['account']:,} 元")
        print(f"   基准指数: {backtest_config['benchmark']}")
        print(f"   持仓数量: {strategy_config['kwargs']['topk']} 只\n")

    except Exception as e:
        print(f"❌ 回测配置失败: {e}\n")
        return

    # 3. 执行回测
    print("=" * 50)
    print("步骤4: 执行回测")
    print("=" * 50)
    print("开始执行回测（这可能需要几分钟）...\n")

    try:
        record = PortAnaRecord(**port_analysis_config)
        record.generate()
        print("✅ 回测执行完成\n")
    except Exception as e:
        print(f"❌ 回测执行失败: {e}\n")
        print("提示：回测可能需要较长时间，请耐心等待")
        return

    # 4. 查看结果
    print("=" * 50)
    print("步骤5: 查看回测结果")
    print("=" * 50)

    try:
        report = record.load()

        print("✅ 回测结果:")
        print(f"   年化收益率: {report.get('return', 'N/A'):.2%}" if isinstance(report.get('return'), (int, float)) else f"   年化收益率: {report.get('return', 'N/A')}")
        print(f"   信息比率: {report.get('information_ratio', 'N/A'):.4f}" if isinstance(report.get('information_ratio'), (int, float)) else f"   信息比率: {report.get('information_ratio', 'N/A')}")
        print(f"   最大回撤: {report.get('max_drawdown', 'N/A'):.2%}" if isinstance(report.get('max_drawdown'), (int, float)) else f"   最大回撤: {report.get('max_drawdown', 'N/A')}")

        # 如果有其他指标，也打印出来
        print(f"\n   完整报告键: {list(report.keys())[:10]}...")  # 只显示前10个键

    except Exception as e:
        print(f"❌ 查看回测结果失败: {e}\n")
        print("提示：回测结果可能以不同格式存储，请查看 Qlib 文档")

    print("\n" + "=" * 50)
    print("✅ 回测示例完成！")
    print("=" * 50)
    print("\n提示：")
    print("- 更多回测方法请参考 docs/06-回测与评估.md")
    print("- 下一步可以学习选股策略，参考 docs/07-选股策略.md")


if __name__ == '__main__':
    main()
