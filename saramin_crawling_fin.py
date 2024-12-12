import json
import time
import bs4
import numpy as np
import pandas as pd
import random
import re
from langchain.document_loaders import WebBaseLoader


path_all = list()
# random_num = random.randrange(1,3100)
# test_link = 'https://www.saramin.co.kr/zf_user/interview-review?my=0&page=1&csn=&group_cd=&orderby=registration&career_cd=&job_category=&company_nm=+'
# for i in range(random_num,random_num+5):
for i in range(1,3154):
    path = f'https://www.saramin.co.kr/zf_user/interview-review?my=0&page={i}'
    path_all.append(path)


loader = WebBaseLoader(
                web_paths = tuple(path_all),
                # web_paths = (test_link,),
                bs_kwargs = dict(
                    parse_only = bs4.SoupStrainer(
                        'div',
                        attrs = {
                            'class' : ['view_title','view_cont']
                        }
                    )
                )
            )

s = loader.load()
db = ''

for u in range(0,len(s)):
    ct = s[u].page_content.strip()
    db = db + ''.join(ct) + '\n'

process_words = db.replace('대기중','불합격').replace('\n면접 질문\n','ctg면접질문\n').replace('\n전형 및 면접 진행 방식\n','ctg진행방식\n').replace('\n면접 유형\n','ctg면접유형\n').replace('\n면접 인원\n','ctg면접인원\n').replace('\nTIP 및 특이사항\n','ctg특이사항\n') ## 이후 필요한 항목들 'ctg이름'으로 분류하기.
process_words = re.sub('\w*합격\n+\d+.\d+.\d+','\nctg회사이름',process_words)
process_words = re.sub('\d\d\d\d년\s\w반기','\nctg직업종류',process_words)
process_words = re.sub('\n+','\\\\n',process_words)
process_words = re.sub('\s\s+','\n',process_words)
process_words = re.sub('\s+',' ',process_words)
words = re.split('\\\\n', process_words)

np_word = np.array(words)
company_where = np.where(np_word=='ctg회사이름')
whereis = list(company_where[0])

company_idx_list = list()
for w in whereis:
    company_idx_list.append(w-1)
company_idx_list.sort()
# company_idx_all = list(tuple(company_idx_list))
# company_idx_all.sort()
# print(len(company_idx_list)), print(len(company_idx_all)) 중복값 없음.

def dict_format(company):
    f = {'company':company,
        'idx':[],
        'job_category':[],
        'interview_type':[],
        'interview_num':[],
        'interview_how':[],
        'interview_questions':[]
    }
    return f

company_name_processing = list()
for c in company_idx_list:
    company_name_processing.append(words[c])
company_name = list(tuple(company_name_processing)) # 중복값 제거

company_json = dict()
for c in company_name:
    comp_idx = np.where(np_word==c)
    comp_idx = list(comp_idx[0])
    comp_idx = [int(i) for i in comp_idx]
    c = c.strip()
    company_unit = dict_format(c)
    company_unit['idx'].extend(comp_idx)
    company_json[c]=company_unit

# np_word = np.array(words)
# company_where = np.where(np_word=='ctg회사이름')
# whereis = list(company_where[0])


company_idx_list.append(len(words))
for c in range(0,len(company_idx_list)-1):
    company_text = words[company_idx_list[c]:company_idx_list[c+1]]
    company_name_strip = company_text[0].strip()
    search_where = np.array(company_text)
    # 직무 : ctg직업종류-1
    ctg_1 = np.where(search_where=='ctg직업종류')
    ctg_ctg = list(ctg_1[0])[0]
    ctg_ctg = search_where[ctg_ctg-1]
    # 면접유형 : ctg면접유형+1
    ctg_2 = np.where(search_where=='ctg면접유형')
    ctg_type = list(ctg_2[0])[0]
    # 면접인원 : ctg면접인원+1
    ctg_3 = np.where(search_where=='ctg면접인원')
    ctg_num = list(ctg_3[0])[0]
    # 진행방식 : ctg진행방식+1
    ctg_4 = np.where(search_where=='ctg진행방식')
    ctg_how = list(ctg_4[0])[0]
    # 면접질문 : ctg면접질문+1
    ctg_5 = np.where(search_where=='ctg면접질문')
    ctg_question = list(ctg_5[0])[0]

    ctg_type = search_where[ctg_type+1:ctg_num]
    ctg_num = search_where[ctg_num+1:ctg_how]
    ctg_how = search_where[ctg_how+1:ctg_question]

    if 'ctg특이사항' in company_text:
        ctg_6 = np.where(search_where=='ctg특이사항')
        ctg_tip = list(ctg_6[0])[0]
        ctg_question = search_where[ctg_question+1:ctg_tip]
    else:
        ctg_question = search_where[ctg_question+1:]

    ctg_ctg = ''.join(ctg_ctg)
    ctg_type = ' '.join(ctg_type)
    ctg_num = ' '.join(ctg_num)
    ctg_how = ' '.join(ctg_how)
    ctg_question = ' '.join(ctg_question)
    if ctg_ctg not in company_json[company_name_strip]['job_category']:
        company_json[company_name_strip]['job_category'].append(ctg_ctg)
    if ctg_type not in company_json[company_name_strip]['interview_type']:
        company_json[company_name_strip]['interview_type'].append(ctg_type)
    if ctg_num not in company_json[company_name_strip]['interview_num']:
        company_json[company_name_strip]['interview_num'].append(ctg_num)
    if ctg_how not in company_json[company_name_strip]['interview_how']:
        company_json[company_name_strip]['interview_how'].append(ctg_how)
    if ctg_question not in company_json[company_name_strip]['interview_questions']:
        company_json[company_name_strip]['interview_questions'].append(ctg_question)



# for x in company_idx_all:



complete_output_path = "./interview_prossed.json"
with open(complete_output_path, "w", encoding="utf-8") as file:
    json.dump(company_json, file, ensure_ascii=False, indent=4)
