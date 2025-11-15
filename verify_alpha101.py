#!/usr/bin/env python3
"""
Alpha101全部因子验证脚本
对比标准: alphas/alphas101.py (DolphinDB优化版)
验证目标: stocks-alpha-sdk/src/main/java/io/github/arkmsg/alpha/calculator/Alpha101Group*.java
"""

import re
import os

# 读取Python参考实现
with open('../alphas/alphas101.py', 'r', encoding='utf-8') as f:
    py_content = f.read()

# Java文件映射
java_files = {
    range(1, 21): 'src/main/java/io/github/arkmsg/alpha/calculator/Alpha101Group1.java',
    range(21, 41): 'src/main/java/io/github/arkmsg/alpha/calculator/Alpha101Group2.java',
    range(41, 61): 'src/main/java/io/github/arkmsg/alpha/calculator/Alpha101Group3.java',
    range(61, 81): 'src/main/java/io/github/arkmsg/alpha/calculator/Alpha101Group4.java',
    range(81, 102): 'src/main/java/io/github/arkmsg/alpha/calculator/Alpha101Group5.java',
}

def get_java_file(alpha_num):
    """获取Java文件路径"""
    for r, file in java_files.items():
        if alpha_num in r:
            return file
    return None

def extract_python_formula(alpha_num):
    """提取Python公式（从注释）"""
    pattern = rf'# Alpha#{alpha_num}\t (.+)'
    match = re.search(pattern, py_content)
    return match.group(1).strip() if match else None

def extract_python_code(alpha_num):
    """提取Python实现代码"""
    pattern = rf'def alpha{alpha_num:03d}\(self\):(.*?)(?=\n    def alpha|\n    #.*Alpha#[0-9]|\Z)'
    match = re.search(pattern, py_content, re.DOTALL)
    if match:
        code = match.group(1).strip()
        # 移除空行和注释
        lines = [line for line in code.split('\n') 
                if line.strip() and not line.strip().startswith('#')]
        return '\n'.join(lines)
    return None

def extract_java_formula(alpha_num, java_file):
    """提取Java公式（从注释）"""
    try:
        with open(java_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找注释中的公式
        pattern = rf'Alpha#{alpha_num}:\s*(.+?)(?:\n\s*\*/|\n\s*\*\s*\n)'
        match = re.search(pattern, content, re.DOTALL)
        if match:
            formula = match.group(1).strip()
            # 只取第一行（公式行）
            return formula.split('\n')[0].strip()
        return None
    except:
        return None

def check_alpha_status(alpha_num, java_file):
    """检查Alpha是否被跳过"""
    try:
        with open(java_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找case语句
        pattern = rf'case {alpha_num}:.*?(?:log\.warn|return 0\.0|SKIPPED)'
        if re.search(pattern, content, re.DOTALL | re.MULTILINE):
            # 提取原因
            reason_pattern = rf'case {alpha_num}:.*?log\.warn\("(.+?)"\)'
            reason_match = re.search(reason_pattern, content, re.DOTALL)
            if reason_match:
                return 'SKIPPED', reason_match.group(1)
            return 'SKIPPED', '未实现'
        
        # 检查是否有方法实现
        method_pattern = rf'private static Double alpha{alpha_num:03d}\('
        if re.search(method_pattern, content):
            return 'IMPLEMENTED', None
        
        return 'UNKNOWN', None
    except:
        return 'ERROR', None

# 生成验证报告
print("=" * 100)
print("Alpha101 全部因子验证报告".center(100))
print(f"参考源: alphas/alphas101.py (DolphinDB优化版)".center(100))
print("=" * 100)

results = {
    'implemented': [],
    'skipped': [],
    'mismatch': [],
    'missing': []
}

for i in range(1, 102):
    java_file = get_java_file(i)
    if not java_file:
        results['missing'].append(i)
        continue
    
    py_formula = extract_python_formula(i)
    py_code = extract_python_code(i)
    java_formula = extract_java_formula(i, java_file)
    status, reason = check_alpha_status(i, java_file)
    
    if status == 'SKIPPED':
        results['skipped'].append((i, reason))
        print(f"⚠️  Alpha#{i:3d}: SKIPPED - {reason}")
    elif status == 'IMPLEMENTED':
        # 检查公式是否匹配
        if py_formula and java_formula:
            # 简单的字符串相似度检查
            py_clean = re.sub(r'\s+', '', py_formula.lower())
            java_clean = re.sub(r'\s+', '', java_formula.lower())
            
            if py_clean == java_clean or py_clean in java_clean or java_clean in py_clean:
                results['implemented'].append(i)
                print(f"✅ Alpha#{i:3d}: 已实现且公式匹配")
            else:
                results['mismatch'].append(i)
                print(f"❌ Alpha#{i:3d}: 已实现但公式可能不匹配")
                if len(py_formula) < 100 and len(java_formula) < 100:
                    print(f"   Python: {py_formula}")
                    print(f"   Java:   {java_formula}")
        else:
            results['implemented'].append(i)
            print(f"✅ Alpha#{i:3d}: 已实现")
    else:
        results['missing'].append(i)
        print(f"❓ Alpha#{i:3d}: 未找到实现")
    
    # 每20个因子输出一次分隔线
    if i % 20 == 0:
        print("-" * 100)

# 输出统计
print("\n" + "=" * 100)
print("验证统计".center(100))
print("=" * 100)
print(f"✅ 已实现: {len(results['implemented'])} 个")
print(f"⚠️  已跳过: {len(results['skipped'])} 个")
print(f"❌ 公式不匹配: {len(results['mismatch'])} 个")
print(f"❓ 未找到: {len(results['missing'])} 个")
print(f"\n总计: {len(results['implemented']) + len(results['skipped'])} / 101 = {(len(results['implemented']) + len(results['skipped'])) / 101 * 100:.1f}%")

if results['skipped']:
    print(f"\n跳过的因子 ({len(results['skipped'])}个):")
    for alpha_num, reason in results['skipped']:
        print(f"  Alpha#{alpha_num}: {reason}")

if results['mismatch']:
    print(f"\n需要检查的因子 ({len(results['mismatch'])}个):")
    print(f"  {results['mismatch']}")

print("\n" + "=" * 100)
print("验证完成！".center(100))
print("=" * 100)

