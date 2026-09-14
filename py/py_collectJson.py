#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..') 
from base.spider import Spider
import json
import re
from urllib import request, parse
import urllib
from xml.etree.ElementTree import fromstring, ElementTree as et

class Spider(Spider):  # 元类 默认的元类 type
	hostUrl=''
	cateManual={}
	homeVideo=None
	isFilter=True
	typeIndex=0
	def getName():
		return "采集[Json]"#除去少儿不宜的内容
	def init(self,extend=""):
		try:
			jRoot = json.loads(extend)
			if 'hostUrl' in jRoot:
				self.hostUrl=jRoot['hostUrl']
				self.header['Host']=self.custom_RegexGetText(Text=self.hostUrl,RegexText='https*://(.*?)(/|$)',Index=1)
				self.header['Referer']=self.hostUrl
			if 'class' in jRoot:
				temporary=jRoot['class'].split(',')
				for vod in temporary:
					tem=vod.split(':')
					self.cateManual[tem[0]]=tem[1]
			if 'isFilter' in jRoot:
				self.isFilter=False if jRoot['isFilter']==0 else True
			if 'type' in jRoot:
				self.typeIndex=jRoot['type']
		except Exception as e:
			print("{0}".format(e))
	def isVideoFormat(self,url):
		pass
	def manualVideoCheck(self):
		pass
	def homeContent(self,filter):
		result = {}
		if self.cateManual=={}:
			if self.typeIndex==0:
				self.cateManual =self.custom_classification()
			else:
				self.cateManual=self.custom_classification_xml()
		classes = []
		for k in self.cateManual:
			classes.append({
				'type_name':k,
				'type_id':self.cateManual[k]
			})
		self.cateManual={}
		result['class'] = classes
		if(filter):
			result['filters'] = self.config['filter']
		return result

	def homeVideoContent(self):
		if self.homeVideo==None:
			strTxt=self.fetch(self.hostUrl+'?ac=list&h=24',headers=self.header).text		
			if self.typeIndex==0:
				jRoot = json.loads(strTxt)
				listJson=jRoot['list']
				videos = self.custom_list(jsonList=listJson)
			else:
				tree = et(fromstring(strTxt))
				root = tree.getroot()
				temporaryList=root.iter('list')
				videos = self.custom_list_xml(temporaryList)
		else:
			videos=self.homeVideo
			
		result = {
			'list':videos
		}
		return result

	def categoryContent(self,tid,pg,filter,extend):
		result = {}
		videos=[]
		Url=self.hostUrl+'?ac=list&t={0}&pg={1}'.format(tid,pg)
		strTxt=self.fetch(Url,headers=self.header).text
		if self.typeIndex==0:
			jRoot = json.loads(strTxt)
			listJson=jRoot['list']
			pagecount=jRoot['pagecount']
			limit=jRoot['limit']
			total=jRoot['total']
			videos = self.custom_list(jsonList=listJson)
		else:
			tree = et(fromstring(strTxt))
			root = tree.getroot()
			temporaryList=root.iter('list')
			videos = self.custom_list_xml(temporaryList)
			try:
				pagecount=root.find('list').get('pagecount')
				limit=root.find('list').get('pagesize')
				total=root.find('list').get('recordcount')
			except:
				limit=pagecount=total=0
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
		vod_play_from=[]
		type_name=vod_year=vod_area=vod_actor=vod_director=vod_content=vod_remarks=''
		vodItems=[]
		vod_play_url=[]
		try:
			url=self.hostUrl+'?ac=detail&ids='+id#https://1080zyk.com/?m=vod-detail-id-64171.html
			strTxt=self.fetch(url,headers=self.header).text
			if self.typeIndex==0:
				jRoot = json.loads(strTxt)
				if jRoot['code']!=1:
					return result
				jsonList=jRoot['list']
				for vod in jsonList:
					vod_play_url=vod['vod_play_url']
					vod_play_from=vod['vod_play_from']
				vod_year=vod['vod_year']
				vod_actor=vod['vod_actor']
				vod_content=vod['vod_content']
				vod_director=vod['vod_director']				
				type_name=vod['type_name']
				vod_area=vod['vod_area']
			else:
				tree = et(fromstring(strTxt))
				root = tree.getroot()
				temporaryList=root.find('list').find('video')
				playfrom=[]
				for v in temporaryList:
					if v.tag=='dl':
						temporary=v.findall('dd')
						for v1 in temporary:
							playfrom.append(v1.get('flag'))
							vodItems.append(v1.text)
					elif v.tag=='type':
						type_name=v.text
					elif v.tag=='year':
						vod_year=v.text
					elif v.tag=='actor':
						vod_actor=v.text
					elif v.tag=='des':
						vod_content=v.text
					elif v.tag=='director':
						vod_director=v.text
					elif v.tag=='area':
						vod_area=v.text
					elif v.tag=='lang':
						vod_remarks=v.text
				vod_play_from='$$$'.join(playfrom)
				vod_play_url='$$$'.join(vodItems)
		except Exception as e:
			vod_content=e		
		vod = {
			"vod_id":array[0],
			"vod_name":title,
			"vod_pic":logo,
			"type_name":type_name,
			"vod_year":vod_year,
			"vod_area":vod_area,
			"vod_remarks":vod_remarks,
			"vod_actor":vod_actor,
			"vod_director":vod_director,
			"vod_content":vod_content
		}
		vod['vod_play_from'] = vod_play_from
		vod['vod_play_url'] = vod_play_url
		result = {
			'list':[
				vod
			]
		}
		if self.ifSkip(classText=type_name)==True:
			result={'list':[]}
		return result
	searchpage=1
	def searchContent(self,key,quick,pg='1'):
		if int(pg)==1:
			self.searchpage=1
		if int(pg)>self.searchpage:
			return {'list':[]}
		Url=self.hostUrl+'?ac=list&wd={0}&pg={1}'.format(urllib.parse.quote(key),pg)
		strTxt=self.fetch(Url,headers=self.header).text
		if self.typeIndex==0:
			jRoot = json.loads(strTxt)
			listJson=jRoot['list']
			self.searchpage=jRoot['pagecount']
			videos = self.custom_list(listJson)
		else:
			tree = et(fromstring(strTxt))
			root = tree.getroot()
			temporaryList=root.iter('list')
			videos = self.custom_list_xml(temporaryList)
			try:
				self.searchpage=root.find('list').get('pagecount')
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
	header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36'}
	def localProxy(self,param):
		return [200, "video/MP2T", action, ""]
	#-----------------------------------------------自定义函数-----------------------------------------------
	#正则取文本
	def custom_RegexGetText(self,Text,RegexText,Index=0):
		returnTxt=""
		Regex=re.search(RegexText, Text, re.M|re.S)
		if Regex is None:
			returnTxt=""
		else:
			returnTxt=Regex.group(Index)
		return returnTxt	
	#分类取结果
	def custom_list(self,jsonList):
		videos = []
		temporary=[]
		for vod in jsonList:
			title=vod['vod_name']
			id=str(vod['vod_id'])
			tid=vod['type_name']
			last=vod['vod_remarks']
			temporary.append({
				"name":title,
				"id":id,
				"last":last
				})
		if len(temporary)>0:
			idTxt=''
			for vod in temporary:
				idTxt=idTxt+str(vod['id'])+','
			if len(idTxt)>1:
				idTxt=idTxt[0:-1]
				url=self.hostUrl+'?ac=detail&ids='+idTxt
				jsonTxt=self.fetch(url).text
				jRoot = json.loads(jsonTxt)
				if jRoot['code']!=1:
					return videos
				jsonList=jRoot['list']
				for vod in jsonList:
					title=vod['vod_name']
					vod_id=str(vod['vod_id'])
					img=vod['vod_pic']
					type_name=vod['type_name']
					vod_year=str(vod['vod_year'])
					remarks=vod['vod_remark'] if 'vod_remark' in vod else ''
					if self.ifSkip(classText=type_name+title)==True:
						continue
					vod_id='{0}###{1}###{2}'.format(title,vod_id,img)
					videos.append({
						"vod_id":vod_id,
						"vod_name":title,
						"vod_pic":img,
						"vod_year":vod_year,
						"vod_remarks":remarks
					})
		return videos			
	#分类取结果
	def custom_list_xml(self,xmlList):
		videos = []
		temporary=[]
		for vod in xmlList:
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
				idTxt=idTxt+str(vod['id'])+','
			if len(idTxt)>1:
				idTxt=idTxt[0:-1]
				url=self.hostUrl+'?ac=detail&ids='+idTxt
				xmlTxt=self.fetch(url,headers=self.header).text
				tree = et(fromstring(xmlTxt))
				root = tree.getroot()
				temporaryList=root.iter('list')
				for vod in temporaryList:
					for v in vod:
						title=vod_id=type_name=img=vod_year=remarks=''
						for v1 in v:
							if v1.tag=='name':
								title=v1.text
							elif v1.tag=='id':
								vod_id=str(v1.text)
							elif v1.tag=='type':
								type_name=v1.text
							elif v1.tag=='pic':
								img=v1.text
							elif v1.tag=='year':
								vod_year=v1.text
							elif v1.tag=='note':
								remarks=v1.text
						if self.ifSkip(classText=type_name+title)==True:
							continue
						vod_id='{0}###{1}###{2}'.format(title,vod_id,img)
						videos.append({
							"vod_id":vod_id,
							"vod_name":title,
							"vod_pic":img,
							"vod_year":vod_year,
							"vod_remarks":remarks
						})
		return videos			
	#取分类
	def custom_classification(self):
		jsonTxt=self.fetch(self.hostUrl+'?ac=list&h=24',headers=self.header).text
		jRoot = json.loads(jsonTxt)
		listJson=jRoot['list']
		self.homeVideo = self.custom_list(jsonList=listJson)
		classList=jRoot['class']
		temporaryClass={}
		for vod in classList:
			if self.custom_RegexGetText(Text=vod['type_name'],RegexText=self.FilterWords,Index=1)!='' and self.isFilter==True:
				continue
			temporaryClass[vod['type_name']]=str(vod['type_id'])
			# print(f'{vod['type_name']}:{vod['type_id']},')
		return temporaryClass
	#取分类
	def custom_classification_xml(self):
		xmlTxt=self.fetch(self.hostUrl+'?ac=list&h=24',headers=self.header).text
		tree = et(fromstring(xmlTxt))
		root = tree.getroot()
		temporaryList=root.iter('class')
		temporaryClass={}
		for vod in temporaryList:
			for v in vod:
				name=v.text
				id=str(v.get('id'))
				temporaryClass[name]=id
				# print(f'{name}:{id},')
		temporaryList=root.iter('list')
		self.homeVideo = self.custom_list_xml(xmlList=temporaryList)
		return temporaryClass
	FilterWords=urllib.parse.unquote('%28%E4%BC%A6%E7%90%86%7C%E5%80%AB%E7%90%86%7C%E7%A6%8F%E5%88%A9%7C%E5%BC%BA%E5%A5%B8%29')
	def ifSkip(self,classText):
		b=True if self.custom_RegexGetText(Text=classText,RegexText=self.FilterWords,Index=1)!='' and self.isFilter==True else False
		return b
