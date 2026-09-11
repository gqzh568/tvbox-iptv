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
import requests

class Spider(Spider):  # 元类 默认的元类 type
	hostUrl=''
	def getName():
		return "魔都资源"#除去少儿不宜的内容
	def init(self,extend=""):
		self.hostUrl=extend

	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def homeContent(self,filter):
		result = {}
		cateManual ={
			"国产动漫":"1"
			"日韩动漫":"2"
			"欧美动漫":"3"
			"港台动漫":"4"
			"动漫电影":"5"
			"动作片":"10"
			"喜剧片":"11"
			"爱情片":"12"
			"科幻片":"13"
			"恐怖片":"14"
			"剧情片":"15"
			"战争片":"16"
			"惊悚片":"17"
			"家庭片":"18"
			"古装片":"19"
			"历史片":"20"
			"悬疑片":"21"
			"犯罪片":"22"
			"灾难片":"23"
			"记录片":"24"
			"短片":"25"
			"国产剧":"26"
			"香港剧":"27"
			"韩国剧":"28"
			"欧美剧":"29"
			"台湾剧":"30"
			"日本剧":"31"
			"海外剧":"32"
			"泰国剧":"33"
			"大陆综艺":"34"
			"港台综艺":"35"
			"日韩综艺":"36"
			"欧美综艺":"37"
			"短剧":"38"
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
		print(xmlTxt)
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
		if self.ifSkip(classText=type_name)==True:
			result={'list':[]}
		return result

	def searchContent(self,key,quick):
		Url='{2}?ac=list&wd={0}&pg={1}'.format(urllib.parse.quote(key),'1',self.hostUrl)
		xmlTxt=self.custom_webReadFile(urlStr=Url)
		jo = json.loads(xmlTxt)
		listXml=jo['list']
		videos = self.custom_list(html=listXml)
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
				'User-Agent':'User-Agent: Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 UBrowser/5.6.12150.8 Safari/537.36',
				"Host":self.custom_RegexGetText(Text=urlStr,RegexText='https*://(.*?)(/|$)',Index=1)
			}
		# ssl._create_default_https_context = ssl._create_unverified_context#全局取消证书验证
		req=urllib.request.Request(url=urlStr)#,headers=header
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
		jo = json.loads(xmlTxt)
		classJson=jo['class']
		temporaryClass={}
		for vod in classJson:
			# print(vod['type_name'])
			if self.ifSkip(vod['type_name'])==True:
				continue
			temporaryClass[vod['type_name']]=vod['type_id']
		return temporaryClass
	FilterWords=urllib.parse.unquote('%28%E4%BC%A6%E7%90%86%7C%E5%80%AB%E7%90%86%7C%E7%A6%8F%E5%88%A9%7C%E5%BC%BA%E5%A5%B8%7C%E9%87%8C%E7%95%AA%29')
	def ifSkip(self,classText):
		b=True if self.custom_RegexGetText(Text=classText,RegexText=self.FilterWords,Index=1)!='' else False
		return b

# T=Spider()
# T.init(extend="https://www.mdzyapi.com/api.php/provide/vod")
# print(T.custom_classification())
# l=T.searchContent(key='柯南',quick='')
# l=T.homeVideoContent()
# # # extend={'types':'netflix',"area":"韩国","year":"2023","lang":"韩语","sort":"score"}
# l=T.categoryContent(tid='1',pg='1',filter=False,extend={})
# for x in l['list']:
# 	print(x['vod_id'])
# mubiao=l['list'][0]['vod_id']
# playTabulation=T.detailContent(array=[mubiao,])
# vod_play_from=playTabulation['list'][0]['vod_play_from']
# vod_play_url=playTabulation['list'][0]['vod_play_url']
# url=vod_play_url.split('$$$')
# vod_play_from=vod_play_from.split('$$$')[0]
# url=url[0].split('$')
# url=url[1].split('#')[0]
# # print(vod_play_from+'='+url)
# m3u8=T.playerContent(flag=vod_play_from,id=url,vipFlags=True)
# print(m3u8)