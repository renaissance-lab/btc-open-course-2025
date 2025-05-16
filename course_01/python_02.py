# ===================================
# 文件：Python 和比特币类型示例代码
# 作者：Aaron Zhang
# 日期：2024年
# 说明：演示 Python 常用数据类型
#      以及比特币开发中的特殊类型
# ===================================
from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey, PublicKey
from bitcoinutils.script import Script
import hashlib
import json
from decimal import Decimal

def demo_python_types():
    # 1. 数字类型
    print("\n=== 数字类型 ===")
    integer = 42  # 整数
    float_num = 3.14  # 浮点数
  
    print(f"整数: {integer}, 类型: {type(integer)}")
    print(f"浮点数: {float_num}, 类型: {type(float_num)}")
  

    # 2. 字符串
    print("\n=== 字符串 ===")
    string = "Hello, Python!"
    print(f"字符串: {string}")
    print(f"长度: {len(string)}")
    print(f"大写: {string.upper()}")
    print(f"切片: {string[0:5]}")  # 获取前5个字符

    # 3. 列表（可变序列）
    print("\n=== 列表 ===")
    my_list = [1, "two", 3.0, [4, 5]]
    print(f"列表: {my_list}")
    my_list.append(6)  # 添加元素
    print(f"添加后: {my_list}")
    print(f"第一个元素: {my_list[0]}")
    print(f"列表长度: {len(my_list)}")


    # 4. 字典
    print("\n=== 字典 ===")
    my_dict = {
        "name": "Alice",
        "age": 25,
        "skills": ["Python", "JavaScript"]
    }
    print(f"字典: {my_dict}")
    print(f"姓名: {my_dict['name']}")
    my_dict["location"] = "Beijing"  # 添加新键值对
    print(f"添加后: {my_dict}")


    # 5. 布尔值
    print("\n=== 布尔值 ===")
    is_true = True
    is_false = False
    print(f"True and False: {is_true and is_false}")
    print(f"True or False: {is_true or is_false}")
    print(f"Not True: {not is_true}")

    # 6. None 类型
    print("\n=== None 类型 ===")
    nothing = None
    print(f"None 值: {nothing}")
    print(f"是否为 None: {nothing is None}")


if __name__ == "__main__":
    demo_python_types()
