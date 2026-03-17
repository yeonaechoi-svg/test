import streamlit as st
import anthropic
from datetime import datetime

# 페이지 설정
st.set_page_config(
    page_title="정보 교사 챗봇",
    page_icon="👨‍🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
    <style>
    .teacher-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        margin-bottom: 20px;
    }
    .chat-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
    }
    .student-message {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
    }
    .teacher-message {
        background-color: #f3e5f5;
        border-left: 4px solid #9c27b0;
    }
    .code-block {
        background-color: #f5f5f5;
        border-radius: 5px;
        padding: 10px;
        margin: 10px 0;
        font-family: monospace;
    }
    </style>
""", unsafe_allow_html=True)

# 사이드바 설정
with st.sidebar:
    st.markdown("### ⚙️ 설정")
    
    api_key = st.text_input(
        "Claude API 키를 입력하세요",
        type="password",
        help="https://console.anthropic.com 에서 API 키를 발급받으세요"
    )
    
    st.markdown("---")
    st.markdown("### 📚 학습 도움말")
    st.info("""
    **이 챗봇을 활용하세요:**
    - 정보 과목의 개념 설명 요청
    - 프로그래밍 코드 작성 및 설명
    - 학습 전략 및 팁
    - 과제 도움 (직접 답안 제공 아님)
    """)
    
    st.markdown("---")
    st.markdown("### 💡 추천 질문")
    st.markdown("""
    - "변수란 무엇인가요?"
    - "Python에서 for 반복문 사용법"
    - "알고리즘이란 뭔가요?"
    - "리스트와 딕셔너리의 차이점"
    """)

# 메인 헤더
st.markdown("""
    <div class="teacher-header">
        <h1>👨‍🏫 고등학교 정보 교사 챗봇</h1>
        <p>Python, 알고리즘, 데이터베이스 등 정보 과목의 모든 것을 도와드립니다!</p>
    </div>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

if "teacher_instructions" not in st.session_state:
    st.session_state.teacher_instructions = """당신은 경험 많은 고등학교 1학년 정보 교사입니다.

역할 및 원칙:
1. 학생의 질문에 친절하고 이해하기 쉽게 설명합니다.
2. 구체적인 예시와 코드 예제를 제공합니다.
3. 개념 이해를 돕기 위해 비유와 실생활 사례를 활용합니다.
4. 틀린 답변은 지적하되, 학생이 스스로 깨달을 수 있도록 유도합니다.
5. 코드 작성 시 주석을 충분히 달고 설명합니다.
6. 한국어로만 응답합니다.
7. 학생의 수준에 맞춰 설명합니다.

정보 교과의 주요 영역:
- 프로그래밍 (Python, 기본 문법)
- 알고리즘 (정렬, 탐색 등)
- 자료구조 (배열, 리스트, 딕셔너리 등)
- 데이터베이스 기초
- 네트워크 기초
- 보안 개념"""

# 탭 구성
tab1, tab2 = st.tabs(["💬 학습 가이드", "🔧 코드 생성"])

with tab1:
    st.subheader("학습 가이드 챗봇")
    st.markdown("정보 과목에 대해 궁금한 점을 물어보세요!")
    
    # 메시지 표시
    message_container = st.container()
    
    with message_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                    <div class="chat-container student-message">
                        <strong>📌 학생:</strong><br>{message["content"]}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="chat-container teacher-message">
                        <strong>👨‍🏫 선생님:</strong><br>{message["content"]}
                    </div>
                """, unsafe_allow_html=True)
    
    # 입력 영역
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "질문을 입력하세요",
            placeholder="예: 변수란 무엇인가요?",
            label_visibility="collapsed"
        )
    
    with col2:
        send_button = st.button("📤 전송", use_container_width=True)
    
    # 메시지 처리
    if send_button and user_input and api_key:
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        try:
            client = anthropic.Anthropic(api_key=api_key)
            
            # API 호출
            response = client.messages.create(
                model="claude-haiku-4-5-20251001",
                max_tokens=2048,
                system=st.session_state.teacher_instructions,
                messages=st.session_state.messages
            )
            
            assistant_message = response.content[0].text
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_message
            })
            
            st.rerun()
            
        except anthropic.APIError as e:
            st.error(f"API 오류: {str(e)}")
    elif send_button and not api_key:
        st.warning("⚠️ API 키를 먼저 입력해주세요")
    
    # 대화 초기화 버튼
    if st.button("🔄 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

with tab2:
    st.subheader("🔧 코드 생성 어시스턴트")
    st.markdown("원하는 코드를 설명하면 생성해드립니다.")
    
    # 코드 생성 요청
    code_request = st.text_area(
        "코드 요청사항을 입력하세요",
        placeholder="예: 1부터 100까지의 합을 구하는 Python 코드를 만들어주세요",
        height=100
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        language = st.selectbox(
            "프로그래밍 언어",
            ["Python", "Java", "C++", "JavaScript"],
            key="language"
        )
    
    with col2:
        difficulty = st.selectbox(
            "난이도",
            ["초급", "중급", "고급"],
            key="difficulty"
        )
    
    with col3:
        include_comments = st.checkbox("주석 포함", value=True)
    
    generate_button = st.button("✨ 코드 생성", use_container_width=True)
    
    if generate_button and code_request and api_key:
        # 변수 정의
        comment_status = "포함" if include_comments else "미포함"
        backtick = "
