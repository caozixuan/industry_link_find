# coding=utf-8
from django.shortcuts import render
import os
import re
import jieba
import jieba.posseg as pseg
import urllib.parse
import urllib.request
from industry.models import Company, Industry, Dictionary

rule_up = [r'(.*)上游(.*)',r'使用(.*)']
rule_down = [r'(.*)下游(.*)',r'(.*)行业下游情况(.*)',r'应用于(.*)']
rule_mid = [r'主营业务(.*)']
rule_company = r'(.*)股份有限公司'

def rename():
    path = 'D:\\temp_data\\temp_data'
    all_file_list = os.listdir(path)
    counter = 1
    for file_name in all_file_list:
        currentdir = os.path.join(path, file_name)
        fname = os.path.splitext(file_name)[0]  # 分解出当前的文件路径名字
        ftype = os.path.splitext(file_name)[1]  # 分解出当前的文件扩展名
        fname = str(counter)
        ftype = ".txt"
        print(fname + ftype)
        newname = os.path.join(path, fname + ftype)  # 文件路径与新的文件名字+原来的扩展名
        os.rename(currentdir, newname)  # 重命名
        counter = counter + 1


def file_name(file_dir):
    L = []
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            if os.path.splitext(file)[1] == '.txt':
                L.append(os.path.join(root, file))
    return L


def get_FileSize(filePath):
    fsize = os.path.getsize(filePath)
    fsize = fsize/float(1024)
    return fsize


def baidu_search(keyword):
    url = "http://www.baidu.com/s"
    search = [('w', keyword)]
    getString = url + "?" + urllib.parse.urlencode(search)
    req = urllib.request.Request(getString)
    response = urllib.request.urlopen(req)
    baiduResponse = str(response.read(), 'utf-8')
    if (baiduResponse.find('<em>'+keyword+'</em>') > -1):
        print(keyword+"加入词典")
        return True
    #if('<em>'+keyword+'</em>') in baiduResponse:
        #print(keyword)
        #return True
    return False


def is_in_dic(name):
    words = Dictionary.objects.all()
    for word in words:
        if name==word.name:
            return word.is_industry
    Dictionary.objects.create(name=name)
    new_word = Dictionary.objects.get(name=name)
    if baidu_search(name+"行业"):
        new_word.is_industry=True
        Industry.objects.get_or_create(name=name)
    return new_word.is_industry


def collect_data(pattern):
    names = file_name('D:\\temp_data\\temp_data')
    if pattern==0:
        for rule in rule_up:
            compile_name = re.compile(rule, re.M)
            company_rule = re.compile(rule_company, re.M)
            for name in names:
                # print (x+1)
                if os.path.getsize(name)/float(1024)<100:
                    continue
                f = open(name,errors='ignore')
                st = f.read()
                res_name = compile_name.finditer(st)
                company_name = company_rule.finditer(st)
                y=0
                name_company = ""
                for x in company_name:
                    if y==0:
                        name_company=x.group()
                    y = y+1
                if y>0:
                    Company.objects.get_or_create(name=name_company)
                else:
                    continue
                for m in res_name:
                    seg_list = jieba.cut(m.group(), cut_all=True)
                    for word in seg_list:
                        industries = Industry.objects.all()
                        print (word)
                        is_industry = is_in_dic(word)
                        if not is_industry:
                            continue
                        elif is_industry:
                            for industry in industries:
                                if word == industry.name:
                                    company = Company.objects.filter(name=name_company)
                                    company[0].up_link.add(industry)
                                    company[0].save()
    elif pattern==1:
        for rule in rule_down:
            compile_name = re.compile(rule, re.M)
            for name in names:
                # print (x+1)
                if(get_FileSize('D:\\temp_data\\temp_data\\'+name)<100):
                    break
                f = open(name)
                st = f.read()
                res_name = compile_name.finditer(st)
                company_rule = re.compile(rule_company, re.M)
                company_name = company_rule.finditer(st)
                if(len(company_name)>0):
                    company=Company.objects.get_or_create(name=company_name[0])
                else:
                    break
                for m in res_name:
                    seg_list = jieba.cut(m.group(), cut_all=True)
                    for word in seg_list:
                        industries = Industry.objects.all()
                        if baidu_search(word):
                            Industry.objects.create(name=word)
                            industry = Industry.objects.get(name=word)
                            company.down_link=industry
                            company.save()
                        else:
                            for industry in industries:
                                if word == industry.name:
                                    company.down_link = industry
                                    company.save()
                                    break
    elif pattern==2:
        for rule in rule_down:
            compile_name = re.compile(rule, re.M)
            for name in names:
                # print (x+1)
                if(get_FileSize('D:\\temp_data\\temp_data\\'+name)<100):
                    break
                f = open(name)
                st = f.read()
                res_name = compile_name.finditer(st)
                company_rule = re.compile(rule_company, re.M)
                company_name = company_rule.finditer(st)
                if(len(company_name)>0):
                    company=Company.objects.get_or_create(name=company_name[0])
                else:
                    break
                for m in res_name:
                    seg_list = jieba.cut(m.group(), cut_all=True)
                    for word in seg_list:
                        industries = Industry.objects.all()
                        if baidu_search(word):
                            Industry.objects.create(name=word)
                            industry = Industry.objects.get(name=word)
                            company.mid_link=industry
                            company.save()
                        else:
                            for industry in industries:
                                if word == industry.name:
                                    company.mid_link = industry
                                    company.save()
                                    break


def filter_data():
    values = Dictionary.objects.all()
    for value in values:
        words = pseg.cut(value.name)
        for word, flag in words:
            if flag=='n':
                value.is_industry = True
            else:
                value.is_industry = False
        if value.is_industry:
            print(value.name)

