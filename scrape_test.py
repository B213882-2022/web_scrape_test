import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time

def get_page(page_number):
    url = f'http://www.letpub.com.cn/nsfcfund_search.php?mode=advanced&datakind=list&currentpage={page_number}'
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    form = {'addcomment_s1':'H', 'startTime':'2019', 'endTime':'2019'} # 'H'为医学科学部
    response = requests.post(url, headers=headers,data=form)
    if response.ok:
        
        soup = BeautifulSoup(response.text,"html.parser")
        all_info = soup.findAll('tr')
        
        title1_list = []
        for title1 in all_info[1]:
            # print(title1.text)
            title1_list.append(title1.text)
        
        title2_list = []
        for i in range(3,7):
            title2_list.append(all_info[i].findAll(['th','td'])[0].text)
        
        df1 = pd.DataFrame()
        df2 = pd.DataFrame()
        for i in range(2,len(all_info)-1):
            if all_info[i].findAll(['th','td'])[0].text not in ['题目','学科分类','学科代码','执行时间','中文关键词','结题摘要']:
                content1_list = []
                for content1 in all_info[i]:
                    content1_list.append(content1.text)
                df_temp1 = pd.DataFrame([content1_list],columns=title1_list)
                df1 = pd.concat([df1,df_temp1],axis=0,ignore_index=True)
            elif all_info[i].findAll(['th','td'])[0].text == '题目':
                content2_list = []
                content2_list.append(all_info[i].findAll(['th','td'])[1].text)
            elif all_info[i].findAll(['th','td'])[0].text in ['学科分类','学科代码']:
                content2_list.append(all_info[i].findAll(['th','td'])[1].text)
            elif all_info[i].findAll(['th','td'])[0].text == '执行时间':
                content2_list.append(all_info[i].findAll(['th','td'])[1].text)
                df_temp2 = pd.DataFrame([content2_list],columns=title2_list)
                df2 = pd.concat([df2,df_temp2],axis=0,ignore_index=True)
            else:
                continue
        
        df2['一级学科'] = df2['学科分类'].map(lambda x: re.split(r'[：|，]',x)[1])
        df2['二级学科'] = df2['学科分类'].map(lambda x: re.split(r'[：|，]',x)[3])
        df2['三级学科'] = df2['学科分类'].map(lambda x: re.split(r'[：|，]',x)[5])
        df2['一级代码'] = df2['学科代码'].map(lambda x: re.split(r'[：|，]',x)[1])
        df2['二级代码'] = df2['学科代码'].map(lambda x: re.split(r'[：|，]',x)[3])
        df2['三级代码'] = df2['学科代码'].map(lambda x: re.split(r'[：|，]',x)[5])
        df2['执行起始'] = df2['执行时间'].map(lambda x: re.split(r'\s',x)[0])
        df2['执行截止'] = df2['执行时间'].map(lambda x: re.split(r'\s',x)[2])
        df2 = df2[['题目','一级学科','二级学科','三级学科','一级代码','二级代码','三级代码','执行起始','执行截止']]
        df = pd.concat([df1,df2],axis=1)
        return df
    else:
        print('get webpage failed!')
        return None

df = pd.DataFrame()
for i in range(1,21):
    print(i)
    df = pd.concat([df,get_page(i)],axis=0,ignore_index=True)
    time.sleep(1)

df.to_csv(r'./scrape_test.csv')