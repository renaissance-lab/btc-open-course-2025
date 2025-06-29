#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单十六进制解析器
输入 OP_PUSHBYTES 后面的十六进制内容，转换为可读文字
"""

def hex_to_text(hex_string):
    """将十六进制字符串转换为可读文字"""
    try:
        # 清理输入：移除空格、换行符等
        hex_string = hex_string.replace(' ', '').replace('\n', '').replace('\t', '')
        
        # 移除可能的0x前缀
        if hex_string.startswith('0x'):
            hex_string = hex_string[2:]
        
        # 确保是偶数长度
        if len(hex_string) % 2 != 0:
            return f"错误: 十六进制长度必须是偶数"
        
        # 转换为字节
        bytes_data = bytes.fromhex(hex_string)
        
        # 尝试UTF-8解码
        try:
            return bytes_data.decode('utf-8')
        except UnicodeDecodeError:
            # 如果UTF-8失败，尝试ASCII
            try:
                return bytes_data.decode('ascii')
            except UnicodeDecodeError:
                # 都失败了，返回原始字节表示
                return f"无法解码为文字，原始字节: {bytes_data}"
    
    except ValueError:
        return "错误: 无效的十六进制格式"
    except Exception as e:
        return f"错误: {str(e)}"

def main():
    print("=" * 50)
    print("简单十六进制解析器")
    print("输入 OP_PUSHBYTES 后面的十六进制内容")
    print("=" * 50)
    
    # 测试示例
    examples = [
        "746578742f706c61696e3b636861727365743d7574662d38",
        "68656c6c6f206161726f6e", 
        "6f7264"
    ]
    
    print("\n📝 示例解析:")
    for hex_data in examples:
        result = hex_to_text(hex_data)
        print(f"输入: {hex_data}")
        print(f"输出: {result}")
        print("-" * 30)
    
    print("\n🔧 交互式解析 (输入 'q' 退出):")
    
    while True:
        try:
            hex_input = input("\n请输入十六进制: ").strip()
            
            if hex_input.lower() in ['q', 'quit', 'exit']:
                print("再见!")
                break
            
            if not hex_input:
                continue
                
            result = hex_to_text(hex_input)
            print(f"结果: {result}")
            
        except KeyboardInterrupt:
            print("\n\n再见!")
            break

if __name__ == "__main__":
    main()