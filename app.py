import streamlit as st
import os
import agent
import memory

# 个人资产配置文件路径（存放在 Obsidian Knowledge-Base 中）
ASSET_FILE = r"D:\AI-Agent-Workspace\Knowledge-Base\Personal_Resume_Asset.md"

def load_asset_file():
    """从 Obsidian Knowledge-Base 自动加载个人资产配置"""
    if os.path.exists(ASSET_FILE):
        with open(ASSET_FILE, 'r', encoding='utf-8') as f:
            return f.read()
    return ""

st.set_page_config(page_title="智能简历调优系统 - Agentic Resume", layout="wide")

st.title("🚀 智能简历调优系统")
st.caption("带长期记忆 × 多维自动评测 × 中国招聘生态深度适配")

# 侧边栏：配置基础信息
with st.sidebar:
    st.header("⚙️ 个人资产配置")
    
    # 自动加载 Obsidian 中的个人资产文件
    loaded_asset = load_asset_file()
    if loaded_asset:
        st.success("✅ 已从 Obsidian 自动加载个人资产")
        with st.expander("📄 查看/编辑已加载的资产内容", expanded=False):
            base_resume = st.text_area("个人核心履历底库", value=loaded_asset, height=400,
                                       help="此内容来自 Knowledge-Base/personal_resume_asset.md，你可以直接在 Obsidian 中编辑它，刷新网页即可生效。")
    else:
        st.warning("⚠️ 未找到个人资产文件，请手动粘贴")
        st.caption(f"或在 Obsidian 中创建：`{ASSET_FILE}`")
        base_resume = st.text_area("你的基础核心履历 (知识底库)", height=300, 
                                   placeholder="在这里粘贴你的真实简历经历，Agent 将基于此进行事实抽取，绝不瞎编。")
    
    st.markdown("---")
    st.header("📡 投递渠道")
    channel = st.radio(
        "选择你要投递的渠道（不同渠道的简历编排策略完全不同）：",
        options=["both", "boss", "official"],
        format_func=lambda x: {
            "both": "🔥 双渠道 (Boss直聘 + 大厂官网)",
            "boss": "📱 仅 Boss直聘",
            "official": "🏢 仅大厂官网/小程序"
        }[x],
        index=0
    )
    
    st.markdown("---")
    st.header("🧠 系统长期记忆库")
    mem_data = memory.load_memory()
    st.write("**当前雷区词汇:**", ", ".join(mem_data["avoid_words"]))
    st.write("**能力边界约束:**", mem_data["skill_constraints"])
    if mem_data["user_feedback_history"]:
        st.write("**最近用户反馈:**")
        for fb in mem_data["user_feedback_history"][-3:]:
            st.caption(f"- {fb}")

# 主界面：分栏
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 输入目标岗位 JD")
    jd_text = st.text_area("粘贴你要投递的 JD 原文（Boss直聘职位描述 或 官网招聘要求）", height=500)
    
    analyze_btn = st.button("🔍 1. 启动风险检测 (JD Decoder)", type="secondary", use_container_width=True)
    generate_btn = st.button("✨ 2. 一键生成简历 (带自动评测反思)", type="primary", use_container_width=True)

    if analyze_btn and jd_text and base_resume:
        with st.spinner("正在以无情精算师视角进行排雷..."):
            risk_report = agent.analyze_jd_risk(jd_text, base_resume)
            st.success("检测完成！")
            st.markdown(risk_report)
    elif analyze_btn:
        st.error("⚠️ 请先在左侧栏填入你的基础履历，并在上方粘贴 JD 原文。")

with col2:
    st.header("📄 定制生成结果")
    
    # 渠道提示
    channel_labels = {
        "both": "📱 Boss直聘 + 🏢 大厂官网",
        "boss": "📱 Boss直聘",
        "official": "🏢 大厂官网/小程序"
    }
    st.info(f"当前优化渠道：**{channel_labels[channel]}**（可在左侧栏切换）")
    
    if generate_btn and jd_text and base_resume:
        # 步骤 1：获取记忆
        mem_context = memory.get_memory_context()
        
        # 步骤 2：生成初稿
        with st.status("🤖 Agent 正在工作中...", expanded=True) as status:
            st.write("1️⃣ 正在读取长期记忆约束...")
            st.write(f"2️⃣ 正在按【{channel_labels[channel]}】渠道策略生成简历...")
            draft = agent.draft_resume(jd_text, base_resume, mem_context, channel)
            
            st.write("3️⃣ 正在唤醒多维度评测系统...")
            eval_result = agent.evaluate_resume(jd_text, draft, base_resume, channel)
            
            # 反思循环 (Reflexion) - 最多重试1次
            if eval_result.get("average_score", 0) < 85:
                st.warning(f"⚠️ 初稿评分仅为 {eval_result.get('average_score')}，触发反思重写机制！")
                
                # 显示缺失关键词
                missing = eval_result.get("missing_keywords", [])
                if missing:
                    st.error(f"❌ 缺失的JD关键词：{', '.join(missing)}")
                
                st.write(f"**裁判批评:** {eval_result.get('feedback_for_improvement')}")
                st.write("4️⃣ 正在根据反馈重新修改简历...")
                
                # 将批评作为临时记忆加入 Prompt 重新生成
                refined_mem_context = mem_context + f"\n\n【上次生成的严厉批评，你必须改正】：{eval_result.get('feedback_for_improvement')}"
                if missing:
                    refined_mem_context += f"\n【必须补上的缺失关键词】：{', '.join(missing)}"
                draft = agent.draft_resume(jd_text, base_resume, refined_mem_context, channel)
                
                # 再次评测
                st.write("5️⃣ 正在进行二次评测...")
                eval_result = agent.evaluate_resume(jd_text, draft, base_resume, channel)
                
            status.update(label="✅ 简历调优与评测完成！", state="complete", expanded=False)
        
        # 展示最终结果
        avg = eval_result.get('average_score', 'N/A')
        if isinstance(avg, (int, float)) and avg >= 85:
            st.success(f"🏆 综合评分: {avg} 分 — 可以投递！")
        elif isinstance(avg, (int, float)):
            st.warning(f"🏆 综合评分: {avg} 分 — 建议在左下角反馈后重新生成")
        else:
            st.info(f"🏆 综合评分: {avg}")
            
        cols = st.columns(5)
        cols[0].metric("🎯 关键词命中", f"{eval_result.get('keyword_hit_rate', 0)}")
        cols[1].metric("💬 破冰话术力", f"{eval_result.get('boss_hook_score', 0)}")
        cols[2].metric("📐 STAR密度", f"{eval_result.get('star_density', 0)}")
        cols[3].metric("🛡️ 反幻觉", f"{eval_result.get('anti_hallucination', 0)}")
        cols[4].metric("👆 HR点击率", f"{eval_result.get('recruiter_click_rate', 0)}")
        
        # 缺失关键词提醒
        missing = eval_result.get("missing_keywords", [])
        if missing:
            st.warning(f"⚠️ 仍有缺失关键词：{', '.join(missing)}。建议检查是否可以从你的真实经历中补充。")
        
        st.markdown("---")
        st.markdown(draft)
        
        # 放入 Session State 供后续评价使用
        st.session_state['latest_draft'] = draft

    elif generate_btn:
        st.error("⚠️ 请先在左侧栏填入你的基础履历，并在左栏上方粘贴 JD 原文。")

    st.markdown("---")
    st.subheader("🗣️ 教导 Agent (更新长期记忆)")
    feedback = st.text_input("对生成的简历不满意？指出它的缺点，Agent 会永远记住：", placeholder="例如：以后不要在项目经验里写'协同排查'，改成'主导排查'")
    if st.button("写入记忆库"):
        if feedback:
            memory.add_feedback(feedback)
            st.success("✅ 记忆已更新！刷新页面后将在左侧边栏生效。下次生成将严格遵守此约束。")
        else:
            st.error("请输入内容")
