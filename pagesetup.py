# Streamlit page setup file

# Streamlit 불러오기
import streamlit
# 자주 쓸 Pandas 불러오기
import pandas
# ChatGPT API 활용
import openai
# FAISS 불러오기
from langchain.vectorstores import FAISS
# OpenAIEmbeddings 불러오기
from langchain.embeddings import OpenAIEmbeddings
# 운영체제 기본 기능 불러오기
import os

# API key를 읽어오기 위해 env load
from dotenv import load_dotenv
load_dotenv()

# Site main header
text1 = "AI 면접관"
streamlit.header(text1, divider='rainbow')

# Site 소개
text2 = "모의 면접 및"
text3 = "자기소개서 첨삭 Platform"
streamlit.title(text2)
streamlit.title(text3)



##### 이건 그냥 시도해 본 case 입니다. 버려도 좋습니다.
##### 비슷하게 여러 button을 활용한 걸 만들수도 있습니다.
# Button으로 입력받을 양식 정하기
#left, right = streamlit.columns(2)
#if left.button("회사 or 직무 하나만 입력할래요",use_container_width = True):
#    left.markdown("알겠습니다! 하나만 입력하세요!")
#if right.button("회사와 직무 모두 입력할래요", use_container_width = True):
#    right.markdown("알겠습니다! 둘 다 입력해주세요!")

# Top Bar에서 기초 정보 입력받기
with streamlit.form("사용자 입력 FORM"):
    company_name = streamlit.text_input("지원한 회사명을 입력해주세요", placeholder = "예) OpenAI")
    position_name = streamlit.text_input("지원한 직무/직군을 입력해주세요", placeholder = "예) 개발자")
    submit_button = streamlit.form_submit_button("면접 시작")
# submit_button이 눌리면
if submit_button:
    streamlit.session_state["company_name"] = company_name     # company_name을 company_name으로 받기
    streamlit.session_state["position_name"] = position_name   # position_name을 position_name으로 받기
    streamlit.session_state["chat_start"] = True
    streamlit.success(f"{company_name}의 {position_name}직무/직군에 대한 면접을 시작합니다.")

# 칸분리
streamlit.divider()

# 실제 면접 진행 interface
if streamlit.session_state.get("chat_started", False):
    streamlit.write("## 면접 진행 중")
    # 이전 메시지 출력
    for message in streamlit.session_state["messages"]:
        with streamlit.chat_message(message["role"]):
            streamlit.markdown(message["content"])
    
    # 사용자 입력 받기
    user_input = streamlit.chat_input("답변을 입력하세요")
    if user_input:
        # 사용자 메시지 추가
        streamlit.session_state["messages"].append({"role": "user", "content": user_input})
        
        # AI 면접관 응답 생성
        with streamlit.chat_message("assistant"):
            # GPT 응답 생성 (예시로 고정된 답변 제공)
            ai_response = f"좋은 답변입니다. {streamlit.session_state['position_name']} 역할에서 추가적으로 강조할 점은 다음과 같습니다..."
            streamlit.markdown(ai_response)
        
        # AI 응답 저장
        streamlit.session_state["messages"].append({"role": "assistant", "content": ai_response})


if "chat_started" not in streamlit.session_state:
    streamlit.session_state["chat_started"]=[]      # session_state 저장소

if submit_button:
    # 회사명과 직무 저장
    streamlit.session_state["company_name"] = company_name
    streamlit.session_state["position_name"] = position_name
    streamlit.session_state["chat_started"] = True

    # 회사 및 직무 설명 출력
    streamlit.success(f"{company_name} {position_name} 지원 면접을 준비합니다!")
    
    # 초기 메시지 추가
    streamlit.session_state["messages"].append({
        "role": "assistant",
        "content": f"안녕하세요! {company_name}의 {position_name} 면접을 준비합니다. 궁금한 점이나 준비된 답변을 입력해보세요!"
    })

# 2. 채팅 인터페이스
if streamlit.session_state["chat_started"]:
    streamlit.write("## 면접 채팅 시작")
    
    # 이전 대화 출력
    for message in streamlit.session_state["messages"]:
        with streamlit.chat_message(message["role"]):
            streamlit.markdown(message["content"])
    
    # 사용자 입력
    user_input = streamlit.chat_input("답변을 입력하세요")
    if user_input:
        # 사용자 메시지 추가
        streamlit.session_state["messages"].append({"role": "user", "content": user_input})
        
        # AI 응답 생성
        with streamlit.chat_message("assistant"):
            with streamlit.spinner("답변 생성 중..."):
                # ChatGPT API 호출
                prompt = f"""
                회사: {streamlit.session_state['company_name']}
                직무: {streamlit.session_state['position_name']}
                질문: {user_input}
                답변을 면접관 스타일로 작성해주세요.
                """
                # GPT-4 API 호출
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
            
            # AI 응답 출력 및 저장
            streamlit.markdown(ai_response)
            streamlit.session_state["messages"].append({"role": "assistant", "content": ai_response})