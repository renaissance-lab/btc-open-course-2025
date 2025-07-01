# ===================================
# 文件：Python 基础语法示例代码
# 作者：Aaron Zhang
# 日期：2024年
# 说明：演示 Python 基础语法
#      包括条件语句、循环和函数
# ===================================


def demo_if():
    """条件语句示例"""
    print("\n=== 条件语句 ===")
    age = 18
    
    # 简单的 if-else
    if age >= 18:
        print("你是成年人")
    else:
        print("你是未成年人")
    
    # if-elif-else
    score = 85
    if score >= 90:
        print("优秀")
    elif score >= 80:
        print("良好")
    elif score >= 60:
        print("及格")
    else:
        print("不及格")

def demo_loop():
    """循环语句示例"""
    print("\n=== 循环语句 ===")
    
    # for 循环
    print("For 循环示例:")
    for i in range(3):  # 0, 1, 2
        print(f"第 {i+1} 次循环")
    
    # 遍历列表
    fruits = ["苹果", "香蕉", "橙子"]
    for fruit in fruits:
        print(f"我喜欢吃 {fruit}")
    
    # while 循环
    print("\nWhile 循环示例:")
    count = 0
    while count < 3:
        print(f"count = {count}")
        count += 1

def calculate_sum(a, b):
    """计算两个数的和"""
    return a + b

def demo_function():
    """函数示例"""
    print("\n=== 函数 ===")
    
    # 调用带返回值的函数
    result = calculate_sum(5, 3)
    print(f"5 + 3 = {result}")
    
    # 默认参数
    def greet(name="世界"):
        print(f"你好, {name}!")
    
    greet()  # 使用默认参数
    greet("小明")  # 传入参数
    
    # 多返回值
    def get_min_max(numbers):
        return min(numbers), max(numbers)
    
    nums = [1, 3, 5, 7, 9]
    min_num, max_num = get_min_max(nums)
    print(f"最小值: {min_num}, 最大值: {max_num}")

if __name__ == "__main__":
    demo_if()
    demo_loop()
    demo_function()