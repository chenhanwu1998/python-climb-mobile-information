import requests
import re
import time
import pandas as pd
from lxml import etree
from reptile_project.gzc_climb import param
data_path=param.data_path
mobile_data_path=param.mobile_data_path
param_data_path=param.param_data_path
evaluate_data_path= param.evaluate_data_path
header=param.header

class mobile_param_evaluate:
    def __init__(self):
        self.data = pd.read_csv(data_path)
        self.brand_list = self.data['品牌']
        self.detail_root = 'http://detail.zol.com.cn'
        self.params_dic = {'id': [],  'CPU':[],'上市日期': [], '主屏尺寸': [], '主屏分辨率': [], '后置摄像头': [], '前置摄像头': [], '电池容量': [], '电池类型': [],
                      '核心数': [], '内存': [], 'param_url': []}
        self.evaluate_dic = {'id': [],'性价比': [], '性能': [], '续航': [], '外观': [], '拍照': [], '4-5星': [], '3-4星': [], '2-3星': [],
                        '1-2星': [], 'score': [], 'descript': [], 'evaluate_url': []}
        self.temp_params_dic = {'id': 'None', 'CPU': 'None', '上市日期': 'None', '主屏尺寸': 'None', '主屏分辨率': 'None', '后置摄像头': 'None', '前置摄像头':'None',
                           '电池容量':'None', '电池类型': 'None',
                           '核心数': 'None', '内存': 'None', 'param_url': 'None'}
        self.temp_evaluate_dic = {'id': 'None', '性价比': 'None', '性能': 'None', '续航': 'None', '外观': 'None', '拍照': 'None', '4-5星': 'None', '3-4星': 'None',
                             '2-3星':'None',
                             '1-2星': 'None', 'score': 'None', 'descript': 'None', 'evaluate_url': 'None'}
        self.verbose=1

    def get_mobile_param(self,param_url):
        #获取手机的上市日期和CPU型号，顺便做了简单初步去噪

        if self.verbose==1:
            print('-' * 50, 'cimlb param ', param_url)
        self.temp_params_dic['param_url']=param_url

        param_page = requests.get(param_url, headers=header).text  # 参数url
        # time.sleep(0.5)
        param_html = etree.HTML(param_page)

        date_pattern = "//span[@id='newPmVal_0']"
        an_dt_pattern = date_pattern + "/a"
        label = "//span[@id='newPmName_0']"
        dt = param_html.xpath(date_pattern)
        an_dt = param_html.xpath(an_dt_pattern)
        lab = param_html.xpath(label)

        temp_date='None'
        if lab and lab[0].text == '上市日期':
            if dt and dt[0].text:
                temp_date=dt[0].text
            elif an_dt:
                temp_date=an_dt[0].text.replace('>', '')

        self.temp_params_dic['上市日期']=temp_date

        pt = "//div[@class='wrapper clearfix mt30']//div[@class='box-item-fl ']"
        label = pt + "//label[@class='name']"
        an_pt = "//span[@id='newPmVal_3']"
        xinhao = "//a[@id='newPmName_3']"
        lab = param_html.xpath(label)
        cpu_con = param_html.xpath(pt)
        an_cpu_con = param_html.xpath(an_pt)
        xinhao = param_html.xpath(xinhao)

        temp_cpu='None'
        if cpu_con:
            if lab[0].text == 'CPU：':
                cpu_con = param_html.xpath(pt)[0].xpath('string(.)')
                cpu_con = cpu_con.replace('\t', '').replace('\r', '').replace(' ', '')
                cpu_list = [t for t in cpu_con.split('\n') if len(t) != 0]
                temp_cpu=cpu_list[0].split('：')[1].split('游戏')[0].split('手机')[0]
            else:
                temp_cpu='None'

        elif an_cpu_con:
            if xinhao and xinhao[0].text == 'CPU型号':
                an_cpu_con = an_cpu_con[0].xpath('string(.)')
                cpu = an_cpu_con.split('更多')[0]
                cpu = cpu.split('手机')[0]
                temp_cpu=cpu.split('游戏')[0]
            else:
                temp_cpu='None'
        else:
            temp_cpu='None'

        self.temp_params_dic['CPU']=temp_cpu

    def get_mobile_detail_param(self,html):
        zp_pattern = "//div[@class='wrapper clearfix']//ul[@class='product-param-item pi-57 clearfix']//li"
        key_list = ['主屏尺寸', '主屏分辨率', '后置摄像头', '前置摄像头', '电池容量', '电池类型', '核心数', '内存']
        param = html.xpath(zp_pattern)
        if len(param)!=0:  #样式还是老版的情况下的爬虫
            params = ''
            for pa in param:
                params += pa.xpath('string(').replace('\t', '').replace('\r', '')
            p_list = params.split('\n')
            real_p = [r for r in p_list if len(r) != 0]

            temp_dic={}   #先用字典缓存起来
            for r in real_p:
                r_cell = r.split('：')
                try:  # 在此可能有其他杂质出现try一下
                    temp_dic[r_cell[0]]=r_cell[1]
                except:
                    pass

            for key in key_list:  #将缓存写入类字典中去
                if key in temp_dic.keys():
                    self.temp_params_dic[key]=temp_dic[key]
                else:
                    self.temp_params_dic[key]='None'

        else:  #新样式爬虫，网站样式排版改变后，再加上另外一种分析机制
            zp_pattern='//*[@id="secondsUnderstand"]//div[@class="tab-con"]//div[@class="info-list-01"]//ul'
            key_list1 = ['屏幕', '分辨率', '后置', '前置', '电池', '内存']
            key_list2=['主屏尺寸', '主屏分辨率', '后置摄像头', '前置摄像头', '电池容量', '内存']
            param=html.xpath(zp_pattern)
            if param: #判断是否存在先
                param=param[0]
            param=param.xpath('string(.)').replace('\t', '').replace('\r', '').replace(' ','')  #获取所有的在这个标签内的东西后再做分割
            param_list = param.split('\n')
            param_list = [p for p in param_list if len(p) != 0 and '：' in p] #顺便去掉一些噪音字符
            temp_param = {}
            for temp_p in param_list:
                cell = temp_p.split('：')
                if cell[0] in key_list1:
                    temp_param[cell[0]] = cell[1]

            for i,key in enumerate(key_list1):  #可能有些情况下爬取不到分辨率等这些，需要做个判断然后置none ，血腥报错
                if key in temp_param.keys():
                    self.temp_params_dic[key_list2[i]]=temp_param[key]
                else:
                    self.temp_params_dic[key_list2[i]]='None'

            for key in key_list:  #对params_dic中的key没有在keylist2中的参数置为none
                if key not in key_list2:
                    self.temp_params_dic[key]='None'

    def get_eva_score(self,html):
        #获取评价指标，将指标写入字典中存储

        eva_v_pattern = "//div[@class='wrapper']//div[@class='circle-value']"
        eva_t_pattern = "//div[@class='wrapper']//div[@class='circle-text']"
        eva_v_list = html.xpath(eva_v_pattern)
        eva_t_list = html.xpath(eva_t_pattern)
        eva_value_list = ['None', 'None', 'None', 'None', 'None']
        eva_text_list = ['性价比', '性能', '续航', '外观', '拍照']
        eva_dic = dict(zip(eva_text_list, eva_value_list))

        for i, eva_t in enumerate(eva_t_list):
            try:
                eva_dic[eva_t.text] = eva_v_list[i].text
            except:
                break

        for k, v in eva_dic.items():
            self.temp_evaluate_dic[k]=v

    def get_xin_score(self,html):
        eva_s_pattern = "//div[@class='wrapper']//ul[@class='comments-level']//var"
        eva_s_list = html.xpath(eva_s_pattern)
        if eva_s_list:  #判断是否存在
            self.temp_evaluate_dic['4-5星']=eva_s_list[0].text
            self.temp_evaluate_dic['3-4星']=eva_s_list[1].text
            self.temp_evaluate_dic['2-3星']=eva_s_list[2].text
            self.temp_evaluate_dic['1-2星']=eva_s_list[3].text

    def get_score(self,html):
        #获取得分
        eva_s_pattern = "//div[@class='wrapper']//div[@class='total-score']/strong"
        eva_score = html.xpath(eva_s_pattern)
        if eva_score:
            self.temp_evaluate_dic['score']=eva_score[0].text

    def get_descript(self,html):
        #获取手机的相关描述
        peo_d_pattern = "//ul[@id='_j_words_filter']//a"
        peo_des_list = html.xpath(peo_d_pattern)
        peo_descript_list = []
        for peo_d in peo_des_list:
            peo_descript_list.append(peo_d.text)
        if peo_des_list:  #存在的话
            self.temp_evaluate_dic['descript'] = '、'.join(peo_descript_list)

    def get_mobile_evaluate(self,evaluate_url):
        if self.verbose==1:
            print('-' * 50, 'climb evaluate ', evaluate_url)
        self.temp_evaluate_dic['evaluate_url']=evaluate_url
        evaluate_page = requests.get(evaluate_url, headers=header).text  # 评论url
        # time.sleep(0.5)
        html = etree.HTML(evaluate_page)
        self.get_eva_score(html)
        self.get_xin_score(html)
        self.get_score(html)
        self.get_descript(html)

    def get_mobile_id(self,m_url):
        pattern = 'index(.*?)\.shtml'
        id_ = re.findall(re.compile(pattern=pattern), m_url)
        self.temp_params_dic['id']=id_[0]
        self.temp_evaluate_dic['id']=id_[0]

    def check_dic(self):
        # 输出一下长度做检查
        for k in self.evaluate_dic.keys():
            print(k, ":", len(self.evaluate_dic[k]))
        for k in self.params_dic.keys():
            print(k, ":", len(self.params_dic[k]))

    def clear_dic(self):
        #将主字典清空
        for k in self.params_dic.keys():
            self.params_dic[k].clear()
        for k in self.evaluate_dic.keys():
            self.evaluate_dic[k].clear()

    def clear_temp_dic(self):
        #将临时字典清空
        for k in self.temp_params_dic.keys():
            self.temp_params_dic[k]='None'
        for k in self.temp_evaluate_dic.keys():
            self.temp_evaluate_dic[k]='None'

    def run_climb(self,verbose):
        self.verbose=verbose
        #主跑函数
        stop=1
        for brand in self.brand_list:

            # if brand.strip() != 'VERTU' and stop == 1:   #控制从哪个开始爬取,从VERTU这个手机厂家开始爬去
            #     continue
            # else:
            #     stop = 0

            global count
            count=0
            d_path = mobile_data_path + '/' + brand.strip() + '.csv'
            if self.verbose==1:
                print('-' * 100, 'climb ', brand)
                print(d_path)
            data_df = pd.read_csv(d_path)
            mobile_url_list = data_df['url']

            jd = '\r%s%s->%.2f%%'
            for i,m_url in enumerate(mobile_url_list):
                count += 1
                if self.verbose==0:
                    a = '-' *((i * 100) //len(mobile_url_list))
                    p = (i / len(mobile_url_list)) * 100
                    print(jd % (brand,a, p), end='')

                if self.verbose==1:
                    print('-' * 120, str(count))
                    print('-' * 80, 'climb ', m_url)

                page = requests.get(m_url, headers=header).text
                html = etree.HTML(page)    #综述页面

                pattern = "//div[@id='_j_tag_nav']/ul/li[4]/a/@href"
                temp_url = html.xpath(pattern)  # 获取参数的链接

                if temp_url:   #如果有此链接，才调到此处继续，否则直接跳过所有一下操作
                    temp_url=temp_url[0]  #如果有就取出第一个
                    pass
                else:
                    continue

                find_patten = '/(\d+/\d+).*shtml'
                real_url_id=re.findall(find_patten,temp_url)[0]
                param_url=self.detail_root+'/'+real_url_id+'/param.shtml'
                evaluate_url=self.detail_root+'/'+real_url_id+'/review.shtml'

                # self.temp_params_dic['id']=real_url_id
                # self.temp_evaluate_dic['id']=real_url_id
                self.get_mobile_id(m_url)   #获取id
                self.get_mobile_detail_param(html)
                self.get_mobile_param(param_url)
                self.get_mobile_evaluate(evaluate_url)

                for k,v in self.temp_params_dic.items():
                    self.params_dic[k].append(v)
                for k,v in self.temp_evaluate_dic.items():
                    self.evaluate_dic[k].append(v)

                if self.verbose==1:
                    print(self.temp_params_dic)
                    print(self.temp_evaluate_dic)
                self.clear_temp_dic()  #清楚临时字典

            # self.check_dic()  #输出检查一下具体字典的长度
            param_data_to_path = param_data_path + '/param_' + brand.strip() + '.csv'
            evaluate_data_to_path = evaluate_data_path + '/evaluate_' + brand.strip() + '.csv'
            param_df = pd.DataFrame(self.params_dic)  #装成pandas数据模式
            evaluate_df = pd.DataFrame(self.evaluate_dic)

            param_df.to_csv(param_data_to_path, index=None)   #存储成csv文件
            evaluate_df.to_csv(evaluate_data_to_path, index=None)
            self.clear_dic()  # 清掉词典