import numpy as np 
import requests
from bs4 import BeautifulSoup
import time
from pykrx import stock
import pandas as pd

def get_beta_one(*tick,type='df'):
    beta_lst = []
    for i in tick:
        url = 'https://navercomp.wisereport.co.kr/v2/company/c1010001.aspx?cmp_cd='+i
        res = requests.get(url)
        # res.raise_for_status()
        soup = BeautifulSoup(res.text,'html.parser')
        section = soup.find('tbody')
        part = section.find_all('td',class_="num")
        beta = part[5].get_text().strip()
        # print(beta)
        beta_lst.append(beta)
        time.sleep(1)
        # break; 
    if type == 'list':
        return beta_lst
    if type == 'df':
        return pd.DataFrame(beta_lst,index=tick,columns={'beta'})

