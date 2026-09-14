#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import re
from urllib import request, parse
import urllib
import urllib.request
from lxml import etree
import ssl
ssl._create_default_https_context = ssl._create_unverified_context#全局取消证书验证
import requests
class Spider(Spider):  # 元类 默认的元类 type
	def getName():
		return "美剧天堂"
	def init(self,extend=""):
		print("============{0}============".format(extend))
		pass
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def homeContent(self,filter):
		result = {}
		cateManual = {
			"电影频道": "dy",
			"剧集频道":"剧集",
			"排行榜":"alltop_hit",
			"最近更新":"new100"
		}
		classes = []
		for k in cateManual:
			classes.append({
				'type_name':k,
				'type_id':cateManual[k]
			})
		result['class'] = classes
		if(filter):
			result['filters'] = self.config['filter']
		return result
	def homeVideoContent(self):
		htmlTxt =self.custom_webReadFile(urlStr='https://www.meijutt.net/',header=None,codeName='gb2312')
		root = self.html(htmlTxt)
		nodes = root.xpath('//li')
		videos = self.custom_list_search(liList=nodes)
		result = {
			'list':videos
		}
		return result
	def categoryContent(self,tid,pg,filter,extend):
		result = {}
		videos=[]
		classification=''
		if tid=='剧集':
			if 'classification' in extend.keys():
				classification=extend['classification']
			Url='https://www.meijutt.net/{1}_{2}______.html'.format(tid,pg,classification)
			xPath="//div[@class='bor_img3_right']"
		elif len(tid)>3:
			Url='https://www.meijutt.net/{0}.html'.format(tid)
			xPath="//li/h5"
		else:
			if 'classification-dy' in extend.keys():
				classification=extend['classification-dy']
			Url='https://www.meijutt.net/{0}/{1}_{2}______.html'.format(tid,pg,classification)
			xPath="//div[@class='bor_img3_right']"
		htmlTxt =self.custom_webReadFile(urlStr=Url,header=None,codeName='gb2312')
		root = self.html(htmlTxt)
		nodes = root.xpath(xPath)		
		videos = self.custom_list_search(liList=nodes)
		pagecount=0 if len(videos)<20 or len(tid)>3 else int(pg)+1
		result['list'] = videos
		result['page'] = pg
		result['pagecount'] =pagecount
		result['limit'] = 90
		result['total'] = 999999
		return result
	def detailContent(self,array):
		aid = array[0].split('###')
		idUrl=aid[1]
		title=aid[0]
		pic=aid[2]
		playFrom = []
		req=requests.get(idUrl)
		htmlTxt =self.custom_webReadFile(urlStr=idUrl,header=None,codeName='gb2312')
		root = self.html(htmlTxt)
		nodes = root.xpath('//div[@class="tabs from-tabs"]/label[contains(@class, "down")]')
		if len(nodes)<1:
			return  {'list': []}
		playFrom=[v.xpath('./text()')[0] for v in nodes ]
		videoList=[]
		vodItems = []
		circuit=root.xpath('//div[contains(@class, "down")]/ul')

		if len(nodes)<1:
			return  {'list': []}
		for v in circuit:
			vodItems=self.custom_EpisodesList(nodes=v)
			joinStr = "#".join(vodItems)
			videoList.append(joinStr)
		vod_play_from='$$$'.join(playFrom)
		vod_play_url = "$$$".join(videoList)
		typeName=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'<em>类型：</em>(.+?)<',Index=1)
		year=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'<em>时间：</em>(\d{4})',Index=1)
		area=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'<em>地区：</em>(.+?)<',Index=1)
		remarks=''
		act=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'<em>主演：</em>(.+?)<',Index=1)
		dir=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'<em>导演：</em>(.+?)<',Index=1)
		cont=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'<em>剧情介绍：</em>(.+?)</',Index=1)
		vod = {
			"vod_id": array[0],
			"vod_name": title,
			"vod_pic": pic,
			"type_name":self.custom_removeHtml(txt=typeName),
			"vod_year": self.custom_removeHtml(txt=year),
			"vod_area": area,
			"vod_remarks": remarks,
			"vod_actor":  self.custom_removeHtml(txt=act),
			"vod_director": self.custom_removeHtml(txt=dir),
			"vod_content": self.custom_removeHtml(txt=cont)
		}
		vod['vod_play_from'] = vod_play_from
		vod['vod_play_url'] = vod_play_url

		result = {
			'list': [
				vod
			]
		}
		if self.ifSkip(classText=title+typeName)==True:
				return  {'list': []}
		return result
	def writeFile(self,filePath,strTxt):
		fileJson = open(filePath,'w',encoding='gb2312', errors='ignore', newline="")
		fileJson.write(strTxt)
		fileJson.close()
	def searchContent(self,key,quick):
		key=urllib.parse.quote(key,encoding="gb2312", safe="")
		Url='https://www.meijutt.net/sousuo/index.asp?page={1}&searchword={0}&searchtype=-1'.format(key,'1')
		htmlTxt =self.custom_webReadFile(urlStr=Url,header=None,codeName='gb2312')
		root = self.html(htmlTxt)
		nodes = root.xpath('//div[@class="bor_img3_right"]')
		videos =self.custom_list_search(liList=nodes)
		result = {
			'list':videos
		}
		return result
	def playerContent(self,flag,id,vipFlags):
		result = {}
		Url=id
		parse=1
		
		result["parse"] = parse#0=直接播放、1=嗅探
		result["playUrl"] =''
		result["url"] = Url
		# result['jx'] = jx#VIP解析,0=不解析、1=解析
		result["header"] = ''	
		return result
	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]

	config = {
		"player": {},
		"filter": {
		"剧集":[
			{"key":"classification","name":"分类","value":[{"n":"全部","v":""},{"n":"魔幻科幻","v":"1"},{"n":"灵异惊悚","v":"2"},{"n":"都市情感","v":"3"},{"n":"犯罪历史","v":"4"},{"n":"选秀综艺","v":"5"},{"n":"动漫卡通","v":"6"}]}
		],
		"dy":[
			{"key":"classification-dy","name":"分类","value":[{"n":"全部","v":""},{"n":"魔幻科幻","v":"1"},{"n":"灵异惊悚","v":"2"},{"n":"剧情情感","v":"3"},{"n":"罪案动作","v":"4"},{"n":"战争历史","v":"5"},{"n":"古装冒险","v":"6"},{"n":"动画卡通","v":"40"},{"n":"传记纪录","v":"41"}]}
		]
		}
		}

	header = {
		"Referer": 'http://www.884707.com/',
		'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36',
		"Host":'www.884707.com'
		}
	#-----------------------------------------------自定义函数-----------------------------------------------
		#正则取文本
	def custom_RegexGetText(self,Text,RegexText,Index):
		returnTxt=""
		Regex=re.search(RegexText, Text, re.M|re.S)
		if Regex is None:
			returnTxt=""
		else:
			returnTxt=Regex.group(Index)
		return returnTxt	
	
	#分类取结果
	def custom_list_search(self,liList):
		videos = []
		head="https://www.meijutt.net"
		for v in liList:
			a=v.xpath('./a')
			if len(a)<1:
				continue
			title=a[0].xpath('./@title')
			if len(title)<1:
				continue
			else:
				title=title[0]
			# print(a[0].xpath("./@href")[0])
			img=a[0].xpath('./img/@src')
			if len(img)<1:
				img='https://www.meijutt.net/template/meijutt/images/logo.png'
			else:
				img=img[0]
			url=a[0].xpath("./@href")
			if len(url)<1:
				continue
			else:
				url=url[0]
			if url.find('://')<1:
				url=head+url
			if img.find('://')<1:
				img=head+img
			vod_id="{0}###{1}###{2}".format(title,url,img)
			if self.ifSkip(classText=vod_id)==True:
				continue
			videos.append({
				"vod_id":vod_id,
				"vod_name":title,
				"vod_pic":img,
				"vod_remarks":''
			})
		return videos
	
		#访问网页
	def custom_webReadFile(self,urlStr,header=None,codeName='utf-8'):
		html=''
		if header==None:
			header={
				"Referer":urlStr,
				'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36',
				"Host":self.custom_RegexGetText(Text=urlStr,RegexText='https*://(.*?)(/|$)',Index=1)
			}
		# import ssl
		# ssl._create_default_https_context = ssl._create_unverified_context#全局取消证书验证
		req=urllib.request.Request(url=urlStr,headers=header)#,headers=header
		with  urllib.request.urlopen(req)  as response:
			html = response.read().decode(codeName,'ignore')
		return html
	#判断网络地址是否存在
	def TestWebPage(self,urlStr,header=None):
		html=''
		if header==None:
			header={
				"Referer":urlStr,
				'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36',
				"Host":self.custom_RegexGetText(Text=urlStr,RegexText='https*://(.*?)(/|$)',Index=1)
			}
		try:
			req=urllib.request.Request(url=urlStr,method='HEAD')#,method='HEAD'
			with  urllib.request.urlopen(req)  as response:
				html = response.getcode () 
		except :
			html=0
		return html
	
	#取集数
	def custom_EpisodesList(self,nodes):
		videos = []
		ListLi=nodes.xpath('.//li')
		for vod in ListLi:
			title =vod.xpath("./p/strong/a/text()")[0]
			url = vod.xpath("./p/strong/a/@href")[0]
			if len(url) == 0:
				continue
			videos.append(title+"$"+url)
		# print('共:'+str(len(videos)))
		return videos
	#取剧集区
	def custom_lineList(self,Txt,mark,after):
		circuit=[]
		origin=Txt.find(mark)
		while origin>8:
			end=Txt.find(after,origin)
			circuit.append(Txt[origin:end])
			origin=Txt.find(mark,end)
		return circuit	
	#正则取文本,返回数组	
	def custom_RegexGetTextLine(self,Text,RegexText,Index):
		returnTxt=[]
		pattern = re.compile(RegexText, re.M|re.S)
		ListRe=pattern.findall(Text)
		if len(ListRe)<1:
			return returnTxt
		for value in ListRe:
			returnTxt.append(value)	
		return returnTxt
	
	#删除html标签
	def custom_removeHtml(self,txt):
		soup = re.compile(r'<[^>]+>',re.S)
		txt =soup.sub('', txt)
		return txt.replace("&nbsp;"," ")
	FilterWords=urllib.parse.unquote('%28%E4%BC%A6%E7%90%86%7C%E5%80%AB%E7%90%86%7C%E7%A6%8F%E5%88%A9%7C%E5%BC%BA%E5%A5%B8%29')
	def ifSkip(self,classText):
		b=True if self.custom_RegexGetText(Text=classText,RegexText=self.FilterWords,Index=1)!='' else False
		return b
	