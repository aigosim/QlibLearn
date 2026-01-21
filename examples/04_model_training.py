#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LightGBM 模型训练示例

本示例展示如何使用 LightGBM 进行模型训练，包括：
1. 准备数据集
2. 创建 LightGBM 模型
3. 训练模型
4. 模型预测
5. 模型评估

注意：运行本示例前，请确保已下载数据（参考 docs/02-数据准备.md）
"""

import qlib
from qlib.constant import REG_CN
from qlib.contrib.model.gbdt import LGBModel
from qlib.data.dataset import DatasetH
from qlib.contrib.data.handler import Alpha158
import numpy as np
import pandas as pd


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

    # 1. 准备数据集
    print("=" * 50)
    print("步骤2: 准备数据集")
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

        # 查看数据集信息
        train_data = dataset.prepare('train')
        valid_data = dataset.prepare('valid')
        test_data = dataset.prepare('test')

        print(f"✅ 数据集准备成功")
        print(f"   训练集形状: {train_data.shape}")
        print(f"   验证集形状: {valid_data.shape}")
        print(f"   测试集形状: {test_data.shape}")
        print(f"   特征数量: {train_data.shape[1] - 1}\n")  # 减去标签列

    except Exception as e:
        print(f"❌ 数据集准备失败: {e}\n")
        return

    # 2. 创建模型
    print("=" * 50)
    print("步骤3: 创建 LightGBM 模型")
    print("=" * 50)

    try:
        model = LGBModel(
            loss='mse',                    # 损失函数：均方误差
            learning_rate=0.05,             # 学习率
            num_leaves=31,                  # 叶子节点数
            max_depth=5,                    # 树的最大深度
            num_threads=20                  # 线程数
        )
        print("✅ 模型创建成功\n")
    except Exception as e:
        print(f"❌ 模型创建失败: {e}\n")
        return

    # 3. 训练模型
    print("=" * 50)
    print("步骤4: 训练模型")
    print("=" * 50)

    try:
        print("开始训练模型（这可能需要几分钟）...")
        model.fit(dataset)
        print("✅ 模型训练完成\n")
    except Exception as e:
        print(f"❌ 模型训练失败: {e}\n")
        return

    # 4. 模型预测
    print("=" * 50)
    print("步骤5: 模型预测")
    print("=" * 50)

    try:
        pred = model.predict(test_data)
        print(f"✅ 模型预测成功")
        print(f"   预测结果形状: {pred.shape}")
        print(f"   预测结果预览:\n{pred.head(10)}\n")
    except Exception as e:
        print(f"❌ 模型预测失败: {e}\n")
        return

    # 5. 模型评估
    print("=" * 50)
    print("步骤6: 模型评估")
    print("=" * 50)

    try:
        label = test_data['label']

        # 计算相关系数（IC 值）
        correlation = pred.corr(label)
        print(f"✅ 模型评估完成")
        print(f"   预测值与真实值的相关系数 (IC): {correlation:.4f}")

        # 计算 RMSE
        rmse = np.sqrt(np.mean((pred - label)**2))
        print(f"   RMSE: {rmse:.4f}")

        # 计算 MAE
        mae = np.mean(np.abs(pred - label))
        print(f"   MAE: {mae:.4f}\n")

    except Exception as e:
        print(f"❌ 模型评估失败: {e}\n")

    print("=" * 50)
    print("✅ 模型训练示例完成！")
    print("=" * 50)
    print("\n提示：")
    print("- 更多模型训练方法请参考 docs/05-模型训练.md")
    print("- 下一步可以学习回测与评估，参考 docs/06-回测与评估.md")


if __name__ == '__main__':
    main()
