from dotenv import load_dotenv
import faiss
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings

load_dotenv()

vectorstore = FAISS.load_local(
     folder_path= 'faiss_db',
     index_name = 'faiss_index',
     embeddings = OpenAIEmbeddings(),
     allow_dangerous_deserialization = True
)

# 이 아래부터 수정하여 작성하기
retriever = vectorstore.as_retriever(search_type="mmr",search_kwargs={"k": 3, "lambda_mult": 0.5})
