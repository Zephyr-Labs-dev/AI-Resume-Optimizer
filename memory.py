import json
import os
from typing import List, Dict

MEMORY_FILE = "user_memory.json"

def load_memory() -> Dict:
    """加载本地记忆文件，如果没有则创建一个空的"""
    if not os.path.exists(MEMORY_FILE):
        default_memory = {
            "avoid_words": ["赋能", "抓手", "闭环", "底层逻辑", "旨在", "打通", "链路", "组合拳"],
            "skill_constraints": "拒绝代码开发、无底层算法调优经验",
            "style_preferences": "必须使用“动宾结构”描述具体动作，例如：主导方案设计、协同排查网络",
            "user_feedback_history": []
        }
        save_memory(default_memory)
        return default_memory
    
    with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_memory(memory_data: Dict):
    """保存记忆到本地JSON文件"""
    with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(memory_data, f, ensure_ascii=False, indent=2)

def add_feedback(feedback_text: str):
    """将用户的最新反馈追加到记忆中"""
    memory = load_memory()
    memory["user_feedback_history"].append(feedback_text)
    save_memory(memory)

def get_memory_context() -> str:
    """获取格式化后的记忆上下文，用于注入到 Prompt 中"""
    memory = load_memory()
    context = "【系统长期记忆与用户偏好约束】\n"
    context += f"1. 绝对禁用的词汇 (雷区)：{', '.join(memory['avoid_words'])}\n"
    context += f"2. 用户的真实能力边界：{memory['skill_constraints']}\n"
    context += f"3. 行文风格偏好：{memory['style_preferences']}\n"
    
    if memory["user_feedback_history"]:
        context += "4. 用户历史修改反馈 (必须遵守)：\n"
        for idx, fb in enumerate(memory["user_feedback_history"][-5:]): # 只取最近5条
            context += f"   - {fb}\n"
            
    return context
