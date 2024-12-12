import re
import random
import streamlit as st
from langchain.vectorstores import FAISS
# from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.callbacks import get_openai_callback
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from sklearn.metrics.pairwise import cosine_similarity


st.set_page_config(page_title="모의 면접 : AI 면접관", page_icon="✒", layout="centered")

# url 후보 : https://drive.google.com/file/d/1Xjz2eUbpPqXw8qfL6DXIXnptaYuUOu2V/view?usp=sharing
# img 후보 : https://img.freepik.com/free-vector/job-interview-conversation_74855-7566.jpg?t=st=1733911614~exp=1733915214~hmac=ec13893600536af309286f5744bfd5eb1c690e5274fbe84367b285a02390f8eb&w=1380
# img 후보 : https://img.freepik.com/premium-vector/user-chat-bot-conversation-chatgpt-tiny-man-sitting-computer-desk-type-text_88272-9822.jpg?w=1380
st.markdown(
         f"""
         <style>
         .stApp {{
             background-image: url("https://img-c.udemycdn.com/course/750x422/5927120_ef97.jpg");
             background-attachment: fixed;
             background-size: cover
             
         }}
         </style>
         """,
         unsafe_allow_html=True
     )
st.markdown(
    """
    <style>
        section[data-testid="stSidebar"] {
            width: 800px !important;
        }
        div[class="st-emotion-cache-4uzi61 e1f1d6gn0"] {
            background-color:#eadba3;
            }
        div[data-testid="stExpander"]{
            background-color:#f4e5ad;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
#stVerticalBlockBorderWrapper

# st.markdown(
#     """
#     <style>
#         div[class="st-emotion-cache-4uzi61 e1f1d6gn0"] {
#             background-color:pink;
#             width:600px;
#         }
#     </style>
#     """,
#     unsafe_allow_html=True,
# )

# API key를 읽어오기 위해 env load
from dotenv import load_dotenv
load_dotenv()

llm = ChatOpenAI(model='gpt-4o',temperature=0)
output_parser = StrOutputParser()
embedding_model = OpenAIEmbeddings()

def similarity(a, b):
    return cosine_similarity([a], [b])[0][0]

vectorstore = FAISS.load_local(
    folder_path = 'faiss_db',
    index_name = 'faiss_index',
    embeddings = embedding_model,
    allow_dangerous_deserialization = True
)
retriever = vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 10})



if "chain" not in st.session_state:
    st.session_state["chain"] = []


################################
# 위는 DATA LOAD
################################
# 아래는 사용 예시 - 저런 식으로 FAISS cache data를 대답과정에 집어넣으면 될 것 같다
################################


# company_name과 position_name을 submit_button을 통해 입력받았다고 가정 시

prompt_1 = PromptTemplate.from_template(
    """
    너는 AI 면접관이야. question을 분석해서 질문의 Important factors를 판단해.
    context에 있는 정보를, 판단한 Important factors를 기반으로 new interview questions을 만들어 출력해줘.
    단, new interview questions의 Import factors가 너무 중복되면 안돼.

    대답은 이 형태의 한글로 출력해줘.
    ### Important factors : \n\n ### new interview questions : 

    # context : {context}
    # question : {question}
    # new interview questions :
    # Important factors :
    """
    )
prompt_2 = PromptTemplate.from_template(
    # 두 번째 prompt
    """
    # interview_question : {interview_question}
    # Important_factor : {Important_factor}
    # context : {context}

    너는 AI 면접관이야. 면접자에게 interview_question 할 것이고, 그 의도는 Important_factor를 파악하기 위함이야.
    면접자는 너에게 context 라고 대답을 했어.
    너는 context를 통해 Important_factor를 판단할 수 있는지 알아내야해.
    판단할 수 없다면, '질문자의 의도를 포함하지 못한 대답입니다. 제가 생각하는 모범답안을 출력하겠습니다.'라고 추가로 출력해줘.
    판단할 수 있다면, context의 내용이 아래의 항목들을 만족시켰는가 확인해줘.
    
    - 간결하고 명확하게 표현을 해야한다. '아마도', '대충' 같은 모호한 표현은 사용하면 안된다.
    - 구체적인 사례 활용을 해야한다.
    - 긍정적인 표현을 사용해야한다. 이전 직장, 동료, 경험에 대한 부정적인 언급은 하면 안된다.
    - 회사와 직무에 대한 충분한 이해도를 보여줘야한다.

    만족시키지 못한 항목을 보완하는 방향으로 context를 수정하고 출력시켜줘.

    대답은 이 형태로 출력해줘.

    ### interview_question :
    ### Important_factor :
    ### 수정한 답변 :
    """
    )

chain_1 = prompt_1|llm|output_parser
chain_2 = prompt_2|llm|output_parser

st.session_state["chain"].extend([chain_1,chain_2])


#### 본문 ####
if "lock" not in st.session_state:
    st.session_state["lock"] = False

if "answer_input" not in st.session_state:
    st.session_state["answer_input"] = ''

if "question_input" not in st.session_state:
    st.session_state["question_input"] = ''

if "output_question" not in st.session_state:
    st.session_state["output_question"]=[]

if "output_factors" not in st.session_state:
    st.session_state["output_factors"]=[]

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

if "text_history" not in st.session_state:
    st.session_state["text_history"] = []

if "result_qna" not in st.session_state:
    st.session_state["result_qna"] = []

if "call_back" not in st.session_state:
    st.session_state["call_back"] = []

def compiler(x):
    x = re.sub(r'"*\d.\s','',x)
    return x

def chat_actions():
    st.session_state["chat_history"].append(st.session_state.input_text)
    st.session_state["text_history"].append(st.session_state.answer_input)
    st.session_state["lock"] = True


with get_openai_callback() as cb:
    with st.sidebar:

        st.chat_input("질문을 입력해주세요.",on_submit=chat_actions,key="input_text",disabled=st.session_state.lock)

        if len(st.session_state.chat_history)==0 :
            st.cache_data.clear()
        else:
            st.sidebar.header(st.session_state.chat_history[0])
            if None in st.session_state.chat_history:
                st.session_state.chat_history.remove(None)
            # if len(st.session_state.chat_history)>1: 초기화 부분 생각해봐야함.
            #     st.write(st.session_state.chat_history)
            #     st.write(st.session_state.text_history)
            #     del st.session_state.chat_history
            #     del st.session_state.text_history
            #     del st.session_state.output_factors
            #     del st.session_state.output_question
            #     del st.session_state.text_history
            #     st.cache_data.clear()
            #     st.rerun()

            @st.cache_data
            def question_list():
                ret = retriever.invoke(st.session_state.chat_history[0])
                result_1 = st.session_state["chain"][0].invoke({'context':st.session_state.chat_history[0],'question':ret})

                result_split = re.split(r'#.*:',result_1)
                result_split = [b for b in result_split if b not in ['',' ']]


                Important_factors = result_split[0].split('\n')
                Important_factors = [b for b in Important_factors if b not in ['',' ']]

                interview_questions = result_split[1].split('\n')
                interview_questions = [b for b in interview_questions if b not in ['',' ']]

                return Important_factors, interview_questions

            Important_factors, interview_questions = question_list()

            interview_questions_del = [i for i in interview_questions if i not in st.session_state["output_question"]]
            Important_factors_del = [i for i in Important_factors if i not in st.session_state["output_factors"]]
            
            try:
                x = random.sample(range(0,len(interview_questions_del)),1)[0]
                output_question = interview_questions_del[x]
                st.session_state["output_question"].append(output_question)

                output_factors = Important_factors_del[x]
                st.session_state["output_factors"].append(output_factors)
                if len(st.session_state["output_question"])>1:
                    pass
                else:
                    st.write(f'### 면접 질문을 생성했습니다. \n {compiler(st.session_state["output_question"][-1])}')

                
                

                if st.text_input('면접 질문에 답변해주세요.',on_change=chat_actions,key="answer_input") :

                    # 체인 형성.
                    result_2 = st.session_state["chain"][1].invoke({'context':st.session_state.text_history[-1],'interview_question':st.session_state["output_question"][-2],'Important_factor':st.session_state["output_factors"][-2]})
                    result_2_split = re.split(r'#.*:',result_2)


                    # 전처리
                    result_2_split = [c for c in result_2_split if c not in ['',' ']]
                    result_2_split = [c.strip() for c in result_2_split]
                    # 전처리 한 뒤, 리스트에 있는 빈 요소를 제거.
                    
                    new_question = result_2_split[0] # :: new question
                    important_factor = result_2_split[1] # :: important factor

                    if '\n\n' in result_2_split[2]:
                        new_answer = result_2_split[2].split('\n\n')
                        reject_word_2 = new_answer[1]
                        reject_warn = '질문자의 의도를 포함하지 못한 대답입니다.\n제가 생각하는 모범답안을 출력하겠습니다.'
                    else:
                        reject_word_2 = result_2_split[2] # :: new answer
                        reject_warn = ''

                    result_qna_1 = compiler(st.session_state["output_question"][-2]) # 받은 질문
                    result_qna_2 = compiler(st.session_state["output_factors"][-2]) # 받은 질문의 의도
                    result_qna_3 = st.session_state.text_history[-1] # 사용자의 대답
                    result_qna_4 = reject_warn # 답안의 적합성
                    result_qna_5 = reject_word_2 # 수정 답안
                    result_qna_5_1 = [result_qna_3,result_qna_5]                
                    result_qna_5_2 = embedding_model.embed_documents(result_qna_5_1)
                    result_qna_6 = similarity(result_qna_5_2[0], result_qna_5_2[-1]) # 유사성
                    
                    st.session_state["result_qna"].append([result_qna_1,result_qna_2,result_qna_3,result_qna_4,result_qna_5,result_qna_5_1,result_qna_5_2,result_qna_6])

                    if len(interview_questions)>len(st.session_state["output_question"]):
                        st.write('')
                        st.subheader('다음 질문입니다.')
                        st.write(compiler(st.session_state["output_question"][-1]))
                        st.write('\n\n\n')
                        st.write('----')
                        container_1 = st.container(border=True)
                        container_1.subheader('면접 팁 : AI의 prompt 기반 📌')
                        st.write('')

                        container_2 = st.container(border=True)
                        container_2.write("- 간결하고 명확하게 표현을 해야한다.")
                        container_2.write("👉 '아마도', '대충' 같은 모호한 표현은 사용하면 안된다.")
                        container_2.write('')
                        container_2.write("- 구체적인 사례 활용을 해야한다.")
                        container_2.write('')
                        container_2.write("- 긍정적인 표현을 사용해야한다.")
                        container_2.write("👉 이전 직장, 동료, 경험에 대한 부정적인 언급은 하면 안된다.")
                        container_2.write('')
                        container_2.write("- 회사와 직무에 대한 충분한 이해도를 보여줘야한다.")

                        st.write('---')
                        st.write('')
                        expander_cb = st.expander('Check_Token_Cost')
                        expander_cb.write(cb)

                            
                    else:
                        st.write('준비된 질문이 모두 소진되었습니다.')

            except ValueError :
                st.write('준비된 질문이 모두 소진되었습니다.')
                st.write('새로고침을 눌러주세요!')


    if len(st.session_state["result_qna"])>0:
        for l in range(0,len(st.session_state["result_qna"])):
            expander = st.expander(st.session_state["result_qna"][l][0]) # 받은 질문
            expander.write(st.session_state["result_qna"][l][1]) # 받은 질문의 의도
            expander.write('---')
            expander.write(st.session_state["result_qna"][l][2]) # 사용자의 대답
            expander.write('')
            expander.write(st.session_state["result_qna"][l][3]) # 답안이 적절했는지
            expander.write('---')
            expander.write(st.session_state["result_qna"][l][4]) # 수정한 답안
            expander.write('')
            expander.write(st.session_state["result_qna"][l][7]) # 유사성.
            st.write('----')
    else:
        container_1 = st.container(border=True)
        container_1.subheader('면접 팁 : AI의 prompt 기반 📌')
        st.write('')
        container_2 = st.container(border=True)
        container_2.write("- 간결하고 명확하게 표현을 해야한다.")
        container_2.write("👉 '아마도', '대충' 같은 모호한 표현은 사용하면 안된다.")
        container_2.write('')
        container_2.write("- 구체적인 사례 활용을 해야한다.")
        container_2.write('')
        container_2.write("- 긍정적인 표현을 사용해야한다.")
        container_2.write("👉 이전 직장, 동료, 경험에 대한 부정적인 언급은 하면 안된다.")
        container_2.write('')
        container_2.write("- 회사와 직무에 대한 충분한 이해도를 보여줘야한다.")

        # 면접 팁 추가하기.



