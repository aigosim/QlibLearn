# Qlib 量化投资平台学习文档与示例

本项目提供微软 Qlib 量化投资平台的完整学习文档和示例代码，从最基础的安装配置开始，逐步深入到制作一个完整的选股工具。

## 📚 项目结构

```
qliblearner/
├── README.md                    # 项目说明（本文件）
├── requirements.txt             # Python 依赖包列表
├── docs/                        # 学习文档目录
│   ├── 01-安装与环境配置.md
│   ├── 02-数据准备.md
│   ├── 03-基础使用.md
│   ├── 04-特征工程.md
│   ├── 05-模型训练.md
│   ├── 06-回测与评估.md
│   ├── 07-选股策略.md
│   ├── 08-命令行选股工具.md
│   ├── 09-常见问题.md
│   ├── 10-每日选股执行方案.md
│   ├── 11-每日选股实盘方案.md
│   ├── 12-模型预测与选股原理.md
│   └── 13-进阶指南与未来展望.md
└── examples/                    # 示例代码目录
    ├── 01_basic_usage.py
    ├── 02_data_loading.py
    ├── 03_feature_extraction.py
    ├── 04_model_training.py
    ├── 05_backtest.py
    ├── 06_stock_selection_cli_basic.py      # 基础版选股工具
    ├── 06_stock_selection_cli_advanced.py   # 增强版选股工具
    └── configs/
        └── workflow_config_lightgbm_Alpha158.yaml
```

## 🚀 快速开始

> 💡 **提示**：以下是最简化的快速开始步骤。如果您是第一次使用或遇到问题，请查看 **[详细的安装与环境配置文档](docs/01-安装与环境配置.md)**，其中包含详细的步骤说明、常见问题解答和故障排查。

### 1. 环境准备

确保您的系统已安装 Python 3.8（推荐）或 Python 3.7/3.9。

> 📖 **详细说明**：查看 [01-安装与环境配置.md](docs/01-安装与环境配置.md#一python-版本要求)

### 2. 安装依赖

```bash
# 创建虚拟环境（推荐）
conda create -n qlib_env python=3.8
conda activate qlib_env

# 安装依赖包
pip install -r requirements.txt
```

> 📖 **详细说明**：查看 [01-安装与环境配置.md](docs/01-安装与环境配置.md#二创建虚拟环境强烈推荐) 和 [01-安装与环境配置.md](docs/01-安装与环境配置.md#三安装前置依赖)

### 3. 数据准备

下载 Qlib 官方数据（A股或美股）：

```bash
# 下载 A 股数据
python -m qlib.run.get_data qlib_data --target_dir ~/.qlib/qlib_data/cn_data --region cn

# 下载美股数据
python -m qlib.run.get_data qlib_data --target_dir ~/.qlib/qlib_data/us_data --region us
```

> 📖 **详细说明**：查看 [02-数据准备.md](docs/02-数据准备.md)

### 4. 运行示例

```bash
# 运行基础使用示例
python examples/01_basic_usage.py

# 运行数据加载示例
python examples/02_data_loading.py
```

> 📖 **遇到问题？** 查看 [09-常见问题.md](docs/09-常见问题.md)

## 📖 学习路径

按照以下顺序阅读文档，循序渐进学习 Qlib：

1. **[安装与环境配置](docs/01-安装与环境配置.md)** - 环境搭建和 Qlib 安装
2. **[数据准备](docs/02-数据准备.md)** - 下载和准备 A 股/美股数据
3. **[基础使用](docs/03-基础使用.md)** - Qlib 初始化和基础数据查询
4. **[特征工程](docs/04-特征工程.md)** - Alpha158 特征库和自定义特征
5. **[模型训练](docs/05-模型训练.md)** - LightGBM 模型训练流程
6. **[回测与评估](docs/06-回测与评估.md)** - 策略回测和绩效评估
7. **[选股策略](docs/07-选股策略.md)** - TopkDropoutStrategy 详解
8. **[命令行选股工具](docs/08-命令行选股工具.md)** - 选股工具使用说明
9. **[常见问题](docs/09-常见问题.md)** - 故障排查和问题解决
10. **[每日选股执行方案](docs/10-每日选股执行方案.md)** - 每日选股的完整执行方案（手动和半自动）
11. **[每日选股实盘方案](docs/11-每日选股实盘方案.md)** - 将选股结果用于实盘交易的完整方案
12. **[模型预测与选股原理](docs/12-模型预测与选股原理.md)** - 模型预测和选股的理论机制解析
13. **[进阶指南与未来展望](docs/13-进阶指南与未来展望.md)** - 进阶学习方向、实践建议和未来展望

## 💡 示例代码说明

所有示例代码都是完全独立的，可以直接运行：

- **01_basic_usage.py** - Qlib 基础使用，包括初始化和简单数据查询
- **02_data_loading.py** - 数据加载的不同方法
- **03_feature_extraction.py** - 特征提取和 Alpha158 使用
- **04_model_training.py** - LightGBM 模型训练完整流程
- **05_backtest.py** - 回测配置和执行
- **06_stock_selection_cli_basic.py** - 基础版命令行选股工具
- **06_stock_selection_cli_advanced.py** - 增强版命令行选股工具（包含模型预测和回测）

## 🛠️ 命令行选股工具

### 基础版本

简单的因子筛选选股工具：

```bash
python examples/06_stock_selection_cli_basic.py \
    --provider_uri ~/.qlib/qlib_data/cn_data \
    --market csi300 \
    --start_date 2023-01-01 \
    --end_date 2023-12-31 \
    --topk 10
```

### 增强版本

包含模型预测和回测评估的完整选股工具：

```bash
python examples/06_stock_selection_cli_advanced.py \
    --provider_uri ~/.qlib/qlib_data/cn_data \
    --market csi300 \
    --start_date 2023-01-01 \
    --end_date 2023-12-31 \
    --topk 10 \
    --train_start 2020-01-01 \
    --train_end 2022-12-31
```

## 📝 注意事项

1. **Python 版本**：推荐使用 Python 3.8，避免使用 Python 3.10+（可能存在兼容性问题）
2. **数据下载**：首次使用需要下载数据，A 股数据约 1-2GB，美股数据可能更大
3. **Windows 用户**：需要安装 Visual C++ 14.0 或更高版本的生成工具
4. **独立示例**：所有示例代码都是完全独立的，可以单独运行，不依赖其他示例

## 🔗 相关资源

- [Qlib 官方文档](https://qlib.readthedocs.io/)
- [Qlib GitHub 仓库](https://github.com/microsoft/qlib)
- [Qlib 官方示例](https://github.com/microsoft/qlib/tree/main/examples)

## 📄 许可证

本项目仅用于学习目的，遵循 Qlib 的开源许可证。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request 来改进本项目！
