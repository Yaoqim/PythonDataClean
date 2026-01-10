# -*- coding: utf-8 -*-
"""
自动代码检查执行器

功能：
1. 在代码生成后自动执行检查
2. 生成检查报告并反馈
3. 记录检查历史
"""

from typing import Callable, Any, Dict, List
import functools
import os
from datetime import datetime

from src.langchain_integration.code_checker import CodeSpecificationChecker, CheckResult
from src.utils.logger import get_logger

logger = get_logger(__name__)


class AutoCodeChecker:
    """自动代码检查执行器"""
    
    def __init__(self):
        self.checker = CodeSpecificationChecker()
        self.check_history: List[Dict[str, Any]] = []
    
    def auto_check_decorator(self, func: Callable) -> Callable:
        """
        自动检查装饰器
        
        在函数执行后，如果生成了文件，则自动执行规范检查
        
        示例：
            @auto_checker.auto_check_decorator
            def generate_code(file_path):
                # 生成代码...
                return file_path
        """
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Dict[str, Any]:
            # 执行原函数
            result = func(*args, **kwargs)
            
            # 如果返回值是文件路径，执行检查
            if isinstance(result, str) and os.path.exists(result):
                return self._execute_check_and_report(result, result)
            
            # 如果返回字典包含file_path，执行检查
            elif isinstance(result, dict) and 'file_path' in result:
                file_path = result['file_path']
                check_result = self._execute_check_and_report(file_path, result)
                return check_result
            
            return result
        
        return wrapper
    
    def _execute_check_and_report(self, file_path: str, original_result: Any) -> Dict[str, Any]:
        """执行检查并生成报告"""
        logger.info(f"自动执行代码规范检查：{file_path}")
        
        # 执行检查
        check_result = self.checker.check_file(file_path)
        
        # 记录检查历史
        self.check_history.append({
            'timestamp': datetime.now().isoformat(),
            'file_path': file_path,
            'compliance_score': check_result.compliance_score,
            'errors': check_result.errors,
            'warnings': check_result.warnings,
            'passed': check_result.passed
        })
        
        # 打印报告
        report = self.checker.format_report(check_result)
        logger.info("\n" + report)
        
        # 返回检查结果和原始结果
        return {
            'original_result': original_result,
            'check_result': {
                'file_path': check_result.file_path,
                'compliance_score': check_result.compliance_score,
                'errors': check_result.errors,
                'warnings': check_result.warnings,
                'passed': check_result.passed,
                'total_issues': check_result.total_issues,
                'issues': [
                    {
                        'level': issue.level.value,
                        'rule': issue.rule,
                        'line_number': issue.line_number,
                        'message': issue.message,
                        'suggestion': issue.suggestion
                    }
                    for issue in check_result.issues
                ]
            }
        }
    
    def check_multiple_files(self, file_paths: List[str]) -> List[CheckResult]:
        """检查多个文件"""
        results = []
        for file_path in file_paths:
            result = self.checker.check_file(file_path)
            results.append(result)
            print(self.checker.format_report(result))
        
        return results
    
    def get_check_history(self) -> List[Dict[str, Any]]:
        """获取检查历史"""
        return self.check_history
    
    def print_summary(self) -> str:
        """打印检查汇总"""
        if not self.check_history:
            return "检查历史为空"
        
        total_checks = len(self.check_history)
        passed_checks = len([h for h in self.check_history if h['passed']])
        avg_score = sum([h['compliance_score'] for h in self.check_history]) / total_checks if total_checks > 0 else 0
        total_errors = sum([h['errors'] for h in self.check_history])
        total_warnings = sum([h['warnings'] for h in self.check_history])
        
        summary = f"""
检查汇总
{'='*50}
总检查数：{total_checks}
通过数：{passed_checks}
平均分数：{avg_score:.1f}/100
总错误数：{total_errors}
总警告数：{total_warnings}
通过率：{(passed_checks/total_checks)*100:.1f}%
{'='*50}
"""
        logger.info(summary)
        return summary


# 全局检查器实例
auto_checker = AutoCodeChecker()
