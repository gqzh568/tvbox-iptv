#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import json
import time
import re
from urllib import request, parse
import urllib
import urllib.request
from xml.etree.ElementTree import fromstring, ElementTree as et
from lxml import etree

class Spider(Spider):  # 元类 默认的元类 type
	hostUrl='https://cjhwba.com/api.php/provide/vod'
	def getName():
		return "华为吧资源"#除去少儿不宜的内容
	def init(self,extend=""):
		print("============{0}============".format(extend))
		pass
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def homeContent(self,filter):
		result = {}
		cateManual ={
			'电影': '20',
		    '冒险片': '22',
		    '剧情片': '24',
		    '动作片': '26',
		    '动画电影': '28',
		    '同性片': '30',
		    '喜剧片': '32',
		    '奇幻片': '34',
		    '恐怖片': '36',
		    '悬疑片': '38',
		    '惊悚片': '40',
		    '歌舞片': '42',
		    '灾难片': '44',
		    '爱情片': '46',
		    '科幻片': '48',
		    '犯罪片': '50',
		    '经典片': '52',
		    '网络电影': '54',
		    '战争片': '56',
		    '电视剧': '60',
		    '欧美剧': '62',
		    '日剧': '64',
		    '韩剧': '66',
		    '台剧': '68',
		    '泰剧': '70',
		    '国产剧': '72',
		    '港剧': '74',
		    '新马剧': '76',
		    '其他剧': '78',
		    '动漫': '80',
		    '综艺': '82',
		    '体育': '84',
		    '纪录片': '86',
		    '篮球': '88',
		    '足球': '90',
		    '网球': '92',
		    '斯诺克': '94',
		    '欧美动漫': '96',
		    '日韩动漫': '98',
		    '国产动漫': '100',
		    '新马泰动漫': '102',
		    '港台动漫': '104',
		    '其他动漫': '106',
		    '国产综艺': '108',
		    '日韩综艺': '110',
		    '欧美综艺': '112',
		    '新马泰综艺': '114',
		    '港台综艺': '116',
		    '其他综艺': '118',
		    '短剧': '120',
		    '预告片': '122'
					
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
		xmlTxt=self.custom_webReadFile(urlStr='{0}?ac=list&h=24'.format(self.hostUrl))
		jo = json.loads(xmlTxt)
		listXml=jo['list']
		videos = self.custom_list(html=listXml)
		result = {
			'list':videos
		}
		return result
	def categoryContent(self,tid,pg,filter,extend):
		result = {}
		videos=[]
		pagecount=1
		limit=20
		total=9999
		Url='{2}?ac=list&t={0}&pg={1}'.format(tid,pg,self.hostUrl)
		xmlTxt=self.custom_webReadFile(urlStr=Url)
		jo = json.loads(xmlTxt)
		listXml=jo['list']
		pagecount=jo['pagecount']
		limit=jo['limit']
		total=jo['total']
		videos = self.custom_list(html=listXml)
		result['list'] = videos
		result['page'] = pg
		result['pagecount'] = pagecount
		result['limit'] = limit
		result['total'] = total
		return result
	def detailContent(self,array):
		result = {}
		aid = array[0].split('###')
		id=aid[1]
		logo = aid[2]
		title = aid[0]
		vod_play_from=['m3u8']
		vod_year=''
		vod_actor=''
		vod_content=''
		vod_director=''
		type_name=''
		vod_area=''
		vod_lang=''
		vodItems=[]
		vod_play_url=[]
		try:
			url='{0}/?ac=detail&ids={1}'.format(self.hostUrl,id)
			xmlTxt=self.custom_webReadFile(urlStr=url)
			jRoot = json.loads(xmlTxt)
			if jRoot['code']!=1:
				return result
			jsonList=jRoot['list']
			for vod in jsonList:
				vodItems=self.custom_EpisodesList(vod['vod_play_url'])
				joinStr = "#".join(vodItems)
				vod_play_url.append(joinStr)
			vod_year=vod['vod_year']
			vod_actor=str(vod['vod_actor'])
			vod_content=vod['vod_content']
			vod_director=str(vod['vod_director'])
			type_name=str(vod['type_name'])
			vod_area=str(vod['vod_area'])
		except Exception as e:
			print(e)
		vod = {
			"vod_id":array[0],
			"vod_name":title,
			"vod_pic":logo,
			"type_name":type_name,
			"vod_year":vod_year,
			"vod_area":vod_area,
			"vod_remarks":vod_lang,
			"vod_actor":vod_actor,
			"vod_director":vod_director,
			"vod_content":vod_content
		}
		vod_play_from.reverse()
		vod_play_url.reverse()
		vod['vod_play_from'] =  "$$$".join(vod_play_from)
		vod['vod_play_url'] = "$$$".join(vod_play_url)
		result = {
			'list':[
				vod
			]
		}
		if self.ifSkip(classText=type_name+title)==True:
			result={'list':[]}
		return result
	searchpage=1
	def searchContent(self,key,quick,pg='1'):
		if int(pg)==1:
			self.searchpage=1
		if int(pg)>self.searchpage:
			return {'list':[]}
		Url='{2}?ac=list&wd={0}&pg={1}'.format(urllib.parse.quote(key),pg,self.hostUrl)
		xmlTxt=self.custom_webReadFile(urlStr=Url)
		jo = json.loads(xmlTxt)
		listXml=jo['list']
		videos = self.custom_list(html=listXml)
		try:
			temporary=jo['pagecount']
			if int(temporary)>0:
				self.searchpage=int(temporary)
		except:
			pass
		result = {
			'list':videos
		}
		return result
	def playerContent(self,flag,id,vipFlags):
		result = {}
		parse=1
		if id.find('.m3u8')>0:
			parse=0
		result["parse"] = 1#0=直接播放、1=嗅探
		result["playUrl"] =''
		result["url"] = id
		result['jx'] = 0#VIP解析,0=不解析、1=解析
		result["header"] = ''	
		return result


	config = {
		"player": {},
		"filter": {}
		}
	header = {}
	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]
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
	def custom_list(self,html):
		ListJson=html
		videos = []
		temporary=[]
		for vod in ListJson:
			title=vod['vod_name']
		
			id=vod['vod_id']
		
			tid=vod['type_name']
		
			last=vod['vod_remarks']
			temporary.append({
				"name":title,
				"id":str(id),
				"last":last
				})
		if len(temporary)>0:
			idTxt=''
			for vod in temporary:
				idTxt=idTxt+vod['id']+','
			if len(idTxt)>0:
				url='{0}/?ac=detail&ids={1}'.format(self.hostUrl,idTxt[0:-1])
				xmlTxt=self.custom_webReadFile(urlStr=url)
				jRoot = json.loads(xmlTxt)
				if jRoot['code']!=1:
					return videos
				jsonList=jRoot['list']
				for vod in jsonList:
					title=vod['vod_name']
					vod_id=vod['vod_id']
					img=vod['vod_pic']
					remarks=vod['vod_remarks']
					type_name=vod['type_name']
					vod_year=vod['vod_year']
					if self.ifSkip(classText=type_name+title)==True:
						continue
					vod_id='{0}###{1}###{2}'.format(title,vod_id,img)
					# vod_id='{0}###{1}###{2}###{3}###{4}###{5}###{6}###{7}###{8}###{9}###{10}'.format(title,vod_id,img,vod_actor,vod_director,'/'.join(type_name),'/'.join(vod_time),'/'.join(vod_area),vod_lang,vod_content,vod_play_url)					
					# print(vod_id)
					videos.append({
						"vod_id":vod_id,
						"vod_name":title,
						"vod_pic":img,
						"vod_year":vod_year,
						"vod_remarks":remarks
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
	#取集数
	def custom_EpisodesList(self,html):
		ListRe=html.split('#')
		videos = []
		for vod in ListRe:
			t= vod.split('$')
			url =t[1]
			title =t[0]
			if len(url) == 0:
				continue
			videos.append(title+"$"+url)
		return videos
	#取分类
	def custom_classification(self):
		xmlTxt=self.custom_webReadFile(urlStr=self.hostUrl)
		tree = et(fromstring(xmlTxt))
		root = tree.getroot()
		classXml=root.iter('class')
		temporaryClass={}
		for vod in classXml:
			for value in vod:
				# print(value.text)
				if self.ifSkip(value.text)==True:
					continue
				temporaryClass[value.text]=value.attrib['id']
		return temporaryClass
	FilterWords=urllib.parse.unquote('%28%E4%BC%A6%E7%90%86%7C%E5%80%AB%E7%90%86%7C%E7%A6%8F%E5%88%A9%7C%E5%BC%BA%E5%A5%B8%29')
	def ifSkip(self,classText):
		b=True if self.custom_RegexGetText(Text=classText,RegexText=self.FilterWords,Index=1)!='' else False
		return b
