#!/usr/bin/python  
#Author: Bluefissure
#Update time: 2017-1-5
import sys
import urllib
import urllib.request
import urllib.parse
import getpass
import json
import http.cookiejar
import time

def login(username,password):
	urlLogin='http://bkjwxk.sdu.edu.cn/b/ajaxLogin'
	
	data = {
		"j_username": username,
		"j_password": password,
	}
	data = urllib.parse.urlencode(data).encode('utf-8')
	try:
		headers = {
			'Content-Type': 'application/x-www-form-urlencoded',
			'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
			'Accept': '*/*',
			'Origin': 'http://bkjwxk.sdu.edu.cn',
			'Connection': 'keep-alive',
			'Accept-Language': 'zh-CN,zh;q=0.8',
			'Accept-Encoding':' gzip, deflate',
			'Host': 'bkjwxk.sdu.edu.cn'
		}
		request = urllib.request.Request(url=urlLogin, headers=headers, data=data)
		cookie = http.cookiejar.CookieJar()
		opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie))
		
		r = opener.open(request) 
		response = r.read().decode('utf-8')
		print(response)
		if(response!='"success"'): 
			print("登陆失败")
			sys.exit()
		print("登陆成功")
		return cookie;
	except Exception as e:
		print("Login Error: %s"%e)


def xuanke(kch,kxh,cookie):
	try:
		urlXuanke='http://bkjwxk.sdu.edu.cn/b/xk/xs/add/%s/%s'%(kch,kxh)
		request = urllib.request.Request(url=urlXuanke)
		cj = cookie
		opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
		r = opener.open(request) 
		response = r.read().decode('utf-8')
		result = json.loads(response)["msg"]
		print(result)
		return("选课成功" in result)
	except Exception as e:
		print("Check Error: %s"%e)


def checkLeft(kch,kxh,cookie):
	try:
		urlCheck='http://bkjwxk.sdu.edu.cn/b/xk/xs/kcsearch'
		curPage = 1
		totPage = 100
		find = False
		while(curPage <= totPage and not find):
			# print("curPage %d"%curPage)
			# print("totPage %d"%totPage)
			# print("kch %s"%kch)
			data = {
					"type": "kc",
					"currentPage": curPage,
					"kch": kch,
					"jsh": "",
					"skxq": "",
					"skjc": "",
					"kkxsh": ""
					}
			data = urllib.parse.urlencode(data).encode('utf-8')

			# for item in cookie:
			# 	print('%s : %s' % (item.name,item.value))
			headers = {
				'Content-Type': 'application/x-www-form-urlencoded',
			}
			request = urllib.request.Request(url=urlCheck, headers=headers, data=data)
			cj = cookie
			opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
			r = opener.open(request) 
			response = r.read().decode('utf-8')
			jsondata = json.loads(response)

			totPage = int(jsondata["object"]["totalPages"])
			curPage = curPage + 1

			for item in jsondata["object"]["resultList"]:
				if(int(item.get("KXH"))==int(kxh)):
					print(item)
					find = True
					if(int(item.get("kyl"))>0):
						if(xuanke(kch,kxh,cookie)):
							print("课程\"%s\"选课成功，谢谢使用\nBy Bluefissure"%(item.get("KCM")))
							sys.exit()
					else:
						print("课程\"%s\"课余量不足，您需要等待至少 %s 人退课"%(item.get("KCM"),-int(item.get("kyl"))+1))
					break

			if(not find):
				print("找不到该课程，请确认课程号、课序号!")
				sys.exit()
	except Exception as e:
		print("Check Error: %s"%e)





try:
	username = input("请输入学号:\n")
	password = getpass.getpass("请输入密码(回显关闭):\n")
	cookie = login(username,password)
	kch = input("请输入课程号\n")
	kxh = input("请输入课序号\n")
	dT = input("请输入刷新时间(秒):\n")
	if(float(dT)<1):
		print("刷新频率太快，下降至1次/秒")
		dT=1
	iterator = 0
	while(True):
		iterator = iterator + 1
		if(iterator % 600 ==0):
			print("Cookie expire, relogining...")
			cookie = login(username,password)
		print("开始第%d次尝试，时间为%s"%(iterator,time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))))
		checkLeft(kch,kxh,cookie)
		time.sleep(float(dT))

except Exception as e:
	print("Error: %s"%e)