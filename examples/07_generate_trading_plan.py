# -*- coding: utf-8 -*-
"""
交易计划生成脚本

功能：
1. 读取选股结果
2. 读取当前持仓
3. 计算目标持仓和调仓差额
4. 生成交易计划清单

使用方法：
    python 07_generate_trading_plan.py \
        --selection_file selection_result.csv \
        --positions_file current_positions.csv \
        --total_assets 1000000 \
        --cash_balance 50000 \
        --trade_date 2024-01-16 \
        --region cn \
        --output trading_plan_20240116.csv

文件格式说明：
1. 选股结果文件（CSV或文本格式）：
   - CSV格式：包含 stock_code 或 instrument 或 code 列
   - 文本格式：每行一个股票代码

2. 当前持仓文件（CSV格式）：
   stock_code,quantity,cost_price,current_price
   SH000001,10000,10.00,10.50
"""

import argparse
import csv
import sys
from datetime import datetime
import qlib
from qlib.constant import REG_CN, REG_US
from qlib.data import D


def read_selection_result(file_path):
    """
    读取选股结果文件

    支持格式：
    - CSV格式：股票代码列（如 stock_code 或 instrument）
    - 文本格式：每行一个股票代码
    """
    stocks = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # 尝试作为CSV读取
            try:
                reader = csv.DictReader(f)
                for row in reader:
                    # 尝试不同的列名
                    stock = row.get('stock_code') or row.get('instrument') or row.get('code')
                    if stock:
                        stocks.append(stock.strip())
            except:
                # 如果不是CSV，按文本文件读取
                f.seek(0)
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        stocks.append(line)
    except Exception as e:
        print(f"❌ 读取选股结果失败: {e}")
        sys.exit(1)

    return stocks


def read_current_positions(file_path):
    """
    读取当前持仓CSV文件

    CSV格式要求：
    stock_code,quantity,cost_price,current_price
    SH000001,10000,10.00,10.50
    """
    positions = {}
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                stock = row.get('stock_code') or row.get('code')
                if stock:
                    positions[stock.strip()] = {
                        'quantity': int(float(row.get('quantity', 0))),
                        'cost_price': float(row.get('cost_price', 0)),
                        'current_price': float(row.get('current_price', 0))
                    }
    except Exception as e:
        print(f"❌ 读取当前持仓失败: {e}")
        sys.exit(1)

    return positions


def get_stock_prices(stocks, provider_uri, region, trade_date):
    """
    查询股票当前价格

    参数:
        stocks: 股票代码列表
        provider_uri: Qlib数据路径
        region: 市场区域
        trade_date: 交易日期
    """
    qlib.init(provider_uri=provider_uri, region=region)
    prices = {}

    for stock in stocks:
        try:
            # 查询收盘价
            data = D.features(
                [stock],
                ['$close'],
                start_time=trade_date,
                end_time=trade_date
            )
            if not data.empty:
                price = data.iloc[0, 0]
                prices[stock] = float(price)
            else:
                print(f"⚠️ 无法获取 {stock} 的价格，请手动输入")
                prices[stock] = None
        except Exception as e:
            print(f"⚠️ 查询 {stock} 价格失败: {e}")
            prices[stock] = None

    return prices


def calculate_target_positions(total_assets, stocks, prices):
    """
    计算目标持仓

    参数:
        total_assets: 总资产
        stocks: 股票代码列表
        prices: 股票价格字典
    """
    n_stocks = len(stocks)
    if n_stocks == 0:
        return {}

    weight = 1.0 / n_stocks
    target_amount = total_assets * weight

    target_positions = {}
    for stock in stocks:
        price = prices.get(stock)
        if price is None or price <= 0:
            print(f"⚠️ {stock} 价格无效，跳过")
            continue

        # 计算目标数量（向下取整到100股）
        target_qty = int((target_amount / price) // 100) * 100
        actual_amount = target_qty * price

        target_positions[stock] = {
            'weight': weight,
            'target_amount': target_amount,
            'target_qty': target_qty,
            'actual_amount': actual_amount,
            'price': price
        }

    return target_positions


def calculate_rebalancing(target_positions, current_positions):
    """
    计算调仓差额

    参数:
        target_positions: 目标持仓字典
        current_positions: 当前持仓字典
    """
    rebalancing = {}

    # 处理目标持仓中的股票
    for stock, target in target_positions.items():
        current = current_positions.get(stock, {'quantity': 0})
        current_qty = current['quantity']
        target_qty = target['target_qty']

        diff = target_qty - current_qty
        rebalancing[stock] = {
            'target_qty': target_qty,
            'current_qty': current_qty,
            'diff': diff,
            'action': '买入' if diff > 0 else '卖出' if diff < 0 else '无需操作',
            'action_qty': abs(diff) if diff != 0 else 0,
            'price': target['price']
        }

    # 处理当前持仓中不在目标持仓的股票（需要清仓）
    for stock, current in current_positions.items():
        if stock not in target_positions:
            rebalancing[stock] = {
                'target_qty': 0,
                'current_qty': current['quantity'],
                'diff': -current['quantity'],
                'action': '卖出',
                'action_qty': current['quantity'],
                'price': current.get('current_price', 0)
            }

    return rebalancing


def generate_trading_plan(rebalancing, cash_balance):
    """
    生成交易计划

    参数:
        rebalancing: 调仓计算结果
        cash_balance: 现金余额
    """
    buy_list = []
    sell_list = []
    no_action_list = []

    for stock, info in rebalancing.items():
        if info['action'] == '买入':
            buy_list.append({
                'stock': stock,
                'quantity': info['action_qty'],
                'price': info['price'],
                'amount': info['action_qty'] * info['price']
            })
        elif info['action'] == '卖出':
            sell_list.append({
                'stock': stock,
                'quantity': info['action_qty'],
                'price': info['price'],
                'amount': info['action_qty'] * info['price']
            })
        else:
            no_action_list.append({
                'stock': stock,
                'target_qty': info['target_qty'],
                'current_qty': info['current_qty']
            })

    # 计算总金额
    total_buy_amount = sum(item['amount'] for item in buy_list)
    total_sell_amount = sum(item['amount'] for item in sell_list)

    # 资金检查
    available_cash = cash_balance + total_sell_amount - total_buy_amount

    return {
        'buy_list': buy_list,
        'sell_list': sell_list,
        'no_action_list': no_action_list,
        'total_buy_amount': total_buy_amount,
        'total_sell_amount': total_sell_amount,
        'available_cash': available_cash,
        'cash_balance': cash_balance
    }


def print_trading_plan(plan, trade_date):
    """
    打印交易计划清单
    """
    print("=" * 80)
    print(f"交易计划清单 - {trade_date}")
    print("=" * 80)

    # 卖出清单
    if plan['sell_list']:
        print("\n【卖出清单】")
        print(f"{'序号':<6} {'股票代码':<15} {'卖出数量':<12} {'当前价格':<12} {'预计金额':<15} {'备注':<10}")
        print("-" * 80)
        for idx, item in enumerate(plan['sell_list'], 1):
            remark = "清仓" if item['quantity'] >= 1000 else "减仓"
            print(f"{idx:<6} {item['stock']:<15} {item['quantity']:<12} "
                  f"{item['price']:<12.2f} {item['amount']:<15.2f} {remark:<10}")
        print(f"\n卖出合计: {plan['total_sell_amount']:,.2f} 元")
    else:
        print("\n【卖出清单】")
        print("无卖出操作")

    # 买入清单
    if plan['buy_list']:
        print("\n【买入清单】")
        print(f"{'序号':<6} {'股票代码':<15} {'买入数量':<12} {'当前价格':<12} {'预计金额':<15} {'备注':<10}")
        print("-" * 80)
        for idx, item in enumerate(plan['buy_list'], 1):
            remark = "新买入" if item['quantity'] >= 1000 else "加仓"
            print(f"{idx:<6} {item['stock']:<15} {item['quantity']:<12} "
                  f"{item['price']:<12.2f} {item['amount']:<15.2f} {remark:<10}")
        print(f"\n买入合计: {plan['total_buy_amount']:,.2f} 元")
    else:
        print("\n【买入清单】")
        print("无买入操作")

    # 无需操作清单
    if plan['no_action_list']:
        print("\n【无需操作清单】")
        print(f"{'股票代码':<15} {'目标数量':<12} {'当前数量':<12} {'说明':<20}")
        print("-" * 80)
        for item in plan['no_action_list']:
            print(f"{item['stock']:<15} {item['target_qty']:<12} "
                  f"{item['current_qty']:<12} {'持仓正确，无需调整':<20}")

    # 资金检查
    print("\n【资金检查】")
    print(f"现金余额: {plan['cash_balance']:,.2f} 元")
    print(f"卖出总金额: {plan['total_sell_amount']:,.2f} 元")
    print(f"买入总金额: {plan['total_buy_amount']:,.2f} 元")
    print(f"执行后可用资金: {plan['available_cash']:,.2f} 元")

    if plan['available_cash'] < 0:
        print("\n⚠️ 警告：资金不足！")
        print("建议：")
        print("  1. 先执行卖出操作，释放资金")
        print("  2. 减少买入数量")
        print("  3. 分批执行交易计划")
    else:
        print("\n✅ 资金充足，可以执行交易计划")

    print("\n" + "=" * 80)


def save_trading_plan(plan, output_file, trade_date):
    """
    保存交易计划到CSV文件
    """
    try:
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['交易计划清单', trade_date])
            writer.writerow([])

            # 卖出清单
            writer.writerow(['卖出清单'])
            writer.writerow(['序号', '股票代码', '卖出数量', '当前价格', '预计金额', '备注'])
            for idx, item in enumerate(plan['sell_list'], 1):
                remark = "清仓" if item['quantity'] >= 1000 else "减仓"
                writer.writerow([
                    idx, item['stock'], item['quantity'],
                    f"{item['price']:.2f}", f"{item['amount']:.2f}", remark
                ])
            writer.writerow(['卖出合计', '', '', '', f"{plan['total_sell_amount']:.2f}", ''])

            writer.writerow([])

            # 买入清单
            writer.writerow(['买入清单'])
            writer.writerow(['序号', '股票代码', '买入数量', '当前价格', '预计金额', '备注'])
            for idx, item in enumerate(plan['buy_list'], 1):
                remark = "新买入" if item['quantity'] >= 1000 else "加仓"
                writer.writerow([
                    idx, item['stock'], item['quantity'],
                    f"{item['price']:.2f}", f"{item['amount']:.2f}", remark
                ])
            writer.writerow(['买入合计', '', '', '', f"{plan['total_buy_amount']:.2f}", ''])

            writer.writerow([])

            # 资金检查
            writer.writerow(['资金检查'])
            writer.writerow(['项目', '金额'])
            writer.writerow(['现金余额', f"{plan['cash_balance']:.2f}"])
            writer.writerow(['卖出总金额', f"{plan['total_sell_amount']:.2f}"])
            writer.writerow(['买入总金额', f"{plan['total_buy_amount']:.2f}"])
            writer.writerow(['执行后可用资金', f"{plan['available_cash']:.2f}"])

        print(f"\n✅ 交易计划已保存到: {output_file}")
    except Exception as e:
        print(f"❌ 保存交易计划失败: {e}")


def main():
    parser = argparse.ArgumentParser(description='生成交易计划清单')
    parser.add_argument('--selection_file', type=str, required=True,
                        help='选股结果文件路径（CSV或文本格式）')
    parser.add_argument('--positions_file', type=str, required=True,
                        help='当前持仓CSV文件路径')
    parser.add_argument('--total_assets', type=float, required=True,
                        help='总资产（元）')
    parser.add_argument('--cash_balance', type=float, required=True,
                        help='现金余额（元）')
    parser.add_argument('--trade_date', type=str, required=True,
                        help='交易日期（YYYY-MM-DD）')
    parser.add_argument('--region', type=str, default='cn', choices=['cn', 'us'],
                        help='市场区域（cn=中国，us=美国）')
    parser.add_argument('--output', type=str, default='trading_plan.csv',
                        help='输出文件路径（默认：trading_plan.csv）')
    parser.add_argument('--provider_uri', type=str, default='~/.qlib/qlib_data/cn_data',
                        help='Qlib数据路径')

    args = parser.parse_args()

    # 初始化Qlib
    region = REG_CN if args.region == 'cn' else REG_US
    provider_uri = args.provider_uri
    if args.region == 'us':
        provider_uri = provider_uri.replace('cn_data', 'us_data')

    qlib.init(provider_uri=provider_uri, region=region)

    print("=" * 80)
    print("交易计划生成工具")
    print("=" * 80)

    # 1. 读取选股结果
    print("\n[1/6] 读取选股结果...")
    target_stocks = read_selection_result(args.selection_file)
    print(f"✅ 读取到 {len(target_stocks)} 只目标持仓股票")

    # 2. 读取当前持仓
    print("\n[2/6] 读取当前持仓...")
    current_positions = read_current_positions(args.positions_file)
    print(f"✅ 读取到 {len(current_positions)} 只当前持仓股票")

    # 3. 查询股票价格
    print("\n[3/6] 查询股票价格...")
    all_stocks = list(set(target_stocks + list(current_positions.keys())))
    prices = get_stock_prices(all_stocks, provider_uri, region, args.trade_date)
    print(f"✅ 查询到 {len([p for p in prices.values() if p is not None])} 只股票的价格")

    # 4. 计算目标持仓
    print("\n[4/6] 计算目标持仓...")
    target_positions = calculate_target_positions(
        args.total_assets, target_stocks, prices
    )
    print(f"✅ 计算出 {len(target_positions)} 只股票的目标持仓")

    # 5. 计算调仓差额
    print("\n[5/6] 计算调仓差额...")
    rebalancing = calculate_rebalancing(target_positions, current_positions)
    print(f"✅ 计算出调仓差额")

    # 6. 生成交易计划
    print("\n[6/6] 生成交易计划...")
    plan = generate_trading_plan(rebalancing, args.cash_balance)

    # 打印交易计划
    print_trading_plan(plan, args.trade_date)

    # 保存交易计划
    save_trading_plan(plan, args.output, args.trade_date)

    print("\n✅ 交易计划生成完成！")


if __name__ == '__main__':
    main()
