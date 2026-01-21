#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
特征提取示例

本示例展示如何使用 Alpha158 特征库和自定义特征，包括：
1. 使用 Alpha158 特征库
2. 创建数据集
3. 自定义特征构建

注意：运行本示例前，请确保已下载数据（参考 docs/02-数据准备.md）
"""

import qlib
from qlib.constant import REG_CN
from qlib.contrib.data.handler import Alpha158
from qlib.data.dataset import DatasetH


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

    # 1. 使用 Alpha158 特征库
    print("=" * 50)
    print("步骤2: 使用 Alpha158 特征库")
    print("=" * 50)

    try:
        # 创建 Alpha158 数据处理器
        handler = Alpha158(
            start_time='2020-01-01',
            end_time='2020-12-31',
            fit_start_time='2020-01-01',
            fit_end_time='2020-12-31',
            instruments='csi300'
        )

        # 获取处理后的数据
        data = handler.fetch()
        print(f"✅ Alpha158 特征提取成功")
        print(f"   数据形状: {data.shape}")
        print(f"   特征数量: {data.shape[1] - 1}")  # 减去标签列
        print(f"   样本数量: {data.shape[0]}")
        print(f"   前5个特征名: {list(data.columns[:5])}")
        print(f"   标签列名: {data.columns[-1]}\n")

    except Exception as e:
        print(f"❌ Alpha158 特征提取失败: {e}\n")

    # 2. 创建数据集
    print("=" * 50)
    print("步骤3: 创建数据集")
    print("=" * 50)

    try:
        # 重新创建 handler（因为 fetch() 后可能无法再次使用）
        handler = Alpha158(
            start_time='2020-01-01',
            end_time='2020-12-31',
            fit_start_time='2020-01-01',
            fit_end_time='2020-12-31',
            instruments='csi300'
        )

        # 创建数据集，划分训练/验证/测试集
        dataset = DatasetH(
            handler=handler,
            segments={
                'train': ('2020-01-01', '2020-08-31'),
                'valid': ('2020-09-01', '2020-10-31'),
                'test': ('2020-11-01', '2020-12-31')
            }
        )

        # 获取训练集
        train_data = dataset.prepare('train')
        print(f"✅ 数据集创建成功")
        print(f"   训练集形状: {train_data.shape}")
        print(f"   训练集特征数: {train_data.shape[1] - 1}")
        print(f"   训练集样本数: {train_data.shape[0]}\n")

        # 获取验证集
        valid_data = dataset.prepare('valid')
        print(f"   验证集形状: {valid_data.shape}")

        # 获取测试集
        test_data = dataset.prepare('test')
        print(f"   测试集形状: {test_data.shape}\n")

    except Exception as e:
        print(f"❌ 数据集创建失败: {e}\n")

    # 3. 自定义特征示例（使用 D.features）
    print("=" * 50)
    print("步骤4: 自定义特征构建示例")
    print("=" * 50)

    try:
        from qlib.data import D

        instruments = D.instruments(market='csi300')
        sample_stocks = list(instruments)[:5]

        # 构建自定义特征
        fields = [
            # 基础价格
            '$close',
            '$volume',

            # 收益率特征
            '$close / Ref($close, 1) - 1',          # 日收益率
            '$close / Ref($close, 5) - 1',           # 5日收益率

            # 移动平均特征
            'Mean($close, 5)',                      # 5日均价
            'Mean($close, 20)',                     # 20日均价

            # 价格位置特征
            '($close - Mean($close, 20)) / Mean($close, 20)',  # 价格相对位置

            # 波动率特征
            'Std($close, 5)',                       # 5日波动率

            # 成交量特征
            '$volume / Mean($volume, 5)',           # 成交量相对水平
        ]

        data = D.features(
            instruments=sample_stocks,
            fields=fields,
            start_time='2020-01-01',
            end_time='2020-01-31'
        )

        print(f"✅ 自定义特征构建成功")
        print(f"   数据形状: {data.shape}")
        print(f"   特征数量: {data.shape[1]}")
        print(f"   特征列表: {list(data.columns)}")
        print(f"\n   数据预览:\n{data.head()}\n")

    except Exception as e:
        print(f"❌ 自定义特征构建失败: {e}\n")

    print("=" * 50)
    print("✅ 特征提取示例完成！")
    print("=" * 50)
    print("\n提示：")
    print("- 更多特征工程方法请参考 docs/04-特征工程.md")
    print("- 下一步可以学习模型训练，参考 docs/05-模型训练.md")


if __name__ == '__main__':
    main()
