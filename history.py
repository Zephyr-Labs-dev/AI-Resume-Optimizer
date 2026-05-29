import os
import json
import datetime

HISTORY_DIR = "history"

def init_history_dir():
    if not os.path.exists(HISTORY_DIR):
        os.makedirs(HISTORY_DIR)

def save_history(jd_text: str, channel: str, scores: dict, draft: str) -> str:
    """保存生成的记录，返回文件名"""
    init_history_dir()
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{channel}.json"
    filepath = os.path.join(HISTORY_DIR, filename)
    
    data = {
        "timestamp": timestamp,
        "channel": channel,
        "jd_text": jd_text,
        "scores": scores,
        "draft": draft
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        
    return filepath

def load_all_history() -> list:
    """加载所有历史记录的摘要信息，按时间倒序"""
    init_history_dir()
    records = []
    for f in os.listdir(HISTORY_DIR):
        if f.endswith('.json'):
            filepath = os.path.join(HISTORY_DIR, f)
            with open(filepath, 'r', encoding='utf-8') as file:
                try:
                    data = json.load(file)
                    # 截取JD前30个字作为标题预览
                    jd_preview = data.get("jd_text", "")[:30].replace("\n", " ") + "..."
                    records.append({
                        "filename": f,
                        "timestamp": data.get("timestamp"),
                        "channel": data.get("channel"),
                        "jd_preview": jd_preview,
                        "score": data.get("scores", {}).get("average_score", 0),
                        "filepath": filepath,
                        "data": data # 包含完整数据
                    })
                except Exception:
                    continue
                    
    # 按文件名（即时间戳）倒序
    records.sort(key=lambda x: x['filename'], reverse=True)
    return records
