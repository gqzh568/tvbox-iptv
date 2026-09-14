#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import re
from urllib import request, parse
import urllib
import urllib.request
from xml.etree.ElementTree import fromstring, ElementTree as et
import ssl
ssl._create_default_https_context = ssl._create_unverified_context#全局取消证书验证
class Spider(Spider):  # 元类 默认的元类 type
	hostUrl='http://cj.ffzyapi.com/api.php/provide/vod/at/xml/'
	def getName():
		return "非凡资源"#除去少儿不宜的内容
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
			'欧美剧': '16', 
			'记录片': '20', 
			'动漫片': '4',
			'短剧': '36',
			'爱情片': '8', 
			'日韩动漫': '30', 
			'海外动漫': '33', 
			'台湾剧': '21', 
			'国产动漫': '29', 
			'恐怖片': '10',
			'科幻片': '9', 
			'欧美动漫': '31', 
			'喜剧片': '7', 
			'泰国剧': '24', 
			'剧情片': '11', 
			'香港剧': '14',
			'欧美综艺': '28',
			'海外剧': '23', 
			'韩国剧': '15',
			'日韩综艺': '27',
			'港台动漫': '32', 
			'大陆综艺': '25', 
			'港台综艺': '26',
			'日本剧': '22',
			'国产剧': '13',
			'战争片': '12',
			'动作片': '6'
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
		xmlTxt=self.custom_webReadFile(urlStr=self.hostUrl+'?ac=list&h=24')
		tree = et(fromstring(xmlTxt))
		root = tree.getroot()
		listXml=root.iter('list')
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
		Url=self.hostUrl+'?ac=list&t={0}&pg={1}'.format(tid,pg)
		xmlTxt=self.custom_webReadFile(urlStr=Url)
		tree = et(fromstring(xmlTxt))
		root = tree.getroot()
		listXml=root.iter('list')
		for vod in listXml:
			pagecount=vod.attrib['pagecount']
			limit=vod.attrib['pagesize']
			total=vod.attrib['recordcount']
		
		videos = self.custom_list(html=root.iter('list'))
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
		vod_play_from=['播放线路',]
		vod_year=''
		vod_actor=''
		vod_content=''
		vod_director=''
		type_name=''
		vod_area=''
		vod_lang=''
		vod_play_url=[]
		try:
			url=self.hostUrl+'?ac=detail&ids='+id
			xmlTxt=self.custom_webReadFile(urlStr=url)
			jRoot = et(fromstring(xmlTxt))
			xmlList=jRoot.iter('list')
			for vod in xmlList:
					for x in vod:
						for v in x:
							if v.tag=='actor':
								vod_actor=v.text
							if v.tag=='director':
								vod_director=v.text
							if v.tag=='des':
								vod_content=v.text
							if v.tag=='area':
								vod_area=v.text
							if v.tag=='year':
								vod_year=v.text
							if v.tag=='type':
								type_name=v.text
							if v.tag=='lang':
								vod_lang=v.text
			circuit=self.custom_RegexGetTextLine(xmlTxt,r'<dd flag="\w+?"><\!\[CDATA\[(.+?)\]\]></dd>',1)
			vod_play_from=self.custom_RegexGetTextLine(xmlTxt,r'<dd flag="(\w+?)">',1)
			# print(circuit)
			if len(circuit)<1:
				return  {'list': []}
			for v in circuit:
				vodItems=self.custom_EpisodesList(html=v)
				joinStr = "#".join(vodItems)
				vod_play_url.append(joinStr)
		except :
			pass
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
		if int(pg)=="1":
			self.searchpage=1
		if int(pg)>self.searchpage:
			return {'list':[]}
		Url=self.hostUrl+'?ac=list&wd={0}&pg={1}'.format(urllib.parse.quote(key),pg)
		xmlTxt=self.custom_webReadFile(urlStr=Url)
		tree = et(fromstring(xmlTxt))
		root = tree.getroot()
		listXml=root.iter('list')
		videos = self.custom_list(html=listXml)
		try:
			temporary=self.custom_RegexGetText(xmlTxt,'pagecount="([0-9]+?)"',1)
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
		parse=0
		url=id
		headers=''
		b=False
		if self.custom_RegexGetText(Text=flag,RegexText=r'(http|ffm3u8)',Index=1)=='':
			htmlTxt=self.custom_webReadFile(urlStr=url,header=self.header)
			url=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'var main = "(.+?\.m3u8.*?)";',Index=1)
			if url.find('.m3u8')<1:
				url=id
				parse=1
			else:
				headers={
					"Referer":url,
					'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36',
					"Host":self.custom_RegexGetText(Text=url,RegexText='https*://(.*?)(/|$)',Index=1)
				}
				if url.find('://')<1:
					redirecturl=[self.custom_RegexGetText(Text=id,RegexText='(https*://.*?)(/|$)',Index=1),self.custom_RegexGetText(Text=htmlTxt,RegexText=r'var redirecturl\s*=\s*"(.+?)";',Index=1)]
					if url.find('?sign=')>-1:
						url=self.custom_RegexGetText(Text=url,RegexText='(.*?)\\?sign=',Index=1)
					for v in redirecturl:
						if self.custom_TestWebPage(v+url, header=headers)==200:
							url=v+url
							headers['Host']=self.custom_RegexGetText(Text=url,RegexText='https*://(.*?)(/|$)',Index=1)
							b=True
							break
			if b==False:
				url=id
				parse=1
				headers=''
		else:
			url=id
			parse=0
		result["parse"] = parse#0=直接播放、1=嗅探
		result["playUrl"] =''
		result["url"] = url
		result['jx'] = 0#VIP解析,0=不解析、1=解析
		result["header"] = headers	
		return result


	config = {
		"player": {},
		"filter": {}
		}
	header = {}
	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]
	#-----------------------------------------------自定义函数-----------------------------------------------
	#判断网络地址是否存在
	def custom_TestWebPage(self,urlStr,header):
		html=0
		try:
			req=urllib.request.Request(url=urlStr,method='HEAD')#,method='HEAD'
			with  urllib.request.urlopen(req)  as response:
				html = response.getcode () 
		except :
			html=0
		return html
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
		ListRe=html
		videos = []
		temporary=[]
		for vod in ListRe:
			for value in vod:
				for x in value:

					if x.tag=='name':
						title=x.text
					if x.tag=='id':
						id=x.text
					if x.tag=='type':
						tid=x.text
					if x.tag=='last':
						last=x.text
				temporary.append({
					"name":title,
					"id":id,
					"last":last
					})
		
		if len(temporary)>0:
			idTxt=''
			for vod in temporary:
				idTxt=idTxt+vod['id']+','
			if len(idTxt)>1:
				idTxt=idTxt[0:-1]
				url=self.hostUrl+'?ac=detail&ids='+idTxt
				
				xmlTxt=self.custom_webReadFile(urlStr=url)
				jRoot =  et(fromstring(xmlTxt))
				xmlList=jRoot.iter('list')
				for vod in xmlList:
					for x in vod:
						for v in x:
							if v.tag=='name':
								title=v.text
							if v.tag=='id':
								vod_id=v.text
							if v.tag=='pic':
								img=v.text
							if v.tag=='note':
								remarks=v.text
							if v.tag=='year':
								vod_year=v.text
							if v.tag=='type':
								type_name=v.text
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
				if self.ifSkip(classText=type_name)==True:
					continue
				temporaryClass[value.text]=value.attrib['id']
		return temporaryClass
	FilterWords=urllib.parse.unquote('%28%E4%BC%A6%E7%90%86%7C%E5%80%AB%E7%90%86%7C%E7%A6%8F%E5%88%A9%7C%E5%BC%BA%E5%A5%B8%29')
	def ifSkip(self,classText):
		b=True if self.custom_RegexGetText(Text=classText,RegexText=self.FilterWords,Index=1)!='' else False
		return b
