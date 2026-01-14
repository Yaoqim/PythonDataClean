import os
import sys
from src.orchestrator.orchestrator import CleaningOrchestrator
from src.utils.logger import get_logger

logger = get_logger(__name__)

def test_json_flow():
    print("\n" + "="*50)
    print("Testing JSON Full Flow...")
    print("="*50)
    json_path = r'e:\workSpace\idea\PythonDataClean\data\temp\CUSTOMER_DIALOG_SIM_20260112_0001.json'
    result = CleaningOrchestrator.process_cleaning_task(json_path, enable_llm=False)
    print(f"Result: {result['success']}")
    if result['success']:
        print(f"Original Count: {result['original_count']}")
        print(f"Cleaned Count: {result['cleaned_count']}")
        print(f"Stored Count: {result['storage_result']['inserted_count']}")
    else:
        print(f"Error: {result.get('error')}")

def test_excel_flow():
    print("\n" + "="*50)
    print("Testing Excel Full Flow...")
    print("="*50)
    excel_path = r'e:\workSpace\idea\PythonDataClean\data\test\CUSTOMER_DIALOG_TEST.xlsx'
    result = CleaningOrchestrator.process_cleaning_task(excel_path, enable_llm=False)
    print(f"Result: {result['success']}")
    if result['success']:
        print(f"Original Count: {result['original_count']}")
        print(f"Cleaned Count: {result['cleaned_count']}")
        print(f"Stored Count: {result['storage_result']['inserted_count']}")
    else:
        print(f"Error: {result.get('error')}")

if __name__ == '__main__':
    # 设置模拟环境（如果需要）
    # os.environ['DB_NAME'] = 'aimerchanter_test'
    
    try:
        test_json_flow()
        test_excel_flow()
    except Exception as e:
        print(f"Unexpected error during testing: {e}")
        import traceback
        traceback.print_exc()
