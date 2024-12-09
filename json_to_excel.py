import os
import json
import pandas as pd
import numpy as np
from openpyxl.cell.cell import ILLEGAL_CHARACTERS_RE


json_path = r'C:\Users\RMARKET\Desktop\middle_project\save_db\interview_saramin_processed.json'
with open(json_path,'r',encoding='utf-8') as j:
    json_open = json.load(j)

json_company = list(json_open.keys())


log = 0
for j in json_company:
    print(f'processing {log+1} / {len(json_company)}')
    j = json_open[j]
    # row_num = [len(j['interview_type']), len(j['interview_num']), len(j['job_category']), len(j['interview_how']),len(j['interview_questions'])]
    row_num = [len(j['interview_type']), len(j['job_category']), len(j['interview_how']),len(j['interview_questions'])]

    row_num_max = max(row_num)
    row_num_over = [list(range(0,i)) for i in row_num]
    for r in range(0,len(row_num)):
        while not (row_num_max - len(row_num_over[r])==0):
            row_num_over[r].append(row_num[r]-1)
    # print(row_num)
    # print(row_num_over)
    # [[0, 1, 2, 3], [0, 1, 1, 1], [0, 1, 2, 3], [0, 1, 2, 3], [0, 1, 2, 3]]

    insert_1 = [
        j['interview_type'],
        # j['interview_num'],
        j['job_category'],
        j['interview_how'],
        j['interview_questions']
        ]
    insert_fin = list()
    c_n = list()
    for u in range(0,max(row_num)):
        c_n.append(j['company'])

    for u in range(0,len(row_num)):
        u_unit = list()
        row_u = row_num_over[u]
        insert_u = insert_1[u]
        for z in range(0,row_num_max):
            u_unit.append(insert_u[row_u[z]])
        insert_fin.append(u_unit)
    insert_fin.insert(0,c_n)
    if log==0:
        input_db = pd.DataFrame(insert_fin)
        input_db_T_old = input_db.T
    else:
        input_db = pd.DataFrame(insert_fin)
        input_db_T = input_db.T
        input_db_T_old = pd.concat([input_db_T_old,input_db_T],ignore_index=True)
    log += 1

# input_db_T.columns = columns
columns = ['회사명','면접유형','직군','질문유형','질문']

excel_path = r'C:\Users\RMARKET\Desktop\middle_project\save_db\saramin_excel.xlsx'
# processing_json.to_excel(excel_path)
input_db_T_old.columns=columns
input_db_T_old.to_excel(excel_path,engine='xlsxwriter')