"""
版权盾服务 - 数字指纹 + 零宽盲水印
"""

import hashlib
import re
import time

# 零宽字符映射
ZERO_WIDTH_CHARS = {
    '0': '\u200B',  # 零宽空格
    '1': '\u200C',  # 零宽非连接器
    '2': '\u200D',  # 零宽连接器
    '3': '\uFEFF',  # 零宽非换行符
}


def generate_copyright_fingerprint(content: str) -> str:
    """
    生成数字版权指纹 (SHA-256)
    """
    # 标准化内容（去除多余空白）
    normalized = re.sub(r'\s+', '', content)
    
    # 计算 SHA-256 哈希
    hash_obj = hashlib.sha256(normalized.encode('utf-8'))
    fingerprint = hash_obj.hexdigest()
    
    return fingerprint


def text_to_binary(text: str) -> str:
    """将文本转为二进制"""
    binary = ''
    for char in text:
        binary += format(ord(char), '08b')
    return binary


def binary_to_text(binary: str) -> str:
    """将二进制转回文本"""
    text = ''
    for i in range(0, len(binary), 8):
        byte = binary[i:i+8]
        if len(byte) == 8:
            text += chr(int(byte, 2))
    return text


def inject_watermark(content: str, user_id: str = "1") -> str:
    """
    注入零宽盲水印
    将用户ID编码后嵌入文本
    """
    if not content:
        return content
    
    # 将用户ID转为二进制
    user_binary = text_to_binary(user_id)
    
    # 在文本中每隔一个字符插入一个零宽字符
    result = []
    binary_idx = 0
    
    for char in content:
        result.append(char)
        # 每隔3个字符嵌入一个水印位
        if len(result) % 3 == 0 and binary_idx < len(user_binary):
            # 映射 0/1 到零宽字符
            bit = user_binary[binary_idx]
            result.append(ZERO_WIDTH_CHARS.get(bit, ''))
            binary_idx += 1
    
    return ''.join(result)


def extract_watermark(content: str) -> str:
    """
    提取零宽盲水印
    """
    # 提取所有零宽字符
    watermark_bits = ''
    
    for char in content:
        if char == ZERO_WIDTH_CHARS['0']:
            watermark_bits += '0'
        elif char == ZERO_WIDTH_CHARS['1']:
            watermark_bits += '1'
        elif char == ZERO_WIDTH_CHARS['2']:
            watermark_bits += '2'
        elif char == ZERO_WIDTH_CHARS['3']:
            watermark_bits += '3'
    
    # 二进制转文本
    if watermark_bits:
        try:
            user_id = binary_to_text(watermark_bits)
            return user_id
        except:
            return ""
    
    return ""


def verify_copyright(content: str, expected_fingerprint: str) -> bool:
    """
    验证版权指纹
    """
    actual_fingerprint = generate_copyright_fingerprint(content)
    return actual_fingerprint == expected_fingerprint


def trace_leak(suspicious_text: str, known_texts: list) -> dict:
    """
    溯源泄漏
    对比可疑文本与已知文本的水印
    """
    extracted = extract_watermark(suspicious_text)
    
    if not extracted:
        return {"matched": False, "reason": "无可识别水印"}
    
    # 检查是否匹配已知用户
    for text in known_texts:
        known_watermark = extract_watermark(text)
        if known_watermark == extracted:
            return {
                "matched": True,
                "source_user_id": extracted,
                "confidence": "high"
            }
    
    return {
        "matched": False,
        "extracted_id": extracted,
        "reason": "未匹配到已知来源"
    }


# 测试
if __name__ == "__main__":
    # 测试
    test_text = "这是一个测试内容，用于验证水印功能。"
    user = "user123"
    
    # 注入水印
    watermarked = inject_watermark(test_text, user)
    print("原文:", test_text)
    print("水印文本:", watermarked)
    
    # 提取水印
    extracted = extract_watermark(watermarked)
    print("提取的用户ID:", extracted)
    print("水印验证:", extracted == user)
    
    # 版权指纹
    fingerprint = generate_copyright_fingerprint(test_text)
    print("版权指纹:", fingerprint)