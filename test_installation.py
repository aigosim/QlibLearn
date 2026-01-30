#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Qlib 安装验证脚本
"""

try:
    import qlib
    print(f"✅ Qlib 安装成功！版本: {qlib.__version__}")

    # 检查关键模块
    from qlib.constant import REG_CN, REG_US
    from qlib.data import D
    print("✅ 核心模块导入成功")

    print("\n🎉 安装验证通过！可以开始使用 Qlib 了。")

except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请检查安装是否正确")
except Exception as e:
    print(f"❌ 验证过程出错: {e}")