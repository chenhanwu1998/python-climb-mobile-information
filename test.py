# import  requests
# from  lxml import  etree
# from reptile_project.gzc_climb import  param
# header=param.header
#
# url='http://detail.zol.com.cn/cell_phone/index1268851.shtml'
# response=requests.get(url,headers=header)
# text=response.text
# pattern='//*[@id="secondsUnderstand"]//div[@class="tab-con"]//div[@class="info-list-01"]//ul'
# html=etree.HTML(text)
# li_list=html.xpath(pattern)[0]
#
# content=li_list.xpath('string(.)').replace('\t', '').replace('\r', '').replace(' ','')
# print(content)
# param_list=content.split('\n')
# print(param_list)
#
# param_list=[p for p in param_list if len(p)!=0 and '：' in p]
# print(param_list)
# temp_param={}
# for temp_p in param_list:
#     cell=temp_p.split('：')
#     temp_param[cell[0]]=cell[1]
# print(temp_param)


import re
str='http://detail.zol.com.cn/1267/1267000/pic.shtml'
patten='/(\d+/\d+).*shtml'
dealout=re.findall(patten,str)
print(dealout)
