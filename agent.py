import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(override=True)

# 初始化 MIMO 客户端（兼容 OpenAI 协议）
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY", "your-api-key"),
    base_url="https://token-plan-cn.xiaomimimo.com/v1"
)
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
        temperature=0.3
    )
    return response.choices[0].message.content

def analyze_jd_risk(jd_text: str, base_resume: str) -> str:
    """分析 JD 的排雷指数，融合了 Jargon Translator 和 Risk Analyzer"""
    system_prompt = f"""
    你是一个极其死板、冷酷的 AI 互联网职场生存精算师与劳动法顾问。你的任务是接收原始岗位文本，并深度读取用户的真实履历资产。你需要执行冷酷的交叉比对，输出一针见血的排雷报告。
    
    【真实履历资产】：
    {base_resume}
    
    # Evaluation Logic (严格分层推理)
    **第一层：最高优前置拦截（一票否决扫描）**
    扫描原文中是否出现"营销策划"、"用户体验(UX/UI)"、"产品原型"等C端属性核心词汇，如果有，必须判定为与用户B端重构基因冲突，锁定为【绝对劝退】。
    
    **第二层：能力与基因匹配（决定 Go/No-Go）**
    抛弃刻板印象，严格对比真实技术栈：
    - 绝对劝退（No-Go）：能力断层（如要求底层算法代码）、纯体力外包。
    - 强烈建议冲刺（Go）：痛点（如工作流编排、长文本解析）被履历完美覆盖。
    
    # Constraints
    1. 剥离情绪，保持冷酷。
    2. 【反幻觉硬隔离】：狙击的所有"暗坑"必须 100% 来源于 JD 原文。
    
    # Output Format (严格按以下 Markdown 格式输出)
    ### 🧭 跨行匹配度拦截
    **【结论】**：(🌟 S级核心潜力岗 / ✅ 强烈建议冲刺 / ⚠️ 建议谨慎评估 / 🚫 绝对劝退)
    **【判定依据】**：(说明原因)
    
    ### 💣 核心暗坑狙击
    * **暗坑 1**："原文引用" -> 分析实质伤害
    *(最多3点，若无则输出：未检测到高危话术陷阱)*
    """
    
    return call_llm(system_prompt, jd_text)


def draft_resume(jd_text: str, base_resume: str, memory_context: str, channel: str = "both") -> str:
    """根据 JD、基础简历、用户偏好和投递渠道生成定制版简历"""
    
    # 根据渠道构建不同的输出策略
    if channel == "boss":
        channel_strategy = """
    # 投递渠道：Boss直聘
    Boss直聘的核心机制是"推荐算法曝光 + 破冰话术转化"。HR平均只花3-5秒扫一眼你的在线简历卡片。
    
    ## 输出策略
    1. 【破冰话术】严格遵循“三段式”结构（总计80字以内）：
       - 明确意向（约10字）：明确表明求职的具体岗位。
       - 核心卖点（40-60字）：提取与JD最贴合的竞争力。公式为：工作年限/背景 + 核心技能/资源 + 数据化业绩。
       - 行动呼唤（约10字）：引导查看简历或请求面试。
    2. 【在线简历定制内容】包含个人优势、工作经历和项目经历的定制：
       - "个人优势"：提炼3段式短文（约200字），强调整体方案落地能力。
       - "工作经历"：按"业绩"和"内容"分段，必须高密度命中JD关键词。
       - "项目经历"：聚焦与JD最相关的项目，突出你的具体角色和量化成果。
    3. 【求职意向标签】输出6个与JD高度匹配的技能标签。
"""
    elif channel == "official":
        channel_strategy = """
    # 投递渠道：大厂官网/小程序
    大厂（字节、腾讯、阿里、百度等）的自研招聘系统有初级AI筛选机制，核心逻辑是"关键词命中率 + 经历结构化解析"。
    
    ## 输出策略
    1. 【关键词覆盖】是最高优先级。必须确保JD中出现的每一个核心技能词（如：Agent、RAG、Prompt Engineering、工作流编排）都在简历中至少出现1次，且嵌入到具体的项目经历中（而非堆砌在技能栏）。
    2. 【结构化经历】大厂系统会解析"STAR"结构，所以每段经历必须严格遵循：
       - Situation（背景）：1句话点明业务场景
       - Task（任务）：你负责什么
       - Action（动作）：你具体做了什么（动宾结构）
       - Result（结果）：量化数据
    3. 【项目经历排序】把与JD匹配度最高的项目放在第一个。大厂系统和HR都倾向于只仔细看前1-2段项目。
    4. 【教育背景与技能栏】如有AI相关的课程、证书或开源项目，单独列出。
"""
    else:  # both
        channel_strategy = """
    # 投递渠道：Boss直聘 + 大厂官网/小程序（双渠道）
    你需要同时输出两套内容，分别针对两个渠道的不同筛选机制进行优化。
    
    ## Boss直聘策略
    - 【破冰话术】严格的三段式结构（总计<80字）。第一段明确意向，第二段提炼核心背景与量化成果，第三段请求面试。绝对不要输出“[意向约10字]”这样的说明提示语，直接输出你要说的话。
    - 【在线简历】必须严格模仿真实用户在Boss直聘文本框里的填写格式。包括“个人优势”、“工作经历(业绩+内容)”、“项目经历”。要求输出所有在底库中存在的项目经历（不要省略或删减个数）。
    - 【技能标签】6个与JD高度匹配的标签。
    
    ## 大厂官网/PDF版策略
    大厂自研招聘系统有AI初筛，核心是"关键词命中率 + STAR结构解析"。同时这套输出将直接被用户导出为PDF。
    - 【完整输出】必须输出一份包含基本信息、教育经历、技能栏、工作经历、项目经历的完整简历（直接给出完整排版，不要省略基础信息）。
    - 【关键词全覆盖】JD中每个核心技能词必须在工作或项目经历中至少出现1次。
    - 【项目完整】必须输出底库中存在的所有项目经历。
"""

    system_prompt = f"""
    你是顶级的AI产品经理求职包装专家，深谙中国互联网招聘生态。
    
    {memory_context}
    
    {channel_strategy}
    
    # 绝对红线
    1. 事实锁死：禁止捏造任何不在履历中的数据或能力。你只能做"视角转换"，不能做"无中生有"。
    2. 能力边界：严格遵守履历库中的能力设定。所有技术实现必须归因于"Prompt工程"、"Workflow设计"或"Agent编排"。
    3. 禁止虚浮：全篇禁用"赋能、助力、旨在、打通底层逻辑"等黑话。必须使用"动宾结构"描述具体动作。
    4. 严格遵守上述【系统长期记忆与用户偏好约束】中的所有规则。
    """
    
    if channel == "boss":
        output_format = """
    # 输出规范
    ### 💬 Boss直聘破冰话术（输出3条供选择，每条严格限制80字以内）
    1. [直接写出完整的话术文本，不要带任何提示说明符号]
    2. ...
    3. ...
    
    ### 🏷️ 个人能力标签（6个）
    标签1 | 标签2 | 标签3 | 标签4 | 标签5 | 标签6

    ---
    ### 📄 【在线简历定制内容】（直接复制粘贴到对应字段）
    
    **【个人优势】**
    [提炼一段约200字的个人优势文本，结合JD核心需求撰写]
    
    **【工作经历 - 业绩】**
    [1-3点纯量化成果数据]
    
    **【工作经历 - 内容】**
    1. [动词+对象+结果，命中JD关键词]
    2. ...
    
    *(根据底库中的项目数量，逐一输出每个项目)*
    **【项目经历 1 - 项目名称】** [结合JD微调项目名称]
    **【项目经历 1 - 业绩】** [量化成果]
    **【项目经历 1 - 内容】** [项目具体职责与工作流]
    
    **【项目经历 2 - 项目名称】** ...
    **【项目经历 2 - 业绩】** ...
    **【项目经历 2 - 内容】** ...
    """
    elif channel == "official":
        output_format = """
    # 输出规范
    ### 📄 大厂官网投递/PDF导出完整版简历
    
    # 你的姓名
    电话：你的电话 | 邮箱：你的邮箱 | 年龄：你的年龄 | 政治面貌：中共党员
    求职意向：[结合JD的岗位名称] | 求职城市：深圳、广州
    
    ## 🛠️ 核心技能与工具
    - [从JD中提取关键词 + 底库技能，全面覆盖]
    - ...
    
    ## 💼 工作经历
    ### [公司名称] | 电气技术员 | 2024.07 — 至今
    - **S(场景)**：[1句话业务场景]
    - **T(任务)**：[你负责什么]
    - **A(动作)**：[具体做了什么，嵌入JD关键词]
    - **R(结果)**：[量化数据]
    *(如果有其他模块，继续按 STAR 格式列出)*
    
    ## 🚀 项目经历
    *(逐一输出底库中的所有项目)*
    ### 项目1：[项目名称] | AI产品设计 / 独立开发 | [时间]
    - **S**：...
    - **T**：...
    - **A**：...
    - **R**：...
    
    ### 项目2：[项目名称] | AI产品设计 | [时间]
    ...
    
    ## 🎓 教育经历
    **湖南工程学院** | 本科 | 电气工程及其自动化 | 2019.09 - 2023.06
    
    ## 📌 综合素质
    CET-6，长跑爱好者。2023.06毕业后全职备考研究生（二战），2024.07入职现单位。
    **GitHub：** github.com/Zephyr-Labs-dev/AI-Resume-Optimizer
    """
    else:  # both
        output_format = """
    # 输出规范（分渠道输出，用分隔线隔开）

    ---
    ## 📱 Boss直聘版
    
    ### 💬 破冰话术（输出3条，严格80字，直接输出话术文本）
    1. ...
    2. ...
    3. ...
    
    ### 🏷️ 个人能力标签（6个）
    标签1 | 标签2 | 标签3 | 标签4 | 标签5 | 标签6

    ### 📄 【在线简历定制内容】
    **【个人优势】**
    [约200字的定制个人优势]
    
    **【工作经历 - 业绩】** [纯量化数据]
    **【工作经历 - 内容】**
    1. [动词+对象+结果]
    2. ...
    
    *(逐一输出底库中所有2个项目)*
    **【项目经历 1 - 项目名称】** ...
    **【项目经历 1 - 业绩】** ...
    **【项目经历 1 - 内容】** ...
    
    **【项目经历 2 - 项目名称】** ...
    ...

    ---
    ## 🏢 大厂官网/PDF导出完整版简历
    
    # 你的姓名
    电话：你的电话 | 邮箱：你的邮箱 | 年龄：你的年龄 | 政治面貌：中共党员
    求职意向：[结合JD的岗位名称] | 求职城市：深圳、广州
    
    ## 🛠️ 核心技能与工具
    - [核心技能点]
    ...
    
    ## 💼 工作经历
    ### [公司名称] | 电气技术员 | 2024.07 — 至今
    - **S**：... **T**：... **A**：... **R**：...
    
    ## 🚀 项目经历
    *(逐一输出所有项目)*
    ### 项目1：[项目名称] | [角色] | [时间]
    - **S**：... **T**：... **A**：... **R**：...
    ...
    
    ## 🎓 教育经历
    **湖南工程学院** | 本科 | 电气工程及其自动化 | 2019.09 - 2023.06
    
    ## 📌 综合素质
    CET-6，长跑爱好者。2023.06毕业后全职备考研究生（二战），2024.07入职现单位。
    **GitHub：** github.com/Zephyr-Labs-dev/AI-Resume-Optimizer
    """

    system_prompt += output_format
    
    user_prompt = f"【基础简历】:\n{base_resume}\n\n【目标 JD】:\n{jd_text}"
    return call_llm(system_prompt, user_prompt)


def evaluate_resume(jd_text: str, drafted_resume: str, base_resume: str, channel: str = "both") -> dict:
    """多路自动化评测：针对中国招聘生态的真实筛选逻辑打分"""
    
    channel_desc = {
        "boss": "Boss直聘（推荐算法曝光 + 破冰话术转化）",
        "official": "大厂官网/小程序（关键词命中 + STAR结构解析）",
        "both": "Boss直聘 + 大厂官网双渠道"
    }.get(channel, "双渠道")
    
    system_prompt = f"""
    你是一个专门模拟中国互联网招聘生态筛选机制的无情评审系统。
    当前评测的投递渠道为：{channel_desc}
    
    请根据提供的【原版 JD】、【用户的真实底库简历】和【AI 生成的定制化简历】，从以下五个维度进行严格打分 (0-100分)：
    
    1. keyword_hit_rate (关键词命中率)：
       - 提取 JD 中所有核心技能/工具/方法论关键词（如：Agent、RAG、Prompt Engineering、工作流编排、B端等）
       - 逐一检查这些关键词是否在生成的简历中出现
       - 计算公式：命中的关键词数 / JD总关键词数 × 100
       - 如果有关键词缺失，在feedback中逐一列出缺失的关键词
    
    2. boss_hook_score (Boss直聘破冰力)：
       - 破冰话术是否在第一句就命中了JD的核心痛点？
       - 是否包含了具体的量化成果（而非空泛的描述）？
       - 是否以一个能引发HR回复欲望的提问结尾？
       - 技能标签是否精准匹配JD高频词？
       - 如果当前渠道不包含Boss直聘，此项给50分作为基准
    
    3. star_density (STAR信息密度)：
       - 每段经历是否都包含了清晰的 Situation-Task-Action-Result？
       - 是否做到了"每句话都有信息增量"（无废话、无空泛描述）？
       - 动词使用是否精准（"设计/搭建/主导" vs "参与/协助/了解"）？
    
    4. anti_hallucination (反幻觉安全指数)：
       - 逐一对比生成简历中提到的每一项技能、数据、项目，检查是否在真实底库简历中有对应原始素材
       - 如果发现了底库中不存在的技能或数据，在feedback中明确指出
       - 100分 = 零幻觉，完全基于事实
    
    5. recruiter_click_rate (预估HR点击率)：
       - 综合以上所有维度，模拟一个大厂AI团队的HR或业务负责人看到这份简历后，会不会点开详情或回复破冰话术
       - 考虑因素：第一眼吸引力、与JD的相关度、专业度感知
    
    你必须以严格的 JSON 格式输出结果：
    {{
        "keyword_hit_rate": 85,
        "boss_hook_score": 78,
        "star_density": 90,
        "anti_hallucination": 95,
        "recruiter_click_rate": 82,
        "average_score": 86,
        "missing_keywords": ["关键词1", "关键词2"],
        "feedback_for_improvement": "具体的修改建议，分点列出：1. 哪些关键词缺失需要补上 2. 破冰话术哪里不够吸引人 3. 哪段经历的STAR结构不完整 4. 是否有幻觉风险"
    }}
    """
    
    user_prompt = f"【原版 JD】:\n{jd_text}\n\n【真实底库简历】:\n{base_resume}\n\n【AI 生成的定制化简历】:\n{drafted_resume}"
    
    response = call_llm(system_prompt, user_prompt, json_mode=True)
    import json
    try:
        result = json.loads(response)
        # 兼容旧字段名，确保 average_score 存在
        if "average_score" not in result:
            scores = [result.get(k, 0) for k in ["keyword_hit_rate", "boss_hook_score", "star_density", "anti_hallucination", "recruiter_click_rate"]]
            result["average_score"] = round(sum(scores) / len(scores))
        return result
    except:
        return {"average_score": 0, "feedback_for_improvement": "解析评分失败"}
