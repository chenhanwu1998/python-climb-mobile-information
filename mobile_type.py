from reptile_project.gzc_climb import param
import requests
import pandas as pd
from lxml import etree
import numpy as np
data_path=param.data_path
header=param.header

class m_type:
    def __init__(self):
        self.mobile_brand_url = 'http://top.zol.com.cn/compositor/57/manu_attention.html'
        self.root_pattern="//div[@class='main']//div[@class='rank-list brand-rank-list']//div[@class='rank-list__item clearfix']"
        self.brand_url=[]
        self.brand_name = []
        self.score_list = []
        self.occupancy_list = []
        self.evaluate_list = []
        self.low_price = []
        self.high_price = []

    def get_brand_url(self,html):
        b_pattern = self.root_pattern + "//div[@class='brand_logo']/p/a/@href"
        brand_url_list = html.xpath(b_pattern)
        for u in brand_url_list:
            self.brand_url.append(u)
            # print(b)

    def get_brand_name(self,html):
        b_pattern = self.root_pattern + "//div[@class='brand_logo']/p/a"
        brand = html.xpath(b_pattern)
        for t in brand:
            self.brand_name.append(t.text.strip())
            #print(t.text)

    def get_score(self,html):
        s_pattern = self.root_pattern + "//div[@class='score clearfix']//span"
        score = html.xpath(s_pattern)
        for s in score:
            self.score_list.append(s.text.replace('分', '').replace('%',''))
            #print(s.text.replace('分', ''))

    def get_occupancy(self,html):
        o_pattern = self.root_pattern + "//div[@class='rank-list__cell cell-4']"
        occupancy = html.xpath(o_pattern)

        for o in occupancy:
            self.occupancy_list.append(o.text.strip().replace('-','0').replace('%',''))
            #print(o.text.strip())

    def get_evaluate(self,html):
        e_pattern = self.root_pattern + "//div[@class='rank-list__cell cell-6']"
        evaluate = html.xpath(e_pattern)
        for e in evaluate:
            self.evaluate_list.append(e.text.replace('%',''))
            #print(e.text)

    def get_price(self,html):
        p_pattern = self.root_pattern + "//div[@class='rank__price']"
        price = html.xpath(p_pattern)
        for p in price:
            p = p.text.replace('&yen', "").replace('暂无报价', '0-0')
            p = p.split('-')
            self.low_price.append(p[0])
            if len(p) == 2:
                self.high_price.append(p[1])
            else:
                self.high_price.append(p[0])
        # for i in range(len(self.low_price)):
        #     print('￥', self.low_price[i], " ", self.high_price[i])


    def climb_m_type(self):
        response = requests.get(self.mobile_brand_url,headers=header)
        page = response.text
        html = etree.HTML(page)

        self.get_brand_url( html)
        self.get_brand_name(html)
        self.get_score(html)
        self.get_occupancy(html)
        self.get_evaluate(html)
        self.get_price(html)

        url_list = np.array(self.brand_url)
        brand_list = np.array(self.brand_name)
        score_list = np.array(self.score_list)
        occupancy_list = np.array(self.occupancy_list)
        low_price = np.array(self.low_price)
        high_price = np.array(self.high_price)
        evaluate_list = np.array(self.evaluate_list)

        data = pd.DataFrame({
            '品牌': brand_list,
            '品牌综合评分': score_list,
            '品牌占有率': occupancy_list,
            '好评率': evaluate_list,
            '最低价': low_price,
            '最高价': high_price,
            'url': url_list
        })
        data.to_csv(data_path, index=None)
        print('-'*50,'finished climb type!')