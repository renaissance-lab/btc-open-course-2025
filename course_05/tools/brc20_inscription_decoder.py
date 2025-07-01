#!/usr/bin/env python3
# BRC-20 Inscription 数据解码器

import json

def decode_brc20_hex(hex_data):
    """
    将 BRC-20 inscription 的 hex 数据解码为可读信息
    
    Args:
        hex_data (str): BRC-20 JSON 数据的十六进制字符串
    
    Returns:
        dict: 解码后的 BRC-20 信息
    """
    try:
        # 将 hex 转换为字符串
        json_str = bytes.fromhex(hex_data).decode('utf-8')
        print(f"📄 原始 JSON: {json_str}")
        
        # 解析 JSON
        brc20_data = json.loads(json_str)
        
        # 验证是否为 BRC-20 格式
        if brc20_data.get('p') != 'brc-20':
            print("⚠️  警告: 这不是标准的 BRC-20 数据")
        
        return brc20_data
        
    except ValueError as e:
        print(f"❌ Hex 解码错误: {e}")
        return None
    except json.JSONDecodeError as e:
        print(f"❌ JSON 解析错误: {e}")
        return None

def format_brc20_info(brc20_data):
    """
    格式化显示 BRC-20 信息
    
    Args:
        brc20_data (dict): BRC-20 数据字典
    """
    if not brc20_data:
        return
    
    print("\n🪙 BRC-20 代币信息:")
    print("=" * 40)
    
    # 基本信息
    protocol = brc20_data.get('p', 'unknown')
    operation = brc20_data.get('op', 'unknown')
    ticker = brc20_data.get('tick', 'unknown')
    
    print(f"📋 协议: {protocol}")
    print(f"🔧 操作: {operation}")
    print(f"🏷️  代币符号: {ticker.upper()}")
    
    # 根据操作类型显示不同信息
    if operation == 'deploy':
        max_supply = brc20_data.get('max', '0')
        mint_limit = brc20_data.get('lim', '0')
        
        print(f"📊 最大供应量: {format_number(max_supply)}")
        print(f"⚡ 单次 Mint 限制: {format_number(mint_limit)}")
        
        # 计算需要多少次 mint
        if max_supply != '0' and mint_limit != '0':
            total_mints = int(max_supply) // int(mint_limit)
            print(f"🔢 需要 Mint 次数: {total_mints:,}")
            
    elif operation == 'mint':
        amount = brc20_data.get('amt', '0')
        print(f"💰 Mint 数量: {format_number(amount)}")
        
    elif operation == 'transfer':
        amount = brc20_data.get('amt', '0')
        print(f"💸 转账数量: {format_number(amount)}")
    
    # 显示所有原始字段
    print(f"\n📋 完整数据:")
    for key, value in brc20_data.items():
        print(f"   {key}: {value}")

def format_number(num_str):
    """
    格式化数字显示，添加千分位分隔符
    """
    try:
        num = int(num_str)
        return f"{num:,}"
    except:
        return num_str

def main():
    # 测试数据
    test_hex = "7b2270223a226272632d3230222c226f70223a226465706c6f79222c227469636b223a226d697961222c226c696d223a2231303030222c226d6178223a223231303030303030227d"
    
    print("🔍 BRC-20 Inscription 解码器")
    print("=" * 50)
    print(f"🔤 输入 Hex: {test_hex}")
    
    # 解码数据
    brc20_info = decode_brc20_hex(test_hex)
    
    # 格式化显示
    format_brc20_info(brc20_info)
    
    print("\n" + "=" * 50)
    print("💡 使用方法:")
    print("   brc20_info = decode_brc20_hex('your_hex_data')")
    print("   format_brc20_info(brc20_info)")

if __name__ == "__main__":
    main()