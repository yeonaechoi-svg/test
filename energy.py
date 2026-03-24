import streamlit as st
import anthropic
import math
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="에너지 변환 시뮬레이션",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 제목
st.title("⚡ 운동에너지 & 위치에너지 전환 시뮬레이션")
st.markdown("중학교 물리 - 에너지 변환의 법칙을 배워봅시다!")

# 사이드바 - API 키 설정
with st.sidebar:
    st.header("🔧 설정")
    api_key = st.text_input(
        "Claude API 키 입력",
        type="password",
        help="Anthropic Claude API 키를 입력하세요"
    )
    
    st.divider()
    st.subheader("📚 학습 가이드")
    st.markdown("""
    ### 운동에너지 (KE)
    - **공식**: KE = ½mv²
    - 물체가 움직일 때 가지는 에너지
    - 속도가 빨수록 커집니다
    
    ### 위치에너지 (PE)
    - **공식**: PE = mgh
    - 높이가 있을 때 가지는 에너지
    - 높이가 높을수록 커집니다
    
    ### 에너지 보존 법칙
    - KE + PE = 상수 (마찰 무시)
    - 위치에너지 → 운동에너지
    """)

# 상태 관리
if "messages" not in st.session_state:
    st.session_state.messages = []
if "simulation_active" not in st.session_state:
    st.session_state.simulation_active = False

# 메인 콘텐츠 - 탭 구조
tab1, tab2, tab3 = st.tabs(["💬 AI 튜터", "🎯 시뮬레이션", "📊 에너지 그래프"])

# ==================== TAB 1: AI 튜터 ====================
with tab1:
    st.subheader("AI 물리교사와 대화하기")
    
    # 채팅 히스토리 표시
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 사용자 입력
    user_input = st.chat_input(
        "물리 질문을 입력하세요...",
        disabled=not api_key
    )
    
    if user_input and api_key:
        # 사용자 메시지 추가
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        with st.chat_message("user"):
            st.markdown(user_input)
        
        # Claude API 호출
        try:
            client = anthropic.Anthropic(api_key=api_key)
            
            system_prompt = """당신은 친절하고 열정적인 중학교 물리교사입니다. 
학생들의 물리 질문에 대해 다음과 같이 답변합니다:

1. **명확한 설명**: 복잡한 개념을 단순하게 설명합니다
2. **실생활 예시**: 일상에서 볼 수 있는 예시를 들어 설명합니다
3. **수학적 기초**: 필요시 공식을 제시하고 설명합니다
4. **격려**: 학생의 호기심을 격려하고 긍정적인 태도를 유지합니다
5. **에너지 전환**: 운동에너지(KE = ½mv²)와 위치에너지(PE = mgh) 전환에 특히 집중합니다

특히 에너지 보존 법칙(총 에너지 = KE + PE = 상수)을 강조하세요."""
            
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                
                with client.messages.stream(
                    model="claude-haiku-4-5-20251001",
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[
                        {"role": msg["role"], "content": msg["content"]}
                        for msg in st.session_state.messages
                    ]
                ) as stream:
                    for text in stream.text_stream:
                        full_response += text
                        message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
            
            # 어시스턴트 응답 저장
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response
            })
        
        except anthropic.APIError as e:
            st.error(f"API 오류: {str(e)}")
    elif user_input and not api_key:
        st.warning("API 키를 입력해주세요!")

# ==================== TAB 2: 시뮬레이션 ====================
with tab2:
    st.subheader("🎯 에너지 변환 시뮬레이션")
    st.markdown("변수를 조정하여 운동에너지와 위치에너지의 변화를 관찰해보세요!")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        mass = st.slider(
            "물체의 질량 (kg)",
            min_value=0.5,
            max_value=10.0,
            value=2.0,
            step=0.5
        )
    
    with col2:
        height = st.slider(
            "초기 높이 (m)",
            min_value=0.0,
            max_value=50.0,
            value=10.0,
            step=1.0
        )
    
    with col3:
        g = st.slider(
            "중력가속도 (m/s²)",
            min_value=8.0,
            max_value=10.0,
            value=9.8,
            step=0.1
        )
    
    st.divider()
    
    # 초기 위치에너지 계산
    initial_pe = mass * g * height
    
    # 떨어지는 높이별 에너지 계산
    heights = np.linspace(height, 0, 100)
    pes = mass * g * heights
    
    # 에너지 보존: KE = 초기PE - 현재PE
    kes = initial_pe - pes
    velocities = np.sqrt(2 * kes / mass)  # v = sqrt(2*KE/m)
    
    # 3개의 메트릭 표시
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
    
    with metric_col1:
        st.metric("초기 위치에너지", f"{initial_pe:.1f} J")
    
    with metric_col2:
        st.metric("지면 도달 시 운동에너지", f"{initial_pe:.1f} J")
    
    with metric_col3:
        final_velocity = np.sqrt(2 * initial_pe / mass)
        st.metric("최종 속도", f"{final_velocity:.2f} m/s")
    
    with metric_col4:
        st.metric("총 에너지", f"{initial_pe:.1f} J")
    
    st.divider()
    
    # 선택 지점에서의 상세 계산
    st.subheader("📍 특정 높이에서의 에너지 계산")
    selected_height = st.slider(
        "확인할 높이 선택 (m)",
        min_value=0.0,
        max_value=height,
        value=height/2,
        step=0.5
    )
    
    pe_at_height = mass * g * selected_height
    ke_at_height = initial_pe - pe_at_height
    v_at_height = np.sqrt(2 * ke_at_height / mass) if ke_at_height >= 0 else 0
    
    detail_col1, detail_col2, detail_col3 = st.columns(3)
    
    with detail_col1:
        st.info(f"""
        **높이: {selected_height:.1f} m**
        
        PE = mgh
        PE = {mass} × {g} × {selected_height}
        PE = **{pe_at_height:.2f} J**
        """)
    
    with detail_col2:
        st.success(f"""
        **운동에너지**
        
        KE = 총E - PE
        KE = {initial_pe:.2f} - {pe_at_height:.2f}
        KE = **{ke_at_height:.2f} J**
        """)
    
    with detail_col3:
        st.warning(f"""
        **순간 속도**
        
        v = √(2KE/m)
        v = √(2 × {ke_at_height:.2f} / {mass})
        v = **{v_at_height:.2f} m/s**
        """)

# ==================== TAB 3: 에너지 그래프 ====================
with tab3:
    st.subheader("📊 에너지 변환 그래프")
    
    col1, col2 = st.columns(2)
    
    with col1:
        mass_graph = st.slider(
            "그래프용 질량 (kg)",
            min_value=0.5,
            max_value=10.0,
            value=2.0,
            step=0.5,
            key="mass_graph"
        )
    
    with col2:
        height_graph = st.slider(
            "그래프용 높이 (m)",
            min_value=0.0,
            max_value=50.0,
            value=10.0,
            step=1.0,
            key="height_graph"
        )
    
    g_graph = 9.8
    
    # 데이터 준비
    heights_graph = np.linspace(height_graph, 0, 100)
    pes_graph = mass_graph * g_graph * heights_graph
    initial_pe_graph = mass_graph * g_graph * height_graph
    kes_graph = initial_pe_graph - pes_graph
    total_energy = pes_graph + kes_graph
    
    # 그래프 생성
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
    
    # 그래프 1: 에너지 변화
    ax1.plot(heights_graph, pes_graph, label='위치에너지 (PE)', linewidth=2, color='blue')
    ax1.plot(heights_graph, kes_graph, label='운동에너지 (KE)', linewidth=2, color='red')
    ax1.plot(heights_graph, total_energy, label='총 에너지', linewidth=2, 
             linestyle='--', color='green')
    ax1.set_xlabel('높이 (m)', fontsize=12)
    ax1.set_ylabel('에너지 (J)', fontsize=12)
    ax1.set_title('에너지 보존 법칙', fontsize=14, fontweight='bold')
    ax1.legend(fontsize=10)
    ax1.grid(True, alpha=0.3)
    
    # 그래프 2: 속도 변화
    velocities_graph = np.sqrt(2 * kes_graph / mass_graph)
    ax2.plot(heights_graph, velocities_graph, linewidth=2, color='purple')
    ax2.fill_between(heights_graph, velocities_graph, alpha=0.3, color='purple')
    ax2.set_xlabel('높이 (m)', fontsize=12)
    ax2.set_ylabel('속도 (m/s)', fontsize=12)
    ax2.set_title('높이에 따른 속도 변화', fontsize=14, fontweight='bold')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    st.pyplot(fig)
    
    # 설명
    st.markdown("""
    ### 📖 그래프 해석
    
    **왼쪽 그래프 (에너지 변화)**
    - 파란 선: 높이가 내려갈수록 위치에너지는 감소
    - 빨간 선: 높이가 내려갈수록 운동에너지는 증가
    - 초록 선(점선): 총 에너지는 항상 일정 (에너지 보존!)
    
    **오른쪽 그래프 (속도 변화)**
    - 물체가 떨어질수록 속도는 빨라집니다
    - 지면에 도달할 때 최대 속도에 도달
    """)

# 푸터
st.divider()
st.markdown("""
<div style='text-align: center; color: gray; font-size: 12px;'>
    <p>🎓 중학교 물리 에너지 학습 플랫폼 | Claude Haiku 4.5 기반</p>
    <p>© 2024 Physics Learning Assistant</p>
</div>
""", unsafe_allow_html=True)
