import requests
import re
from fontTools.ttLib import TTFont

#获得响应文本
def page(url):
    headers={
        'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                     'Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.81'
    }
    response = requests.get(url=url, headers=headers)
    return response.text

#获取字体文件
def font_(page):
    url = re.findall("format\('eot'\); src: url\('(.*?)'\) format\('woff'\)", page)[0]
    headers = {
     'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) ' 
                   'Chrome/88.0.4324.182 Safari/537.36 Edg/88.0.705.81'
    }
    response = requests.get(url=url, headers=headers)
    font_data = response.content
    with open('jiami.woff', 'wb')as f:
         f.write(font_data)

#解密月票获得对应关系字典
def dic_o():

    #解密字体文件获得对应关系字典best_map
    font = TTFont('jiami.woff')
    font.saveXML('font4.xml')
    best_map = font.getBestCmap()

    #将英文转化为阿拉伯数字
    dic_e_a={'one':'1', 'two':'2', 'three':'3','four':'4','five':'5','six':'6','seven':'7','eight':'8','nine':'9','zero':'0'}
    for i in best_map:
        for j in dic_e_a:
            if j == best_map[i]:
                best_map[i]=dic_e_a[j]

    return best_map

#通过对应关系替换加密月票密文并去分号,参数result1为加密月票数组，reault2为对应关系
def replace(result1, result2):
    list=[]
    for i in result1:
        for j in sorted(result2.keys()):
            pattern = re.compile(r'{}'.format(j))                  #正则表达式中有变量要使用方法format(),变量区域用{}
            i = re.sub(pattern,result2[j],i)
            i = re.sub(';', '', i)
        list.append(i)
    return list

def main():
    start = input('请输入要开始的页数:')
    number = input('请输入爬取页数:')
    result=[]
    result_i=[]
    for number in range(int(start), int(start)+int(number)):  # 翻页
        url = 'https://www.qidian.com/rank/yuepiao?page=' + str(number)                    # 匹配不同页的url
        one_page = page(url)                                                               # 调用函数获得响应文本

        pattern = re.compile('<span class="rank-tag no.*? ">(.*?)<cite></cite></span>.*?<div class="book-mid-info">'
                             '.*?data-bid=".*?">(.*?)</a></h4>', re.S)                     # 密封解析书名的正则表达式

        resul = re.findall(pattern, one_page)                                             # 获得书名数组result
        for i in resul:
            result.append(i)

        resul_i = re.findall('</style><span class=".*?">(.*?);</span></span>', one_page)  # 获得加密的月票数组result_i
        for i in resul_i:
            result_i.append(i)

    #去除加密月票数的&#符号得到新数组new_result_i
    new_result_i = []
    for i in result_i:
        j = re.sub('&#', '', i)
        new_result_i.append(j)


    #获取字体文件
    font_(one_page)
    #利用函数dic_o()解密，获得密文对应关系字典list
    list = dic_o()


    #利用函数replace()替换加密的月票数组new_result_i的到月票数组new_result
    new_list = replace(new_result_i, list)

    # 加工书名
    new_name = []
    for i in result:
        name = '第' + i[0] + '名:' + i[1]
        new_name.append(name)

    #将月票数组和书名数组合并为字典
    dic={}
    for i in range(0, int(number)*20):
        dic[new_name[i]] = new_list[i]
    #存储并打印结果
    with open('qidian.text', 'w') as f:
        for name in dic.keys():
            f.write(name+':'+dic[name]+'票\n')
            print(name+':'+dic[name]+'票    存储成功')

main()