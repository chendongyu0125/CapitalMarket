from pathlib import Path
import os
import pandas as pd
import re

# -*- coding: utf-8 -*-
'''
Author: Dongyu Chen
Date: 2020-09-28
Revision：2020-11-11

Description: extract key words from annual report 

Source: 
(1) pdf2txt_SZ_disclosure 深圳证交所上市公司年报
(2) pdf2txt_SH_disclosure 上海证交所上市公司年报

Key_words: 
    '大数据',
    '人工智能',
    '机器学习',
    '区块链',
    '新一代信息技术',
    '深度学习',
    '人工神经网络',
    '云计算'

'''

from pathlib import Path
import os
import pandas as pd
import re

class DocReader:
    '''
    根据root, file_name,flag信息获得文件相关信息
    
    初始化函数
    doc = DocReader(root, file_name, market="sh")
    
        输入参数
            root: 所在文件目录
            file_name: 年报文件名
            market：指明是上证年报还是深证年报
        属性：
            CompanyCode
            CompanyName
            Year
            root
            file_name
            IsAnnualReport
    
    getContent()
        返回值：如果是年报文件，则返回年报内容
        
    
    '''
    def __init__(self, root, file_name, market="sh"):
        if not file_name.endswith(".txt"):
            self.IsAnnualReport=False
            
        if market.lower()=="sh": #上交所年报
                if file_name.startswith('6') and '_n' in file_name: #上交所年报
                    self.IsAnnualReport=True
                    segs = file_name.split("_")        
                    self.CompanyCode = market+"_"+segs[0]  
                    self.CompanyName=""
                    self.Year = segs[1]
                    self.root=root
                    self.file_name=file_name                    
                else:
                    self.IsAnnualReport=False 
        elif market.lower()=="sz": #深交所年报
                if '年度报告'in file_name and '摘要' not in file_name and '已取消' not in file_name: #深交所年报
                    self.IsAnnualReport=True
                    segs = file_name.split("_")
                    self.CompanyCode=market+"_"+segs[0]
                    self.CompanyName=segs[1]
                    self.Year=segs[2]
                    self.root=root
                    self.file_name=file_name
                else:
                    self.IsAnnualReport=False
        else:
            self.IsAnnualReport=False    
    def getContent(self):
        assert self.IsAnnualReport            
        file_path=Path(self.root, self.file_name)        
        with open(file_path, 'r', encoding='utf-8', errors ='ignore') as f:
           # print(file_path)
            content = f.read()                
            f.close()       
        return content

            
def extract_keywords(dir_markets, key_words, save_path):
    '''
    用来根据关键字提取其在年报中出现的次数，并将结果存储在save_path文件中
    extract_keywords(dir_markets, key_words, save_path)
    输入参数：
        dir_markets:年报的文件目录，包括上证年报目录和深证年报目录
        key_words:关键词列表
        save_path：提取结果的存储目录
        
    返回值：
        item: pandas DataFrame对象，包括CompanyCode, CompanyName, Year,关键词词频等信息
        
    '''
    columns=['CompanyCode','Year','CompanyName']
    columns.extend(key_words)
    items = []
    test_counter=0
    flag=False
    print("start to extract key words...")
    for market in dir_markets:
        print("\nstart to extract the market of {0}".format(market))
        for root, dirs, files in os.walk(dir_markets[market]):              
            if flag: break
            for file_name in files: 
                if flag: break                
                
                doc=DocReader(root, file_name, market=market)
                if not doc.IsAnnualReport:
                    continue
                test_counter=test_counter+1
                # if test_counter>=300: flag=True
                item={}
                item['CompanyCode']=doc.CompanyCode
                item['CompanyName']=doc.CompanyName
                item['Year']=doc.Year
                content=doc.getContent()
                content=content.replace("电子商务有限公司","")
                for keyword in key_words:
                    key_word=keyword.replace("+","\+")
                    num = len(re.findall(key_word, content))
                    item[keyword]=num 
               
                items.append(item)
                if test_counter % 100 ==0:
                    print(".", end="")
    df = pd.DataFrame(items, columns=columns)
    df.to_csv(save_path, index=False) 
    print("\nsuccessfully extracted and written to: {}".format(save_path))
    return df

import re
def extract_origin(dir_markets, key_words, save_path):
    '''
    提取关键词所出现的位置，并将结果存储在save_path文件中
    extract_origin(dir_markets, key_words, save_path)
    输入参数：
        dir_markets:年报的文件目录，包括上证年报目录和深证年报目录
        key_words:关键词列表
        save_path：提取结果的存储目录
        
    返回值：
        item: pandas DataFrame对象，包括CompanyCode, CompanyName, Year,keyword，origin,counts
        其中counts表示该关键词在该句中出现的次数
        
    '''
    columns=['CompanyCode','Year','CompanyName','keyword','counts','origin']
    
    items = []
    test_counter=0
    flag=False
    print("start to extract key words...")
    for market in dir_markets:
        print("\nstart to extract the market of {0}".format(market))
        for root, dirs, files in os.walk(dir_markets[market]):              
            if flag: break
            for file_name in files: 
                if flag: break                
                
                doc=DocReader(root, file_name, market=market)
                if not doc.IsAnnualReport:
                    continue
                
                
                test_counter=test_counter+1
                if test_counter>=30: flag=True
                

                content=doc.getContent()
                content=content.replace("\n","").replace(" ","")
                content=content.replace("电子商务有限公司","")
                companyName=re.findall("公司简称：....",content)
                if len(companyName)>0:
                    companyName=companyName[0].replace("公司简称：","")
                else:
                    companyName=""
                split_symbs ="[！|!|。|.]"
                if len(content)<=0: continue
                sentences = re.split(split_symbs, content)             
                
                for sentence in sentences:                    
                    for keyword in key_words: 
                        key_word=keyword.replace("+","\+")
                        num = len(re.findall(key_word, sentence))
                        if num>0:
                            item={}
                            item['CompanyCode']=doc.CompanyCode
                            if len(doc.CompanyName)>0:
                                item['CompanyName']=doc.CompanyName
                            else:
                                item['CompanyName']=companyName
                            item['Year']=doc.Year
                            item['keyword']=keyword
                            item['counts']=num
                            item['origin']=sentence.replace(keyword,"***"+keyword+"***")                            
                            items.append(item)
                del content
                del doc
                
                if (test_counter) % 100==0:
                    print(".", end="")
    df = pd.DataFrame(items, columns=columns)
    df.to_csv(save_path, index=False) 
    print("\nsuccessfully extracted and written to: {}".format(save_path))
    return df

# 从以下目录的年报中提取信息，并将结果存在当前目录的csv文件中
sh_dir ="/data/rawdata/ListedCompanyReport/pdf2txt_SH_disclosure/reports"
sz_dir="/data/rawdata/ListedCompanyReport/pdf2txt_SZ_disclosure"
dir_markets={"sh":sh_dir, "sz":sz_dir}

key_words = ['互联网+','电子商务','工业互联网']

save_path="keywords_counter_20201229_updated.csv"
items=extract_keywords(dir_markets, key_words, save_path)
items

var1 =['大数据',
'人工智能',
'机器学习',
'区块链',
'新一代信息技术',
'深度学习',
'人工神经网络',
'云计算',
'工业互联网'
]
var2 =['大数据',
'云计算',
]
var3=['大数据',
'人工智能',
'机器学习',
'区块链',
'新一代信息技术',
'深度学习',
'人工神经网络',
'云计算',
'物联网',
'技术支持',
'新型信息技术服务',
]
var4=[
    '互联网＋',
'Internet',
'物联网',
'人工智能',
'大数据',
'云计算',
'电子商务',
'线上',
'线下',
'O2O',
'B2B',
'C2C',
'B2C',
'C2B',
'P2P',
'区块链',
'物联网',
'深度学习',

]
var5=[
    'EB 级存储',
'NFC 支付',
'差分隐私技术',
'大数据',
'第三方支付',
'多方安全计算',
'分布式计算',
'股权众筹融资',
'互联网金融',
'机器学习',
'开放银行',
'类脑计算',
'量化金融',
'流计算',
'绿色计算',
'内存计算',
'区块链',
'人工智能',
'认知计算',
'融合架构',
'商业智能',
'身份验证',
'深度学习',
'生物识别技术',
'数据可视化',
'数据挖掘',
'数字货币',
'投资决策辅助系统',
'图计算',
'图像理解',
'网联',
'文本挖掘',
'物联网',
'信息物理系统',
'虚拟现实',
'移动互联',
'移动支付',
'亿级并发',
'异构数据',
'语义搜索',
'语音识别',
'云计算',
'征信',
'智能金融合约',
'智能客服',
'智能数据分析',
'智能投顾',
'自然语言处理',

]

var6=[
    '第三方支付',
'网贷',
'互联网理财',
'电子银行',
'大数据',
'在线支付',
'众筹',
'网络理财',
'在线银行',
'云计算',
'移动支付',
'网络小贷',
'理财平台',
'网银',
'人工智能',
'电脑支付',
'网上融资',
'券商',
'网络银行',
'区块链',
'网上支付',
'网上投资',
'互联网保险',
'网上银行',
'ABS云',

]
var7=[
    '互联网＋',
'Internet',
'物联网',
'人工智能',
'大数据',
'云计算',
'电子商务',
'线上',
'线下',
'O2O',
'B2B',
'C2C',
'B2C',
'C2B',
'P2P',

]

var8=[
    '互联网时代',
'互联网思维',
'移动互联网',
'Internet',
'互联网+',
'电子商务',
'互联网 ',
'互联网商业模式',
'线上',
'线下',
'O2O',
'B2B',
'C2C',
'B2C',
'C2B',

]

var9=[
    '5G',
'三网融合',
'通信网络',
'互联网时代',
'互联网思维',
'移动互联网',
'互联网商业模式',
'互联网 ',
'金融科技相关等',

]

var10=[
    '互联网＋',
'Internet',
'物联网',
'人工智能',
'大数据',
'云计算',
'电子商务',
'线上',
'线下',
'O2O',
'B2B',
'C2C',
'B2C',
'C2B',
'P2P',
'区块链',
'物联网',
'技术支持',
'新型信息技术服务',
'人工神经网络',
'深度学习',

]

bag_of_words =[var1, var2, var3, var4,var5, var6, var7, var8, var9, var10]

key_words=[]
for keys in bag_of_words:
    key_words.extend(keys)
key_words=set(key_words)
print(key_words)
    
save_path="origin_keywords_counter_20201229_all.csv"
extract_origin(dir_markets, key_words, save_path)


# 从以下目录的年报中提取信息，并将结果存在当前目录的csv文件中
sh_dir ="/data/rawdata/ListedCompanyReport/pdf2txt_SH_disclosure/reports"
sz_dir="/data/rawdata/ListedCompanyReport/pdf2txt_SZ_disclosure"
dir_markets={"sh":sh_dir, "sz":sz_dir}

key_words = ['大数据','人工智能','机器学习',
             '区块链','新一代信息技术','深度学习',
             '人工神经网络','云计算']
key_words = ['大数据','人工智能','机器学习',
             '区块链','新一代信息技术','深度学习',
             '人工神经网络','云计算',
            'ABS云','物联网','技术支持','新型信息技术服务','Internet','电子商务','线上','线下',
            'O2O','B2B','C2C','B2C','C2M','C2B','P2P','互联网+','AI','IoT']
save_path="origin_keywords_counter_20201229_sample.csv"
items=extract_origin(dir_markets, key_words, save_path)
items
