# CACHE DATA LOAD

import streamlit
import openai
from langchain.vectorstores import FAISS
from langchain.embeddings import OpenAIEmbeddings
import os

# API key를 읽어오기 위해 env load
from dotenv import load_dotenv
load_dotenv()

# 캐시된 데이터 로드 함수
@streamlit.cache_data(persist = "disk")        # persist = disk로 local disk에 저장
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
if "company_name" not in streamlit.session_state:
    streamlit.session_state["company_name"] = ""
if "position_name" not in streamlit.session_state:
    streamlit.session_state["position_name"] = ""
if "chat_started" not in streamlit.session_state:
    streamlit.session_state["chat_started"] = False
if "messages" not in streamlit.session_state:
    streamlit.session_state["messages"] = []

# FAISS data load
try:
    faiss_store = load_faiss_data()
    streamlit.success("FAISS data has been loaded!")
except FileNotFoundError as e:
    streamlit.error(str(e))

################################
# 위는 DATA LOAD
################################
# 아래는 사용 예시 - 저런 식으로 FAISS cache data를 대답과정에 집어넣으면 될 것 같다
################################


# company_name과 position_name을 submit_button을 통해 입력받았다고 가정 시
if submit_button:
    # 입력 값 저장
    streamlit.session_state["company_name"] = company_name
    streamlit.session_state["position_name"] = position_name
    streamlit.session_state["chat_started"] = True

    # 회사 및 직무 설명 출력
    streamlit.success(f"{company_name}에서 {position_name}로 지원하는 면접을 준비합니다!")
    job_description = f"""
    **{company_name}**은(는) 혁신적인 기술을 개발하는 회사입니다.  
    **{position_name}**은(는) 주로 AI 모델 개발, 데이터 분석 및 배포 작업을 포함합니다.
    """

    # 초기 메시지
    streamlit.session_state["messages"].append({
        "role": "assistant",
        "content": f"안녕하세요! {company_name}의 {position_name} 면접을 준비합니다.\n (이후에 어떤걸 말로 시작해야할지)"
    })

# Chatting Interface
if streamlit.session_state["chat_started"]:
    streamlit.write("## 면접 채팅 시작")
    
    # 이전 message 출력
    for message in streamlit.session_state["messages"]:
        with streamlit.chat_message(message["role"]):
            streamlit.markdown(message["content"])
    
    # 사용자 입력
    user_input = streamlit.chat_input("답변을 입력하세요")
    if user_input:
        # 사용자 message 저장
        streamlit.session_state["messages"].append({"role": "user", "content": user_input})
        
        # AI 응답 생성
        with streamlit.chat_message("assistant"):
            with streamlit.spinner("답변 생성 중..."):
                # FAISS를 활용한 질문 추천
                related_questions = faiss_store.similarity_search(user_input, k=3)
                faiss_response = "\n".join([f"- {q.page_content}" for q in related_questions])

                # GPT 기반 답변 생성
                prompt = f"""
                회사: {streamlit.session_state['company_name']}
                직무: {streamlit.session_state['position_name']}
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
                except Exception as e:    # 오류 발생 시
                    ai_response = "AI 응답 생성 중 오류가 발생했습니다. 다시 시도해주세요."
            
            # 응답 출력 및 저장
            streamlit.markdown(ai_response)
            streamlit.session_state["messages"].append({"role": "assistant", "content": ai_response})
    
    # 추가 질문 button ??
    if streamlit.button("추가 질문 하시겠습니까?"):
        streamlit.info("추가 질문을 입력해주세요.")
    elif streamlit.button("면접 종료"):
        streamlit.success("면접이 종료되었습니다. 결과를 확인하세요.")