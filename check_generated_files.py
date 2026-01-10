# -*- coding: utf-8 -*-
"""快速验证生成的代码文件"""

import os
import re
from pathlib import Path

def check_file_encoding(file_path):
    """检查文件编码和基本规范"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        issues = []
        
        # 检查BOM
        if content.startswith('\ufeff'):
            issues.append("包含BOM标记")
        
        # 检查中文直接使用（而不是Unicode转义）
        has_chinese = bool(re.search(r'[\u4e00-\u9fff]', content))
        has_unicode_escape = bool(re.search(r'\\u[0-9a-fA-F]{4}', content))
        
        if has_unicode_escape and not has_chinese:
            issues.append("滥用Unicode转义")
        
        # 检查编码声明
        if not content.startswith('# -*- coding: utf-8 -*-'):
            issues.append("缺少UTF-8编码声明")
        
        # 基本统计
        lines = content.split('\n')
        docstrings = len(re.findall(r'"""', content))
        
        return {
            'file': file_path,
            'lines': len(lines),
            'encoding_ok': True,
            'has_chinese': has_chinese,
            'has_unicode_escape': has_unicode_escape,
            'has_docstring': docstrings > 0,
            'issues': issues
        }
    except Exception as e:
        return {
            'file': file_path,
            'error': str(e),
            'encoding_ok': False
        }

if __name__ == '__main__':
    print("\n" + "="*70)
    print("文件规范检查报告")
    print("="*70)
    
    files = [
        'src/file_service/aliyun_client.py',
        'src/file_service/file_validator.py',
        'src/file_service/file_utils.py',
    ]
    
    all_passed = True
    
    for file_path in files:
        full_path = os.path.join('e:\\workSpace\\idea\\PythonDataClean', file_path)
        result = check_file_encoding(full_path)
        
        print(f"\n📄 {file_path}")
        print("-" * 70)
        
        if 'error' in result:
            print(f"  ✗ 错误：{result['error']}")
            all_passed = False
        else:
            print(f"  ✓ 编码：UTF-8")
            print(f"  ✓ 行数：{result['lines']}")
            print(f"  ✓ 中文：{'支持' if result['has_chinese'] else '暂无'}")
            print(f"  ✓ 文档字符串：{'是' if result['has_docstring'] else '否'}")
            
            if result['issues']:
                print(f"  ⚠️  问题数：{len(result['issues'])}")
                for issue in result['issues']:
                    print(f"      - {issue}")
                all_passed = False
            else:
                print(f"  ✓ 规范检查：通过")
    
    print("\n" + "="*70)
    if all_passed:
        print("✓ 所有文件符合规范")
    else:
        print("✗ 存在规范问题，请查看上述报告")
    print("="*70 + "\n")
