import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 初始化 DeepSeek 客户端
# 注意：DeepSeek API 完全兼容 OpenAI 的 Python SDK
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY", "your-api-key"), # 兼容之前填入的Key
    base_url="https://token-plan-cn.xiaomimimo.com/v1"
)
# MIMO 平台上配置的具体模型名称，如果没有在环境中指定，暂用 default
MODEL_NAME = os.getenv("MIMO_MODEL_NAME", "default")

def call_llm(system_prompt: str, user_prompt: str, json_mode: bool = False) -> str:
    """通用的 LLM 调用函数"""
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    
    response_format = {"type": "json_object"} if json_mode else {"type": "text"}
    
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        response_format=response_format,
        temperature=0.3 # 保持相对冷静和稳定
    )
    return response.choices[0].message.content

def analyze_jd_risk(jd_text: str, base_resume: str) -> str:
    """分析 JD 的排雷指数，融合了你的 Jargon Translator 和 Risk Analyzer"""
    system_prompt = f"""
    你是一个极其死板、冷酷的 AI 互联网职场生存精算师与劳动法顾问。你的任务是接收原始岗位文本，并深度读取用户的真实履历资产。你需要执行冷酷的交叉比对，输出一针见血的排雷报告。
    
    【真实履历资产】：
    {base_resume}
    
    # Evaluation Logic (严格分层推理)
    **第一层：最高优前置拦截（一票否决扫描）**
    扫描原文中是否出现“营销策划”、“用户体验(UX/UI)”、“产品原型”等C端属性核心词汇，如果有，必须判定为与用户B端重构基因冲突，锁定为【绝对劝退】。
    
    **第二层：能力与基因匹配（决定 Go/No-Go）**
    抛弃刻板印象，严格对比真实技术栈：
    - 绝对劝退（No-Go）：能力断层（如要求底层算法代码）、纯体力外包。
    - 强烈建议冲刺（Go）：痛点（如工作流编排、长文本解析）被履历完美覆盖。
    
    # Constraints
    1. 剥离情绪，保持冷酷。
    2. 【反幻觉硬隔离】：狙击的所有“暗坑”必须 100% 来源于 JD 原文。
    
    # Output Format (严格按以下 Markdown 格式输出)
    ### 🧭 跨行匹配度拦截
    **【结论】**：(🌟 S级核心潜力岗 / ✅ 强烈建议冲刺 / ⚠️ 建议谨慎评估 / 🚫 绝对劝退)
    **【判定依据】**：(说明原因)
    
    ### 💣 核心暗坑狙击
    * **暗坑 1**：“原文引用” -> 分析实质伤害
    *(最多3点，若无则输出：未检测到高危话术陷阱)*
    """
    
    return call_llm(system_prompt, jd_text)


def draft_resume(jd_text: str, base_resume: str, memory_context: str) -> str:
    """根据 JD、基础简历和用户偏好生成定制版简历"""
    system_prompt = f"""
    你是顶级的AI产品经理求职包装专家。
    
    {memory_context}
    
    # 核心任务
    将用户的真实履历，用 JD 偏好的业务术语（如：工作流编排、B端SOP重构等）进行重新包装，输出一份高度匹配ATS解析规则的在线简历和破冰话术。
    
    # 绝对红线
    1. 事实锁死：禁止捏造任何不在履历中的数据或能力。
    2. 严格遵守上述【系统长期记忆与用户偏好约束】中的所有规则。
    
    # 输出规范 (直接生成纯文本，不要使用Markdown代码块包裹)
    ### 💬 BOSS直聘破冰直聊话术
    您好！[结合JD提炼一句痛点]，[从知识库抽取对应的量化成果]，[结合岗位提一个探讨提问？]

    ---
    ### 📄 定制版工作经历与项目
    (按 JD 核心要求重新组织履历亮点，突出 Agent、Prompt 工程师、流程重构等关键词)
    """
    
    user_prompt = f"【基础简历】:\n{base_resume}\n\n【目标 JD】:\n{jd_text}"
    return call_llm(system_prompt, user_prompt)


def evaluate_resume(jd_text: str, drafted_resume: str, base_resume: str) -> dict:
    """多路自动化评测：让 LLM 做裁判"""
    system_prompt = """
    你是一个无情的简历打分系统 (ATS 模拟器)。
    请根据提供的【原版 JD】、【用户的真实底库简历】和【AI 生成的定制化简历】，分别从以下三个维度进行严格打分 (0-100分)：
    1. jd_coverage_score: JD 核心技能的覆盖率 (是否提到了JD要求的能力)。
    2. star_format_score: STAR 法则规范度 (是否都是 动作+数据结果，有没有废话)。
    3. hallucination_risk: 幻觉风险 (是否瞎编了基础简历里根本没有的技能，分数越高代表越安全，没有瞎编)。
    
    你必须以严格的 JSON 格式输出结果：
    {
        "jd_coverage_score": 85,
        "star_format_score": 90,
        "hallucination_risk": 95,
        "average_score": 90,
        "feedback_for_improvement": "具体的修改建议，指出哪里做的不够好，告诉生成器下次怎么改。"
    }
    """
    
    user_prompt = f"【原版 JD】:\n{jd_text}\n\n【真实底库简历】:\n{base_resume}\n\n【AI 生成的定制化简历】:\n{drafted_resume}"
    
    response = call_llm(system_prompt, user_prompt, json_mode=True)
    import json
    try:
        return json.loads(response)
    except:
        return {"average_score": 0, "feedback_for_improvement": "解析评分失败"}
