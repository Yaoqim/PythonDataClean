import json
import re
import os

def transform_json(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Regex to match "Name(Type)：Content"
    # Example: 车品一号专卖店星星(人工)：亲...
    agent_pattern = re.compile(r'^(.*?)\((人工|机器人)\)：(.*)$', re.DOTALL)

    for session in data:
        merchant_name = session.get('merchant_name', '')
        # 记录会话中出现的第一个客服名，作为会话级的 agent_name
        first_agent_name = None

        for msg in session.get('messages', []):
            sender = msg.get('sender', '')
            content = msg.get('content', '')
            
            # 如果发送者是商家（或者是我们之前处理过的占位符）
            if sender == merchant_name or "专卖店" in sender or "售后" in sender or "旗舰店" in sender:
                match = agent_pattern.match(content)
                if match:
                    agent_name = match.group(1).strip()
                    agent_type = match.group(2).strip()
                    actual_content = match.group(3).strip()
                    
                    msg['content'] = actual_content
                    msg['sender'] = agent_name  # 将具体客服名存入 sender
                    msg['agent_type'] = agent_type
                    
                    if not first_agent_name:
                        first_agent_name = agent_name
                
                # 无论是否匹配正则，如果 msg 中已有 agent_name（上个版本遗留），则清理掉
                if 'agent_name' in msg:
                    # 如果 sender 还是商户全称，尝试用已有的 agent_name 更新它
                    if msg['sender'] == merchant_name:
                        msg['sender'] = msg['agent_name']
                    del msg['agent_name']
                
                if not first_agent_name and msg.get('sender') != merchant_name:
                    first_agent_name = msg.get('sender')

        # 更新会话级 agent_name
        if first_agent_name:
            session['agent_name'] = first_agent_name

    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    transform_json('e:/workSpace/idea/PythonDataClean/data/temp/CUSTOMER_DIALOG_SIM_20260112_0001.json')
