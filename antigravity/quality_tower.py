"""
Quality Tower Components - 质量之塔组件
====================================

Ceremonial UI components for Sheriff Brain's Delivery Gate.
Sheriff Brain 交付门控的仪式感 UI 组件。

Phase 21 P2 Features:
- Ceremonial dual-signature stamps with HTML/SVG animations
- Visual conflict indicators (Green/Yellow/Red)
- Interactive healing preview dialogs
- Trend radar chart with historical shadows
- Quality sparklines (Quality Genome)
"""

import streamlit as st
import asyncio
from pathlib import Path
from typing import Dict, Optional, List
import plotly.graph_objects as go

from .delivery_gate import DeliveryGate, DeliveryResult
from .audit_history import AuditHistoryManager


def display_ceremonial_stamps(result: Optional[DeliveryResult]):
    """
    Display ceremonial dual-signature stamps / 展示仪式感双重签名印章
    
    Phase 21 P2: Enhanced with HTML/SVG animations and visual conflict handling.
    
    Args:
        result: Delivery gate result / 交付门控结果
    """
    if not result:
        st.info("🔍 请先运行质量审计")
        return
    
    # Stamp style template
    stamp_style = """
    <div style="
        border: 4px solid {color};
        padding: 20px;
        border-radius: 15px;
        text-align: center;
        transform: rotate({rotate}deg);
        opacity: {opacity};
        transition: all 0.5s ease-in-out;
        background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0) 100%);
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    ">
        <h2 style="color: {color}; margin: 0; font-weight: bold;">{text}</h2>
        <p style="color: {color}; margin: 5px 0; font-size: 14px;">{subtext}</p>
        <small style="color: {color}; opacity: 0.7;">{signature}</small>
    </div>
    """
    
    cols = st.columns(2)
    
    # Left: Local Signature
    with cols[0]:
        st.subheader("🔐 本地签名 (Local)")
        
        if result.local_signature and result.local_signature.signed:
            # Green stamp - approved
            st.markdown(
                stamp_style.format(
                    color="#00FF00",
                    rotate="-5",
                    opacity="1",
                    text="✅ LOCAL SIGNED",
                    subtext=f"Vibe Score: {result.local_signature.vibe_score:.1f}",
                    signature=result.local_signature.signature
                ),
                unsafe_allow_html=True
            )
            
            # Metrics
            col1, col2 = st.columns(2)
            with col1:
                st.metric("语法错误", result.local_signature.syntax_errors, delta=None)
            with col2:
                st.metric("安全问题", result.local_signature.security_issues, delta=None)
        
        else:
            # Gray stamp - waiting
            st.markdown(
                stamp_style.format(
                    color="#888888",
                    rotate="0",
                    opacity="0.3",
                    text="⏳ WAITING",
                    subtext="Static/Dynamic Check",
                    signature="Pending..."
                ),
                unsafe_allow_html=True
            )
            
            st.caption("静态或动态审计未通过")
    
    # Right: Remote Signature
    with cols[1]:
        st.subheader("🌐 远程签名 (Remote)")
        
        if result.remote_signature and result.remote_signature.signed:
            # Gold stamp - approved
            st.markdown(
                stamp_style.format(
                    color="#FFD700",
                    rotate="5",
                    opacity="1",
                    text="✅ REMOTE SIGNED",
                    subtext=f"Logic Score: {result.remote_signature.logic_score:.1f}",
                    signature=result.remote_signature.signature
                ),
                unsafe_allow_html=True
            )
            
            # Expert comments
            if result.remote_signature.expert_comments:
                with st.expander("专家评论"):
                    for comment in result.remote_signature.expert_comments:
                        st.write(f"- {comment}")
        
        else:
            # Determine status
            if result.local_signature and result.local_signature.signed:
                # Yellow stamp - waiting for remote
                status_text = "⚠️ PENDING"
                status_subtext = "Expert Review"
                color = "#FFA500"
                opacity = "0.7"
            else:
                # Gray stamp - locked
                status_text = "🔒 LOCKED"
                status_subtext = "Local Check Required"
                color = "#888888"
                opacity="0.3"
            
            st.markdown(
                stamp_style.format(
                    color=color,
                    rotate="0",
                    opacity=opacity,
                    text=status_text,
                    subtext=status_subtext,
                    signature="Awaiting..."
                ),
                unsafe_allow_html=True
            )
            
            if result.local_signature and result.local_signature.signed:
                st.caption("本地已通过，等待架构审计...")
            else:
                st.caption("本地审计未通过，远程审计已锁定")
    
    # Visual conflict indicator
    st.markdown("---")
    
    if result.can_deliver:
        # Both signed - celebration!
        st.balloons()
        st.success("🎉 **项目已通过双重签名，准予投产！**")
        st.caption(f"✅ 本地签名: {result.local_signature.signature}")
        st.caption(f"✅ 远程签名: {result.remote_signature.signature}")
        
        # Golden approval banner
        golden_banner = """
        <div style="
            background: linear-gradient(90deg, #FFD700 0%, #FFA500 100%);
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            margin: 10px 0;
            box-shadow: 0 4px 8px rgba(255, 215, 0, 0.3);
        ">
            <h3 style="color: white; margin: 0;">🏆 SHERIFF APPROVED 🏆</h3>
            <p style="color: white; margin: 5px 0;">Quality Gate Passed - Ready for Production</p>
        </div>
        """
        st.markdown(golden_banner, unsafe_allow_html=True)
    
    elif result.local_signature and result.local_signature.signed:
        # Local only - yellow warning
        st.warning("⚠️ **黄色警告：架构不合规，需要远程审计批准**")
        st.caption("本地质量检查已通过，但需要 Sheriff Strategist 的架构审计")
    
    else:
        # Neither signed - red failure
        st.error("🚨 **红色失败：项目未通过质量门控，禁止交付**")
        st.caption("请修复阻塞问题后重新审计")


def display_blocking_issues(result: Optional[DeliveryResult]):
    """
    Display blocking issues / 展示阻塞问题
    
    Args:
        result: Delivery gate result / 交付门控结果
    """
    if not result or not result.blocking_issues:
        st.success("✅ 无阻塞问题")
        return
    
    st.subheader("🚫 阻塞问题 (Blocking Issues)")
    
    with st.expander(f"查看 {len(result.blocking_issues)} 个问题", expanded=True):
        for i, issue in enumerate(result.blocking_issues, 1):
            st.error(f"{i}. {issue}")


def display_trend_radar(project: Dict, history_manager: AuditHistoryManager):
    """
    Display trend radar chart with historical shadows / 展示趋势雷达图（带历史阴影）
    
    Phase 21 P2: Enhanced with quality sparklines (Quality Genome).
    
    Args:
        project: Project information / 项目信息
        history_manager: Audit history manager / 审计历史管理器
    """
    st.subheader("📊 质量趋势雷达图 (Quality Radar)")
    
    # Get audit history
    history = history_manager.get_history(project['name'], limit=3)
    
    if not history:
        st.info("暂无审计历史，请先运行审计")
        return
    
    # Prepare data
    categories = ['Vibe Score', 'Coverage', 'Logic Score', 'Security']
    
    # Current audit (solid line)
    current = history[0]
    current_values = [
        current.get('vibe_score', 0),
        current.get('test_coverage', 0),
        current.get('logic_score', 0),
        max(0, 100 - current.get('security_issues', 0) * 10)  # Convert to score
    ]
    
    # Previous audit (shadow)
    if len(history) > 1:
        previous = history[1]
        previous_values = [
            previous.get('vibe_score', 0),
            previous.get('test_coverage', 0),
            previous.get('logic_score', 0),
            max(0, 100 - previous.get('security_issues', 0) * 10)
        ]
    else:
        previous_values = [0, 0, 0, 0]
    
    # Ideal values (background)
    ideal_values = [100, 100, 100, 100]
    
    # Create radar chart
    fig = go.Figure()
    
    # Ideal (background, semi-transparent green)
    fig.add_trace(go.Scatterpolar(
        r=ideal_values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(0, 255, 0, 0.1)',
        line=dict(color='rgba(0, 255, 0, 0.3)', dash='dash', width=1),
        name='理想满分'
    ))
    
    # Previous (shadow, semi-transparent gray)
    if len(history) > 1:
        fig.add_trace(go.Scatterpolar(
            r=previous_values,
            theta=categories,
            fill='toself',
            fillcolor='rgba(128, 128, 128, 0.2)',
            line=dict(color='rgba(128, 128, 128, 0.5)', width=2),
            name='上次审计'
        ))
    
    # Current (solid, vibrant blue)
    fig.add_trace(go.Scatterpolar(
        r=current_values,
        theta=categories,
        fill='toself',
        fillcolor='rgba(0, 100, 255, 0.3)',
        line=dict(color='rgb(0, 100, 255)', width=3),
        name='当前审计'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=10)
            )
        ),
        showlegend=True,
        height=450,
        margin=dict(l=80, r=80, t=40, b=40)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Quality trend indicator
    if len(history) > 1:
        avg_current = sum(current_values) / len(current_values)
        avg_previous = sum(previous_values) / len(previous_values)
        delta = avg_current - avg_previous
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("当前平均分", f"{avg_current:.1f}", delta=f"{delta:+.1f}")
        
        with col2:
            if delta > 0:
                st.success(f"📈 质量上升 +{delta:.1f}%")
            elif delta < 0:
                st.error(f"📉 质量下降 {delta:.1f}%")
            else:
                st.info("➡️ 质量持平")
        
        with col3:
            # Show timestamp
            st.caption(f"审计时间: {current.get('timestamp', 'Unknown')[:19]}")
    
    # Quality Sparklines (Phase 21 P2: Quality Genome)
    st.markdown("---")
    st.subheader("✨ 质量火花线 (Quality Sparklines)")
    st.caption("过去 10 次审计的波动趋势")
    
    sparklines = history_manager.get_sparkline_data(project['name'])
    
    spark_cols = st.columns(4)
    
    for i, (metric, values) in enumerate(sparklines.items()):
        with spark_cols[i]:
            if values:
                # Create mini sparkline chart
                fig_spark = go.Figure()
                fig_spark.add_trace(go.Scatter(
                    y=values,
                    mode='lines',
                    line=dict(color='#0064FF', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(0, 100, 255, 0.2)'
                ))
                fig_spark.update_layout(
                    showlegend=False,
                    height=80,
                    margin=dict(l=0, r=0, t=0, b=0),
                    xaxis=dict(showticklabels=False, showgrid=False),
                    yaxis=dict(showticklabels=False, showgrid=False, range=[0, 100])
                )
                
                st.plotly_chart(fig_spark, use_container_width=True, key=f"spark_{metric}")
                st.caption(metric.replace('_', ' ').title())


def display_healing_buttons(result: Optional[DeliveryResult], project: Dict):
    """
    Display interactive healing buttons / 展示交互式修复按钮
    
    Phase 21 P2: Enhanced with remedy preview dialogs.
    
    Args:
        result: Delivery gate result / 交付门控结果
        project: Project information / 项目信息
    """
    if not result or result.can_deliver:
        st.success("✅ 无需修复，项目已通过所有审计")
        return
    
    st.subheader("🔥 一键修复 (Interactive Healing)")
    st.caption("Sheriff 可以自动修复以下问题")
    
    # Analyze blocking issues and provide targeted buttons
    issues = result.blocking_issues
    
    for issue in issues:
        if "Test coverage" in issue or "Core coverage" in issue or "Happy path" in issue:
            if st.button("🧪 请求 Agent 补充测试用例", key="heal_tests", type="primary"):
                show_remedy_preview(
                    issue_type="test_coverage",
                    issue=issue,
                    project=project
                )
        
        elif "Vibe score" in issue:
            if st.button("✨ 请求 Agent 清理代码", key="heal_vibe"):
                show_remedy_preview(
                    issue_type="vibe_score",
                    issue=issue,
                    project=project
                )
        
        elif "Security" in issue:
            if st.button("🔒 请求 Agent 修复安全问题", key="heal_security"):
                show_remedy_preview(
                    issue_type="security",
                    issue=issue,
                    project=project
                )
        
        elif "Logic score" in issue:
            if st.button("🎨 请求 Agent 优化逻辑", key="heal_logic"):
                show_remedy_preview(
                    issue_type="logic",
                    issue=issue,
                    project=project
                )


@st.dialog("🔍 修复方案预览 (Remedy Preview)")
def show_remedy_preview(issue_type: str, issue: str, project: Dict):
    """
    Show remedy preview dialog / 展示修复方案预览对话框
    
    Phase 21 P2: Interactive healing with transparency.
    
    Args:
        issue_type: Type of issue / 问题类型
        issue: Issue description / 问题描述
        project: Project information / 项目信息
    """
    st.write("### Sheriff 的诊断报告")
    
    # Generate remedy plan based on issue type
    if issue_type == "test_coverage":
        st.info(f"""
        **问题**: {issue}
        
        **诊断**: 检测到测试覆盖率不足。Sheriff 将分析未覆盖的代码分支，
        并基于本地推理引擎补齐缺失的 Happy Path 测试用例。
        
        **预计效果**: 覆盖率提升 10-20%
        """)
        
        st.write("**预计变更文件:**")
        st.code("A tests/test_missing_coverage.py")
        st.code("M tests/__init__.py")
        
        if st.button("🔥 执行手术 (Execute Healing)", type="primary"):
            with st.spinner("Sheriff 正在生成测试用例..."):
                # Trigger AutonomousAuditor in test_executor mode
                from .healing_executor import HealingExecutor
                
                executor = HealingExecutor(Path(project['root']))
                result = asyncio.run(executor.heal_test_coverage(issue))
                
                if result['success']:
                    st.success(f"✅ {result['message']}")
                    st.write("**变更文件:**")
                    for file in result.get('files_modified', []):
                        st.code(f"A {file}")
                    st.caption("请重新运行审计验证覆盖率提升")
                else:
                    st.error(f"❌ {result['message']}")
                
                st.rerun()
    
    elif issue_type == "vibe_score":
        st.info(f"""
        **问题**: {issue}
        
        **诊断**: 检测到代码质量问题（缺少文档、未使用变量等）。
        Sheriff 将自动清理代码并补充文档字符串。
        
        **预计效果**: Vibe Score 提升至 90+
        """)
        
        st.write("**预计变更文件:**")
        st.code("M src/main.py (添加文档)")
        st.code("M src/utils.py (移除未使用变量)")
        
        if st.button("🔥 执行手术 (Execute Healing)", type="primary"):
            with st.spinner("Sheriff 正在清理代码..."):
                # Trigger code cleanup
                from .healing_executor import HealingExecutor
                
                executor = HealingExecutor(Path(project['root']))
                result = asyncio.run(executor.heal_vibe_score(issue))
                
                if result['success']:
                    st.success(f"✅ {result['message']}")
                    st.write("**变更文件:**")
                    for file in result.get('files_modified', []):
                        st.code(f"M {file}")
                    st.caption("请重新运行审计验证 Vibe Score 提升")
                else:
                    st.error(f"❌ {result['message']}")
                
                st.rerun()
    
    elif issue_type == "security":
        st.warning(f"""
        **问题**: {issue}
        
        **诊断**: 检测到安全问题（硬编码密钥、危险函数调用等）。
        Sheriff 将修复这些安全隐患。
        
        **预计效果**: 安全问题清零
        """)
        
        st.write("**预计变更文件:**")
        st.code("M src/config.py (移除硬编码密钥)")
        st.code("M src/utils.py (替换 eval() 为安全实现)")
        
        if st.button("🔥 执行手术 (Execute Healing)", type="primary"):
            with st.spinner("Sheriff 正在修复安全问题..."):
                # Trigger security fix
                from .healing_executor import HealingExecutor
                
                executor = HealingExecutor(Path(project['root']))
                result = asyncio.run(executor.heal_security(issue))
                
                if result['success']:
                    st.success(f"✅ {result['message']}")
                    st.write("**变更文件:**")
                    for file in result.get('files_modified', []):
                        st.code(f"M {file}")
                    st.caption("请重新运行审计验证安全问题已解决")
                else:
                    st.error(f"❌ {result['message']}")
                
                st.rerun()
    
    elif issue_type == "logic":
        st.info(f"""
        **问题**: {issue}
        
        **诊断**: 检测到逻辑问题（命名不规范、潜在竞态条件等）。
        Sheriff 将优化代码逻辑。
        
        **预计效果**: Logic Score 提升至 90+
        """)
        
        st.write("**预计变更文件:**")
        st.code("M src/core.py (优化变量命名)")
        st.code("M src/async_handler.py (修复竞态条件)")
        
        if st.button("🔥 执行手术 (Execute Healing)", type="primary"):
            with st.spinner("Sheriff 正在优化逻辑..."):
                # Trigger logic optimization
                from .healing_executor import HealingExecutor
                
                executor = HealingExecutor(Path(project['root']))
                result = asyncio.run(executor.heal_logic(issue))
                
                if result['success']:
                    st.success(f"✅ {result['message']}")
                    st.write("**变更文件:**")
                    for file in result.get('files_modified', []):
                        st.code(f"M {file}")
                    st.caption("请重新运行审计验证逻辑优化效果")
                else:
                    st.error(f"❌ {result['message']}")
                
                st.rerun()
    
    if st.button("取消"):
        st.rerun()


def run_delivery_gate_audit(project: Dict) -> Optional[DeliveryResult]:
    """
    Run delivery gate audit / 运行交付门控审计
    
    Args:
        project: Project information / 项目信息
        
    Returns:
        Delivery result / 交付结果
    """
    try:
        gate = DeliveryGate(Path(project['root']))
        
        with st.spinner("🔍 Sheriff 正在执行三级审计..."):
            # Show live pulse indicator
            pulse_placeholder = st.empty()
            
            # Run audit
            result = asyncio.run(gate.can_deliver(project))
            
            pulse_placeholder.empty()
        
        # Save to history
        history_manager = AuditHistoryManager(Path(project['root']))
        history_manager.save_audit(result, project['name'])
        
        # Store in session state
        st.session_state['latest_audit'] = result
        st.session_state['latest_audit_project'] = project['name']
        
        return result
    
    except Exception as e:
        st.error(f"❌ 审计失败: {e}")
        import traceback
        st.code(traceback.format_exc())
        return None


def get_latest_audit_result(project: Dict) -> Optional[DeliveryResult]:
    """
    Get latest audit result / 获取最新审计结果
    
    Args:
        project: Project information / 项目信息
        
    Returns:
        Latest audit result / 最新审计结果
    """
    # Check session state first
    if ('latest_audit' in st.session_state and 
        'latest_audit_project' in st.session_state and
        st.session_state['latest_audit_project'] == project['name']):
        return st.session_state['latest_audit']
    
    return None
