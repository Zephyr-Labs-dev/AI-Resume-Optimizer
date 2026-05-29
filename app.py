import streamlit as st
import os
import agent
import memory
import history

# 个人资产配置文件路径（已迁移至 Obsidian Personal-Notes）
ASSET_FILE = r"D:\AI-Personal-Notes\Personal-Notes\Personal_Resume_Asset.md"

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
    
    loaded_asset = load_asset_file()
    if loaded_asset:
        st.success("✅ 已从 Obsidian 自动加载")
        with st.expander("📄 查看/编辑已加载的资产内容", expanded=False):
            base_resume = st.text_area("个人核心履历底库", value=loaded_asset, height=400)
    else:
        st.warning("⚠️ 未找到个人资产文件")
        base_resume = st.text_area("你的基础核心履历", height=300)
    
    st.markdown("---")
    st.header("📡 投递渠道")
    channel = st.radio(
        "选择你要投递的渠道：",
        options=["both", "boss", "official"],
        format_func=lambda x: {
            "both": "🔥 双渠道 (Boss直聘 + 大厂官网)",
            "boss": "📱 仅 Boss直聘",
            "official": "🏢 仅大厂官网/小程序"
        }[x],
        index=0
    )
    
    st.markdown("---")
    st.header("🎛️ 模型选择")
    selected_model = st.selectbox(
        "选择 MIMO 模型",
        options=["mimo-v2.5", "mimo-v2.5-pro"],
        index=0,
        help="mimo-v2.5: 速度快；mimo-v2.5-pro: 逻辑深度更强，生成质量更高"
    )

    st.markdown("---")
    st.header("📜 历史生成记录")
    history_records = history.load_all_history()
    selected_history = None
    if history_records:
        history_options = ["-- 新建生成任务 --"] + [f"{r['timestamp']} | 渠道:{r['channel']} | 分数:{r['score']}" for r in history_records]
        history_choice = st.selectbox("查阅过往生成的简历", options=history_options)
        if history_choice != "-- 新建生成任务 --":
            selected_history = history_records[history_options.index(history_choice) - 1]
    else:
        st.caption("暂无历史记录")
        
    st.markdown("---")
    st.header("🧠 系统长期记忆库")
    mem_data = memory.load_memory()
    st.write("**当前雷区词汇:**", ", ".join(mem_data["avoid_words"]))
    st.write("**能力边界约束:**", mem_data["skill_constraints"])
    if mem_data["user_feedback_history"]:
        st.write("**最近反馈:**")
        for fb in mem_data["user_feedback_history"][-3:]:
            st.caption(f"- {fb}")

# 主界面：分栏
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📝 输入目标岗位 JD")
    jd_value = selected_history['data']['jd_text'] if selected_history else ""
    jd_text = st.text_area("粘贴你要投递的 JD 原文", height=500, value=jd_value)
    
    analyze_btn = st.button("🔍 1. 启动风险检测 (JD Decoder)", type="secondary", use_container_width=True)
    generate_btn = st.button("✨ 2. 一键生成简历 (带自动评测反思)", type="primary", use_container_width=True)

    if analyze_btn and jd_text and base_resume:
        with st.spinner("正在以无情精算师视角进行排雷..."):
            risk_report = agent.analyze_jd_risk(jd_text, base_resume, selected_model)
            st.success("检测完成！")
            st.markdown(risk_report)
    elif analyze_btn:
        st.error("⚠️ 请先粘贴 JD 原文。")

with col2:
    st.header("📄 定制生成结果")
    
    if selected_history:
        st.info(f"🔙 正在查看历史版本: **{selected_history['timestamp']}** (模型: {selected_history['data'].get('model', '未知')})")
    else:
        st.info(f"当前模式：新建生成任务 | 渠道：{channel} | 模型：{selected_model}")
        
    draft = None
    eval_result = None
    
    if generate_btn and jd_text and base_resume:
        mem_context = memory.get_memory_context()
        
        with st.status("🤖 Agent 正在工作中...", expanded=True) as status:
            st.write(f"1️⃣ 正在使用 **{selected_model}** 生成简历初稿...")
            draft = agent.draft_resume(jd_text, base_resume, mem_context, channel, selected_model)
            
            st.write("2️⃣ 正在唤醒多维度评测系统...")
            eval_result = agent.evaluate_resume(jd_text, draft, base_resume, channel, selected_model)
            
            if eval_result.get("average_score", 0) < 85:
                st.warning(f"⚠️ 初稿评分仅为 {eval_result.get('average_score')}，触发反思重写机制！")
                missing = eval_result.get("missing_keywords", [])
                if missing:
                    st.error(f"❌ 缺失关键：{', '.join(missing)}")
                
                st.write(f"**裁判批评:** {eval_result.get('feedback_for_improvement')}")
                st.write("3️⃣ 正在进行针对性修正重写...")
                
                refined_mem = mem_context + f"\n\n【必须改正的批评】：{eval_result.get('feedback_for_improvement')}"
                if missing:
                    refined_mem += f"\n【必须补上的词】：{', '.join(missing)}"
                    
                draft = agent.draft_resume(jd_text, base_resume, refined_mem, channel, selected_model)
                eval_result = agent.evaluate_resume(jd_text, draft, base_resume, channel, selected_model)
                
            status.update(label="✅ 简历调优与评测完成！", state="complete", expanded=False)
            
        # 将使用的模型也存入历史数据
        eval_result['model'] = selected_model
        history.save_history(jd_text, channel, eval_result, draft)
        
    elif selected_history:
        draft = selected_history['data']['draft']
        eval_result = selected_history['data']['scores']
        
    if draft and eval_result:
        avg = eval_result.get('average_score', 'N/A')
        if isinstance(avg, (int, float)) and avg >= 85:
            st.success(f"🏆 综合评分: {avg} 分 — 可以投递！")
        elif isinstance(avg, (int, float)):
            st.warning(f"🏆 综合评分: {avg} 分 — 建议重新生成或手动优化")
            
        cols = st.columns(5)
        cols[0].metric("🎯 关键词命中", f"{eval_result.get('keyword_hit_rate', 0)}")
        cols[1].metric("💬 破冰话术力", f"{eval_result.get('boss_hook_score', 0)}")
        cols[2].metric("📐 STAR密度", f"{eval_result.get('star_density', 0)}")
        cols[3].metric("🛡️ 反幻觉", f"{eval_result.get('anti_hallucination', 0)}")
        cols[4].metric("👆 HR点击率", f"{eval_result.get('recruiter_click_rate', 0)}")
        
        missing = eval_result.get("missing_keywords", [])
        if missing:
            st.warning(f"⚠️ 仍有缺失关键词：{', '.join(missing)}")
        
        st.markdown("---")
        st.markdown(draft)

    st.markdown("---")
    st.subheader("🗣️ 教导 Agent (更新长期记忆)")
    feedback = st.text_input("对生成的简历不满意？指出它的缺点，Agent 会永远记住：", placeholder="例如：以后不要写'协同'，改成'主导'")
    if st.button("写入记忆库"):
        if feedback:
            memory.add_feedback(feedback)
            st.success("✅ 记忆已更新！下次生成将严格遵守此约束。")
        else:
            st.error("请输入内容")
