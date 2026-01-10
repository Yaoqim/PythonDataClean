# -*- coding: utf-8 -*-
"""
LangChain MCP 工作流集成

展示如何在代码生成工作流中集成自动规范检查
"""

from typing import Dict, Any, List
from src.langchain_integration.auto_checker import auto_checker
from src.utils.logger import get_logger

logger = get_logger(__name__)


class CodeGenerationWorkflow:
    """代码生成工作流，内置自动规范检查"""
    
    @staticmethod
    def generate_and_check(generator_func, *args, **kwargs) -> Dict[str, Any]:
        """
        生成代码并自动检查
        
        Args:
            generator_func: 代码生成函数
            *args, **kwargs: 传递给生成函数的参数
        
        Returns:
            包含生成结果和检查结果的字典
        
        示例：
            result = CodeGenerationWorkflow.generate_and_check(
                create_cleaner_code,
                business_type="EC_GOODS_PHONE"
            )
        """
        logger.info("开始代码生成工作流")
        
        # 执行代码生成
        generation_result = generator_func(*args, **kwargs)
        
        # 如果生成了文件，自动执行检查
        if isinstance(generation_result, dict) and 'file_path' in generation_result:
            file_path = generation_result['file_path']
            logger.info(f"代码生成完成，文件：{file_path}")
            
            # 执行自动检查
            check_result = auto_checker._execute_check_and_report(file_path, generation_result)
            
            # 返回完整结果
            return {
                'success': check_result['check_result']['passed'],
                'generation': generation_result,
                'check': check_result['check_result']
            }
        
        return {'success': False, 'error': '生成失败或无文件输出'}
    
    @staticmethod
    def batch_generate_and_check(generator_func, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        批量生成代码并检查
        
        Args:
            generator_func: 代码生成函数
            items: 生成参数列表
        
        Returns:
            包含所有生成和检查结果的汇总
        """
        logger.info(f"开始批量代码生成，共 {len(items)} 个")
        
        results = []
        for item in items:
            try:
                result = CodeGenerationWorkflow.generate_and_check(generator_func, **item)
                results.append(result)
            except Exception as e:
                logger.error(f"生成失败：{e}")
                results.append({'success': False, 'error': str(e)})
        
        # 生成汇总
        passed = len([r for r in results if r.get('success')])
        failed = len(results) - passed
        
        summary = {
            'total': len(results),
            'passed': passed,
            'failed': failed,
            'pass_rate': f"{(passed/len(results)*100):.1f}%" if results else "0%",
            'results': results
        }
        
        logger.info(f"批量生成完成：通过 {passed}，失败 {failed}")
        return summary


class CheckReportGenerator:
    """检查报告生成器"""
    
    @staticmethod
    def generate_html_report(check_results: List[Dict[str, Any]]) -> str:
        """生成HTML检查报告"""
        html = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>代码规范检查报告</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1000px; margin: 0 auto; background-color: white; padding: 20px; border-radius: 5px; }
        .header { border-bottom: 2px solid #333; padding-bottom: 10px; margin-bottom: 20px; }
        .summary { background-color: #f9f9f9; padding: 15px; border-left: 4px solid #4CAF50; margin-bottom: 20px; }
        .file-item { margin-bottom: 20px; border: 1px solid #ddd; padding: 15px; border-radius: 3px; }
        .passed { border-left: 4px solid #4CAF50; background-color: #f0f8f0; }
        .failed { border-left: 4px solid #f44336; background-color: #fef0f0; }
        .score { font-size: 24px; font-weight: bold; }
        .score.high { color: #4CAF50; }
        .score.medium { color: #ff9800; }
        .score.low { color: #f44336; }
        .issue { margin: 10px 0; padding: 10px; background-color: #fff3cd; border-left: 3px solid #ffc107; }
        .issue.error { background-color: #f8d7da; border-left-color: #f44336; }
        .issue.warning { background-color: #fff3cd; border-left-color: #ffc107; }
        .issue.info { background-color: #d1ecf1; border-left-color: #17a2b8; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; }
        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f5f5f5; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📋 代码规范检查报告</h1>
        </div>
"""
        
        # 汇总统计
        total_files = len(check_results)
        passed_files = len([r for r in check_results if r.get('passed')])
        total_issues = sum([r.get('total_issues', 0) for r in check_results])
        total_errors = sum([r.get('errors', 0) for r in check_results])
        
        html += f"""
        <div class="summary">
            <h2>✓ 检查汇总</h2>
            <table>
                <tr>
                    <th>总文件数</th><td>{total_files}</td>
                    <th>通过数</th><td>{passed_files}</td>
                    <th>通过率</th><td>{(passed_files/total_files*100):.1f}%</td>
                </tr>
                <tr>
                    <th>总问题数</th><td>{total_issues}</td>
                    <th>总错误数</th><td>{total_errors}</td>
                    <th>平均分数</th><td>{sum([r.get('compliance_score', 0) for r in check_results])/total_files:.1f}/100</td>
                </tr>
            </table>
        </div>
"""
        
        # 详细结果
        for result in check_results:
            status_class = "passed" if result.get('passed') else "failed"
            score = result.get('compliance_score', 0)
            score_class = "high" if score >= 80 else "medium" if score >= 60 else "low"
            
            html += f"""
        <div class="file-item {status_class}">
            <h3>{result.get('file_path', 'Unknown')}</h3>
            <div style="margin: 10px 0;">
                <span class="score {score_class}">{score:.0f}/100</span>
                <span style="margin-left: 20px;">
                    错误: {result.get('errors', 0)} | 
                    警告: {result.get('warnings', 0)} | 
                    问题: {result.get('total_issues', 0)}
                </span>
            </div>
"""
            
            # 显示问题
            issues = result.get('issues', [])
            if issues:
                for issue in issues[:10]:  # 只显示前10个问题
                    issue_class = issue.get('level', 'info').lower()
                    html += f"""
            <div class="issue {issue_class}">
                <strong>[{issue.get('rule')}]</strong> 第{issue.get('line_number')}行<br>
                问题：{issue.get('message')}<br>
                建议：{issue.get('suggestion')}
            </div>
"""
            else:
                html += '<div class="issue info">✓ 没有检测到问题</div>'
            
            html += "</div>"
        
        html += """
    </div>
</body>
</html>
"""
        return html
    
    @staticmethod
    def save_html_report(check_results: List[Dict[str, Any]], file_path: str) -> str:
        """保存HTML报告"""
        html = CheckReportGenerator.generate_html_report(check_results)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        logger.info(f"检查报告已保存到：{file_path}")
        return file_path


# 使用示例
if __name__ == '__main__':
    print("代码生成工作流集成示例")
    print("=" * 50)
    
    # 示例1：生成单个文件并检查
    print("\n示例1：生成单个文件并自动检查")
    print("-" * 50)
    
    # 示例2：批量生成并检查
    print("\n示例2：批量生成多个文件并检查")
    print("-" * 50)
    
    print("\n生成报告")
    print("-" * 50)
