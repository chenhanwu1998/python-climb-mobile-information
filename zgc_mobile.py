import requests
import re
import time
import pandas as pd
from lxml import etree
from reptile_project.gzc_climb import param
data_path=param.data_path
mobile_data_path=param.mobile_data_path
header=param.header

class zgc_mobile:
    def __init__(self):
        self.detail_root= 'http://detail.zol.com.cn'  # 用来拼接成完整的链接的
        self.data = pd.read_csv(data_path)
        self.brand = self.data['品牌']
        self.mobile_url = self.data['url']
        self.m_url_list = []
        self.m_id_list = []
        self.m_type_list = []
        self.m_ref_price_list = []
        self.m_descript_list = []
        self.m_score_list = []
        self.mobile_com=[]
        self.verbose=1

    def get_mobile_id(self,m_url_list):
        # print('-' * 50, 'climb_id')
        pattern = 'index(.*?)\.shtml'
        for m in m_url_list:
            id_ = re.findall(re.compile(pattern=pattern), m)
            self.m_id_list.append(id_[0])

    def get_mobile_type(self,html):
        # print('-' * 50, 'climb_type')
        t_pattern = "//ul[@id='J_PicMode']//h3/a"
        type_list = html.xpath(t_pattern)
        for t in type_list:
            self.m_type_list.append(t.text)

    def get_mobile_reference_price(self,html):
        # print('-' * 50, 'climb_ref_price')
        r_pattern = "//ul[@id='J_PicMode']//div[@class='price-row']//b[@class='price-type']"
        ref_price_list = html.xpath(r_pattern)
        for r in ref_price_list:
            r = r.text.replace('即将上市', '0').replace('价格面议','0')
            r = r.replace('概念产品', '0').replace('停产','0')
            self.m_ref_price_list.append(r)

    def get_mobile_descript(self,html):
        # print('-' * 50, 'climb_desc')
        d_pattern = "//ul[@id='J_PicMode']//h3/a/span"
        des_list = html.xpath(d_pattern)
        for des in des_list:
            self.m_descript_list.append(des.text)

    def get_mobile_score(self,html):
        # print('-' * 50, 'climb_score')
        m_s_pattern = "//ul[@id='J_PicMode']//div[@class='comment-row']/span[@class='score']"
        m_s_list = html.xpath(m_s_pattern)
        for m_s in m_s_list:
            self.m_score_list.append(m_s.text)

    def run_reptile(self,verbose):
        self.verbose=verbose
        jd = '\r%s>%.2f%%'
        print('climb Rough information of all mobile')
        for i, m_url in enumerate(self.mobile_url):  # 每一类手机的url
            if self.verbose==0:
                a = '-' * ((i * 100) // len(self.mobile_url))
                p = (i / len(self.mobile_url)) * 100
                print(jd % (a, p), end='')

            if self.verbose==1:
                print('-' * 80, 'climb ', self.brand[i])
            m_url = m_url.replace('.html', '_0_1_2_0_')   #查看网页信息可获得规律化网站链接
            temp = m_url
            for t in range(1, 10):  # 模拟翻页    模拟多次翻页，知道最终匹配不到错误跳出遍历
                m_url = temp + str(t) + '.html'
                if self.verbose==1:
                    print('climb  ' + m_url)
                try:
                    page = requests.get(m_url, headers=header).text
                    time.sleep(0.5)
                    html = etree.HTML(page)
                    m_pattern = "//ul[@id='J_PicMode']//h3/a/@href"  # 获取各个手机对应的详细信息的url
                    mobile_list = html.xpath(m_pattern)
                    for m in mobile_list:
                        self.m_url_list.append(self.detail_root + m)  # 将url拼接成可以访问的url

                    if mobile_list:  # 如果爬取到的url为空的话说明没有没有这一页了，就停止翻页
                        pass
                    else:
                        break

                    self.get_mobile_type(html)  # 手机型号
                    self.get_mobile_reference_price(html)  # 参考价格
                    self.get_mobile_descript(html)  # 对手机的描述

                except Exception as e:
                    print(e)
                    print('-' * 50, 'error!!!')
                    break

            self.get_mobile_id(self.m_url_list)  # 手机id
            self.mobile_com = [self.brand[i]] * len(self.m_id_list)

            if self.verbose==1:
                print(len(self.m_id_list))
                print(len(self.m_type_list))
                print(len(self.m_ref_price_list))
                print(len(self.m_descript_list))
                print(len(self.m_url_list))
                print(len(self.mobile_com))

            df = pd.DataFrame({
                'id': self.m_id_list,
                'type': self.m_type_list,
                'reference_price': self.m_ref_price_list,
                'descript': self.m_descript_list,
                'url': self.m_url_list,
                'company':self.mobile_com
            })

            df.to_csv(mobile_data_path + '/' + self.brand[i].strip() + '.csv', index=None)
            if self.verbose==1:
                print('-' * 80, 'finish ', self.brand[i])

            self.m_url_list.clear()
            self.m_id_list.clear()
            self.m_type_list.clear()
            self.m_ref_price_list.clear()
            self.m_descript_list.clear()
            self.mobile_com.clear()
