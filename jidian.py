#!/usr/bin/env python3 
#coding=utf-8
#Author: Bluefissure
import sys
import requests
import getpass
import json
import time
import codecs
from hashlib import md5
urlbase='http://bkjws.sdu.edu.cn'
#urlbase='http://202.194.15.19' #If domain cannot be accessed
def login(req,username,password):
	urlLogin=urlbase+'/b/ajaxLogin'
	m = md5()
	m.update(password.encode())
	password = m.hexdigest()
	data = {
		"j_username": username,
		"j_password": password,
	}
	try:
		headers = {
			'Content-Type': 'application/x-www-form-urlencoded',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
			'Accept': '*/*',
			'Origin': urlbase+'',
			'Connection': 'keep-alive',
			'Accept-Language': 'zh-CN,zh;q=0.8',
			'Accept-Encoding':'gzip, deflate',
			'Host': 'bkjws.sdu.edu.cn'
		}
		res = req.post(url=urlLogin, headers=headers, data=data)
		if not "success" in res.text:
			print(res.text)
			return False
		return True
	except Exception as e:
		print("Login Error: %s"%e)
		sys.exit()

def getRawScore(req):
	print("开始获取成绩数据")
	url = urlbase+'/b/cj/cjcx/xs/lscx'
	data = {"aoData":'[{"name":"sEcho","value":1},{"name":"iColumns","value":10},{"name":"sColumns","value":""},{"name":"iDisplayStart","value":0},{"name":"iDisplayLength","value":1000},{"name":"mDataProp_0","value":"xnxq"},{"name":"mDataProp_1","value":"kch"},{"name":"mDataProp_2","value":"kcm"},{"name":"mDataProp_3","value":"kxh"},{"name":"mDataProp_4","value":"xf"},{"name":"mDataProp_5","value":"kssj"},{"name":"mDataProp_6","value":"kscjView"},{"name":"mDataProp_7","value":"wfzjd"},{"name":"mDataProp_8","value":"wfzdj"},{"name":"mDataProp_9","value":"kcsx"},{"name":"iSortCol_0","value":5},{"name":"sSortDir_0","value":"desc"},{"name":"iSortingCols","value":1},{"name":"bSortable_0","value":false},{"name":"bSortable_1","value":false},{"name":"bSortable_2","value":false},{"name":"bSortable_3","value":false},{"name":"bSortable_4","value":false},{"name":"bSortable_5","value":true},{"name":"bSortable_6","value":false},{"name":"bSortable_7","value":false},{"name":"bSortable_8","value":false},{"name":"bSortable_9","value":false}]'}
	res = req.post(url=url, data=data)
	json_data = json.loads(res.text)
	if json_data["result"]!="success":
		print(json_data["result"])
		return False
	return json_data

def parseScore(data):
	print("开始处理成绩数据")
	datalist = data["object"]["aaData"]
	xuehao = datalist[0]["xh"]
	title = ["课程号","课程名","课序号","学号","考试时间","教师号","上课学期","学分","学时","课程属性","考试成绩","最终成绩","考查成绩","重修补考标志","是否gd","bz","期末成绩","录入时间","操作人","平时成绩","实验成绩","期中成绩","tdkch","考试类型","bz2","bz3","kslb","五分制等级","五分制成绩","id"]
	strid = ["kch","kcm","kxh","xh","kssj","jsh","xnxq","xf","xs","kcsx","kscj","kscjView","kccj","cxbkbz","sfgd","bz","qmcj","lrsj","czr","pscj","sycj","qzcj","tdkch","kslx","bz2","bz3","kclb","wfzdj","wfzjd","id"]
	with codecs.open("Score_%s.csv"%(xuehao),"w",'utf_8_sig') as f:
		for item in title:
			f.write(item+",")
		f.write("\n")
		sum_credit = 0
		sum_5 = 0
		sum_100 = 0
		for score in datalist:
			for idname in strid:
				f.write("%s,"%(score[str(idname)]))
			f.write("\n")
			if (("必修" in score["kcsx"]) or ("限选" in score["kcsx"])) and not score["cxbkbz"]:
				xf = float(score["xf"])
				score_100 = abs(float(score["kscj"]))
				score_5 = abs(float(score["wfzjd"]))
				sum_credit += xf
				sum_100 += score_100*xf
				sum_5 += score_5*xf
				print("%s：%s 学分：%s 百分制：%s 五分制：%s"%(score["kcsx"],score["kcm"],xf,score_100,score_5))
		jidian_100 = sum_100/sum_credit
		jidian_5 = sum_5/sum_credit
		f.write("百分制绩点:%s,\n"%(jidian_100))
		f.write("五分制绩点:%s,\n"%(jidian_5))
		f.close()
		print("%s 的百分制绩点为 %s"%(xuehao,jidian_100))
		print("%s 的五分制绩点为 %s"%(xuehao,jidian_5))
	

try:
	req = requests.Session()
	username = input("请输入学号:\n")
	password = getpass.getpass("请输入密码(回显关闭):\n")
	if not login(req,username,password):
		print("登陆失败")
	else:
		print("登陆成功")
		data = getRawScore(req)
		if not data:
			print("获取成绩失败")
		else:
			print("成功获取成绩")
			parseScore(data)
except Exception as e:
	print("Error: %s"%e)
	if "Permission denied" in str(e):
		print("请关闭打开的csv文件")
	else:
		raise e