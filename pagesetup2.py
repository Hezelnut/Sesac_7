import streamlit as st
import openai
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
import os

# API key를 읽어오기 위해 env load
from dotenv import load_dotenv
load_dotenv()

# 캐시된 데이터 로드 함수
@st.cache_data(persist = "disk")        # persist = disk로 local disk에 저장
def load_faiss_data():
    # FAISS 인덱스 및 메타데이터 로드
    embedding_model = OpenAIEmbeddings()
    os.path.exists()                    # Path 지정
    x = FAISS.load_local(
        folder_path = 'faiss_db',
        index_name = 'faiss_index',
        embeddings = OpenAIEmbeddings(),
        allow_dangerous_deserialization = True
    )
    return x
    
# session_state 선언 전 빈 file로 초기화 해주기
if "company_name" not in st.session_state:
    st.session_state["company_name"] = ""
if "position_name" not in st.session_state:
    st.session_state["position_name"] = ""
if "chat_started" not in st.session_state:
    st.session_state["chat_started"] = False
if "messages" not in st.session_state:
    st.session_state["messages"] = []

# FAISS data load
try:
    faiss_store = load_faiss_data()
    st.success("FAISS data has been loaded!")
except FileNotFoundError as e:
    st.error(str(e))

# 입력 form
###st.title("AI 면접관")
###st.markdown("지원할 **회사**와 **직무**를 입력하세요.")

with st.form("user_input_form"):
    company_name = st.text_input("회사명", placeholder="예: OpenAI")
    position_name = st.text_input("직무", placeholder="예: AI 엔지니어")
    submit_button = st.form_submit_button("면접 준비 시작")

if submit_button:
    # 입력 값 저장
    st.session_state["company_name"] = company_name
    st.session_state["position_name"] = position_name
    st.session_state["chat_started"] = True

    # 회사 및 직무 설명 출력
    st.success(f"{company_name}에서 {position_name}로 지원하는 면접을 준비합니다!")
    job_description = f"""
    **{company_name}**은(는) 혁신적인 기술을 개발하는 회사입니다.  
    **{position_name}**은(는) 주로 AI 모델 개발, 데이터 분석 및 배포 작업을 포함합니다.
    """
    st.markdown(job_description)

    # 초기 메시지
    st.session_state["messages"].append({
        "role": "assistant",
        "content": f"안녕하세요! {company_name}의 {position_name} 면접을 준비합니다.\n (이후에 어떤걸 말로 시작해야할지)"
    })

# 채팅 인터페이스
if st.session_state["chat_started"]:
    st.write("## 면접 채팅 시작")
    
    # 이전 메시지 출력
    for message in st.session_state["messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # 사용자 입력
    user_input = st.chat_input("답변을 입력하세요")
    if user_input:
        # 사용자 메시지 저장
        st.session_state["messages"].append({"role": "user", "content": user_input})
        
        # AI 응답 생성
        with st.chat_message("assistant"):
            with st.spinner("답변 생성 중..."):
                # FAISS를 활용한 질문 추천
                related_questions = faiss_store.similarity_search(user_input, k=3)
                faiss_response = "\n".join([f"- {q.page_content}" for q in related_questions])

                # GPT 기반 답변 생성
                prompt = f"""
                회사: {st.session_state['company_name']}
                직무: {st.session_state['position_name']}
                질문: {user_input}
                관련 질문: {faiss_response}
                답변을 면접관의 스타일로 작성하세요.
                """
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are an AI interview assistant."},
                            {"role": "user", "content": prompt}
                        ]
                    )
                    ai_response = response["choices"][0]["message"]["content"]
                except Exception as e:
                    ai_response = "AI 응답 생성 중 오류가 발생했습니다. 다시 시도해주세요."
            
            # 응답 출력 및 저장
            st.markdown(ai_response)
            st.session_state["messages"].append({"role": "assistant", "content": ai_response})
    
    # 추가 질문 button
    if st.button("추가 질문 하시겠습니까?"):
        st.info("추가 질문을 입력해주세요.")
    elif st.button("면접 종료"):
        st.success("면접이 종료되었습니다. 결과를 확인하세요.")


# Cache data 초기화 button
if st.button("CACHE 초기화"):
    st.cache_data.clear()


###########################################################################

# Streamlit의 cache_data decorator 활용하면
# 사용자의 data를 caching
# 재방문시 빠르게 FAISS data를 미리 준비&load 가능

# Cached data load
@streamlit.cache_data
def load_faiss_data():
    # FAISS index 및 metadata 로드
    embedding_model = OpenAIEmbeddings(model = "text-embedding-ada-002")
    index_path = "faiss_index"
    if os.path.exists(index_path):
        return FAISS.load_local(index_path, embedding_model)
    else:
        raise FileNotFoundError("FAISS 인덱스 파일이 존재하지 않습니다.")

# Session 초기화
if "company_name" not in streamlit.session_state:
    streamlit.session_state["company_name"] = ""
if "position_name" not in streamlit.session_state:
    streamlit.session_state["position_name"] = ""
if "chat_started" not in streamlit.session_state:
    streamlit.session_state["chat_started"] = False
if "messages" not in streamlit.session_state:
    streamlit.session_state["messages"] = []

# FAISS 데이터 로드
try:
    faiss_store = load_faiss_data()
    streamlit.success("FAISS 데이터 로드 완료!")
except FileNotFoundError as e:
    streamlit.error(str(e))
