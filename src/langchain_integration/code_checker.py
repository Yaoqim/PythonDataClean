# -*- coding: utf-8 -*-
"""
LangChain MCP 代码规范检查工具

功能：
1. 编码规范检查
2. 命名规范检查  
3. 代码结构检查
4. 逻辑错误检查
5. 功能完整性检查（修复而非删除原则）
"""

from typing import Dict, List, Any, Tuple
import re
import os
from dataclasses import dataclass
from enum import Enum

from src.utils.logger import get_logger

logger = get_logger(__name__)


class CheckLevel(Enum):
    """检查级别"""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class CodeIssue:
    """代码问题"""
    level: CheckLevel
    rule: str
    line_number: int
    message: str
    suggestion: str


@dataclass
class CheckResult:
    """检查结果"""
    file_path: str
    total_issues: int
    errors: int
    warnings: int
    issues: List[CodeIssue]
    compliance_score: float
    passed: bool


class CodeSpecificationChecker:
    """代码规范检查器"""
    
    def __init__(self):
        self.naming_rules = {
            "class_name": r"^[A-Z][a-zA-Z0-9]*$",
            "function_name": r"^[a-z_][a-z0-9_]*$",
            "constant_name": r"^[A-Z_][A-Z0-9_]*$",
            "variable_name": r"^[a-z_][a-z0-9_]*$",
        }
    
    def check_file(self, file_path: str) -> CheckResult:
        """检查单个文件"""
        logger.info(f"开始检查文件：{file_path}")
        
        if not os.path.exists(file_path):
            return CheckResult(
                file_path=file_path,
                total_issues=1,
                errors=1,
                warnings=0,
                issues=[CodeIssue(
                    level=CheckLevel.ERROR,
                    rule="file_not_found",
                    line_number=0,
                    message=f"文件不存在",
                    suggestion=f"检查文件路径是否正确"
                )],
                compliance_score=0.0,
                passed=False
            )
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception as e:
            logger.error(f"读取文件失败：{e}")
            return CheckResult(
                file_path=file_path,
                total_issues=1,
                errors=1,
                warnings=0,
                issues=[CodeIssue(
                    level=CheckLevel.ERROR,
                    rule="file_read_error",
                    line_number=0,
                    message=f"文件读取错误",
                    suggestion="检查文件编码或权限"
                )],
                compliance_score=0.0,
                passed=False
            )
        
        issues = []
        issues.extend(self._check_encoding(content))
        issues.extend(self._check_naming(lines))
        issues.extend(self._check_imports(lines))
        issues.extend(self._check_docstrings(lines))
        issues.extend(self._check_functionality_completeness(lines, content))
        issues.extend(self._check_fix_not_bypass_principle(lines, content))
        
        errors = len([i for i in issues if i.level == CheckLevel.ERROR])
        warnings = len([i for i in issues if i.level == CheckLevel.WARNING])
        
        compliance_score = max(0, 100 - (errors * 10 + warnings * 3))
        passed = errors == 0
        
        result = CheckResult(
            file_path=file_path,
            total_issues=len(issues),
            errors=errors,
            warnings=warnings,
            issues=issues,
            compliance_score=compliance_score,
            passed=passed
        )
        
        logger.info(f"检查完成：{file_path}，合规分数：{compliance_score:.0f}，状态：{'通过' if passed else '失败'}")
        return result
    
    def _check_encoding(self, content: str) -> List[CodeIssue]:
        """检查编码规范"""
        issues = []
        
        if content.startswith('\ufeff'):
            issues.append(CodeIssue(
                level=CheckLevel.ERROR,
                rule="bom_forbidden",
                line_number=0,
                message="文件包含BOM标记",
                suggestion="移除文件开头的BOM标记"
            ))
        
        if re.search(r'\\u[0-9a-fA-F]{4}', content) and not re.search(r'u"', content):
            count = len(re.findall(r'\\u[0-9a-fA-F]{4}', content))
            if count > 5:
                issues.append(CodeIssue(
                    level=CheckLevel.WARNING,
                    rule="avoid_unicode_escape",
                    line_number=0,
                    message=f"检测到 {count} 处Unicode转义",
                    suggestion="应直接使用中文，避免滥用Unicode转义"
                ))
        
        return issues
    
    def _check_naming(self, lines: List[str]) -> List[CodeIssue]:
        """检查命名规范"""
        issues = []
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
                continue
            
            # 检查类定义
            class_match = re.search(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', line)
            if class_match:
                class_name = class_match.group(1)
                if not re.match(self.naming_rules["class_name"], class_name):
                    issues.append(CodeIssue(
                        level=CheckLevel.WARNING,
                        rule="class_naming",
                        line_number=line_num,
                        message=f"类名 '{class_name}' 应使用PascalCase",
                        suggestion=f"改为 '{class_name[0].upper() + class_name[1:]}'"
                    ))
            
            # 检查函数定义
            func_match = re.search(r'def\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', line)
            if func_match:
                func_name = func_match.group(1)
                if not re.match(self.naming_rules["function_name"], func_name):
                    if func_name[0].isupper():
                        issues.append(CodeIssue(
                            level=CheckLevel.WARNING,
                            rule="function_naming",
                            line_number=line_num,
                            message=f"函数名 '{func_name}' 应使用snake_case",
                            suggestion=f"改为小写形式"
                        ))
        
        return issues
    
    def _check_imports(self, lines: List[str]) -> List[CodeIssue]:
        """检查导入规范"""
        issues = []
        
        # 检查是否有未使用的导入
        for line_num, line in enumerate(lines, 1):
            if line.strip().startswith('import ') or line.strip().startswith('from '):
                # 提取导入的模块/名称
                match = re.search(r'(?:from|import)\s+([a-zA-Z0-9_.]+)', line)
                if match:
                    module = match.group(1)
                    # 简单检查是否在代码中使用
                    content = '\n'.join(lines)
                    if module not in content[len('\n'.join(lines[:line_num])):]:
                        pass  # 可选：检查未使用的导入
        
        return issues
    
    def _check_docstrings(self, lines: List[str]) -> List[CodeIssue]:
        """检查文档字符串"""
        issues = []
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # 检查函数定义后是否有docstring
            if stripped.startswith('def '):
                if line_num < len(lines):
                    next_line = lines[line_num].strip()
                    if not (next_line.startswith('"""') or next_line.startswith("'''")):
                        issues.append(CodeIssue(
                            level=CheckLevel.INFO,
                            rule="missing_docstring",
                            line_number=line_num,
                            message="函数缺少文档字符串",
                            suggestion='在函数定义后添加 """...""" 文档字符串'
                        ))
        
        return issues
    
    def _check_functionality_completeness(self, lines: List[str], content: str) -> List[CodeIssue]:
        """
        检查功能完整性
        
        识别以下反模式：
        1. 过度简化的数据结构（跳过字段以避免处理复杂性）
        2. 删除表/字段而不是修复问题
        3. 空实现或TODO函数
        """
        issues = []
        
        # 检查空实现或不完整的函数
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # 检查TODO/FIXME注释（表示不完整的实现）
            if 'TODO' in line or 'FIXME' in line or 'XXX' in line:
                issues.append(CodeIssue(
                    level=CheckLevel.WARNING,
                    rule="incomplete_implementation",
                    line_number=line_num,
                    message="检测到未完成的实现标记",
                    suggestion="应该完成该功能，而不是留下TODO"
                ))
            
            # 检查 pass 语句（空实现）
            if stripped == 'pass':
                issues.append(CodeIssue(
                    level=CheckLevel.WARNING,
                    rule="empty_implementation",
                    line_number=line_num,
                    message="检测到空实现（仅有 pass 语句）",
                    suggestion="应该实现完整的函数逻辑，而不是使用 pass"
                ))
        
        return issues
    
    def _check_fix_not_bypass_principle(self, lines: List[str], content: str) -> List[CodeIssue]:
        """
        检查"修复而非删除/绕过"原则
        
        核心原则：当功能无法完成时，应该修复根本问题，而不是：
        1. 删除功能或跳过必要检查
        2. 修改数据结构以避免问题
        3. 注释掉关键业务逻辑
        4. 简化功能要求
        """
        issues = []
        
        for line_num, line in enumerate(lines, 1):
            stripped = line.strip()
            
            # 检查是否有注释掉的关键业务逻辑
            if stripped.startswith('#') and any(keyword in stripped.lower() for keyword in
                ['check', 'validate', 'clean', 'transform', 'verify', 'filter', 'sanitize']):
                issues.append(CodeIssue(
                    level=CheckLevel.WARNING,
                    rule="commented_business_logic",
                    line_number=line_num,
                    message="检测到被注释的业务逻辑",
                    suggestion="应该修复该逻辑使其正常工作，而不是注释掉"
                ))
            
            # 检查禁用验证的代码
            if any(pattern in line for pattern in ['if False:', 'if not True:', 'disabled', 'skip_validation']):
                issues.append(CodeIssue(
                    level=CheckLevel.WARNING,
                    rule="disabled_validation",
                    line_number=line_num,
                    message="检测到被禁用的数据验证",
                    suggestion="应该修复验证逻辑，使其正常工作，而不是禁用它"
                ))
            
            # 检查过度简化的结构定义（表示可能在规避问题）
            if 'CREATE TABLE' in line.upper():
                # 查找该表的完整定义范围
                table_lines = []
                for i in range(line_num - 1, min(line_num + 100, len(lines))):
                    table_lines.append(lines[i])
                    if ';' in lines[i]:
                        break
                
                table_def = '\n'.join(table_lines)
                # 统计字段数量
                field_count = sum(1 for t in table_lines if any(
                    keyword in t.upper() for keyword in 
                    ['VARCHAR', 'INT', 'DECIMAL', 'DATE', 'DATETIME', 'LONGTEXT', 'BOOLEAN', 'JSON']
                ))
                
                # 如果表定义过于简单（少于3个字段），可能是过度简化
                if 0 < field_count < 3:
                    issues.append(CodeIssue(
                        level=CheckLevel.INFO,
                        rule="oversimplified_schema",
                        line_number=line_num,
                        message=f"表结构过于简化（仅 {field_count} 个字段）",
                        suggestion="检查是否为了规避复杂问题而简化了表结构。应使用完整的业务字段定义"
                    ))
        
        return issues
    
    def format_report(self, result: CheckResult) -> str:
        """格式化检查报告"""
        report = []
        report.append("=" * 60)
        report.append("代码规范检查报告")
        report.append("=" * 60)
        report.append(f"文件：{result.file_path}")
        report.append(f"状态：{'✓ 通过' if result.passed else '✗ 失败'}")
        report.append(f"合规分数：{result.compliance_score:.0f}/100")
        report.append(f"问题总数：{result.total_issues} (错误: {result.errors}, 警告: {result.warnings})")
        report.append("")
        
        if result.issues:
            report.append("问题列表：")
            report.append("-" * 60)
            for issue in result.issues:
                level_symbol = "❌" if issue.level == CheckLevel.ERROR else "⚠️" if issue.level == CheckLevel.WARNING else "ℹ️"
                report.append(f"{level_symbol} [{issue.rule}] 第{issue.line_number}行")
                report.append(f"   问题：{issue.message}")
                report.append(f"   建议：{issue.suggestion}")
                report.append("")
        else:
            report.append("✓ 检查通过，代码符合规范")
        
        report.append("=" * 60)
        return "\n".join(report)
