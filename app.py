import streamlit as st
import agent
import memory

st.set_page_config(page_title="智能简历调优系统 - Agentic Resume", layout="wide")

st.title("🚀 Agentic Resume Optimizer (带长期记忆与自动评测)")

# 侧边栏：配置基础信息
with st.sidebar:
    st.header("⚙️ 个人资产配置")
    base_resume = st.text_area("你的基础核心履历 (知识底库)", height=300, 
                               placeholder="在这里粘贴你的真实简历经历，Agent 将基于此进行事实抽取，绝不瞎编。")
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
    jd_text = st.text_area("粘贴你要投递的 Boss 直聘或猎聘 JD 原文", height=500)
    
    analyze_btn = st.button("🔍 1. 启动风险检测 (JD Decoder)", type="secondary")
    generate_btn = st.button("✨ 2. 一键生成简历 (带自动评测反思)", type="primary")

    if analyze_btn and jd_text and base_resume:
        with st.spinner("正在以无情精算师视角进行排雷..."):
            risk_report = agent.analyze_jd_risk(jd_text, base_resume)
            st.success("检测完成！")
            st.markdown(risk_report)

with col2:
    st.header("📄 定制生成结果")
    
    if generate_btn and jd_text and base_resume:
        # 步骤 1：获取记忆
        mem_context = memory.get_memory_context()
        
        # 步骤 2：生成初稿
        with st.status("🤖 Agent 正在工作中...", expanded=True) as status:
            st.write("1. 正在读取长期记忆约束...")
            st.write("2. 正在打磨破冰话术与简历结构...")
            draft = agent.draft_resume(jd_text, base_resume, mem_context)
            
            st.write("3. 正在唤醒多维度评测系统 (ATS 模拟器)...")
            eval_result = agent.evaluate_resume(jd_text, draft, base_resume)
            
            # 反思循环 (Reflexion) - 演示逻辑，最多重试1次
            if eval_result.get("average_score", 0) < 85:
                st.warning(f"⚠️ 初稿评分仅为 {eval_result.get('average_score')}，触发反思重写机制！")
                st.write(f"**裁判给出的批评:** {eval_result.get('feedback_for_improvement')}")
                st.write("4. 正在根据反馈重新修改简历...")
                
                # 将批评作为临时记忆加入 Prompt 重新生成
                refined_mem_context = mem_context + f"\n\n【上次生成的严厉批评，你必须改正】：{eval_result.get('feedback_for_improvement')}"
                draft = agent.draft_resume(jd_text, base_resume, refined_mem_context)
                
                # 再次评测
                st.write("5. 正在进行二次评测...")
                eval_result = agent.evaluate_resume(jd_text, draft, base_resume)
                
            status.update(label="✅ 简历调优与评测完成！", state="complete", expanded=False)
        
        # 展示最终结果
        st.subheader(f"🏆 最终 ATS 综合评分: {eval_result.get('average_score', 'N/A')} 分")
        cols = st.columns(3)
        cols[0].metric("JD 覆盖率", f"{eval_result.get('jd_coverage_score', 0)}")
        cols[1].metric("STAR 规范度", f"{eval_result.get('star_format_score', 0)}")
        cols[2].metric("反幻觉安全指数", f"{eval_result.get('hallucination_risk', 0)}")
        
        st.markdown("---")
        st.markdown(draft)
        
        # 放入 Session State 供后续评价使用
        st.session_state['latest_draft'] = draft

    st.markdown("---")
    st.subheader("🗣️ 教导 Agent (更新长期记忆)")
    feedback = st.text_input("对生成的简历不满意？指出它的缺点，Agent 会永远记住：", placeholder="例如：以后不要在项目经验里写‘协同排查’，改成‘主导排查’")
    if st.button("写入记忆库"):
        if feedback:
            memory.add_feedback(feedback)
            st.success("✅ 记忆已更新！刷新页面后将在左侧边栏生效。下次生成将严格遵守此约束。")
        else:
            st.error("请输入内容")
