#coding=utf-8
#!/usr/bin/python
import sys
sys.path.append('..')
from base.spider import Spider
import re
from urllib import request, parse
import urllib
import urllib.request
# import ssl
import json
# ssl._create_default_https_context = ssl._create_unverified_context#全局取消证书验证
class Spider(Spider):  # 元类 默认的元类 type
	def getName():
		return "十品影视"
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
			"电影":"1",
			"电视剧":"2",
			"动漫":"4",
			"综艺":"3"
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
		htmlTxt=self.custom_webReadFile(urlStr='https://sgbpmj.com/')
		element =self.html(htmlTxt)
		nodes = element.xpath('//div[@class="stui-vodlist__box"]')
		videos=self.custom_list(aList=nodes)
		result = {
			'list':videos
		}
		return result
	def categoryContent(self,tid,pg,filter,extend):
		result = {}
		videos=[]
		re='//div[@class="stui-vodlist__box"]'
		Url='https://sgbpmj.com/vtype/{0}-{1}.html'.format(tid,pg)
		if tid=="R":
			Url='https://sgbpmj.com/vodsearch/----%E4%BC%A6%E7%90%86%E7%89%87------{0}---.html'.format(pg)
			re='//li[@class="active top-line-dot clearfix"]/div[@class="thumb"]'
		htmlTxt= self.custom_webReadFile(urlStr=Url)
		root=self.html(htmlTxt)
		nodes = root.xpath(re)
		videos = self.custom_list(aList=nodes)
		pagecount=0 if len(videos)<5 else int(pg)+1
		result['list'] = videos
		result['page'] = pg
		result['pagecount'] =pagecount
		result['limit'] = len(videos)
		result['total'] = 999999
		return result
	def detailContent(self,array):
		aid = array[0].split('###')
		idUrl=aid[1]
		title=aid[0]
		pic=aid[2]
		url=idUrl
		playFrom = []
		htmlTxt =  self.custom_webReadFile(urlStr=url)
		root = self.html(htmlTxt)
		nodes = root.xpath('//div[@class="stui-pannel-box"]/div[1]/div[@class="stui-pannel__head bottom-line active clearfix"]/h3[@class="title"]')
		playFrom=[v.xpath('./text()')[0] for v in nodes ]
		if len(playFrom)<1:
			return  {'list': []}
		videoList=[]
		vodItems = []
		circuit=root.xpath('//div[@class="stui-pannel_bd col-pd clearfix"]/ul')
		for v in circuit:
			vodItems=self.custom_EpisodesList(nodes=v)
			joinStr = "#".join(vodItems)
			videoList.append(joinStr)
		vod_play_from='$$$'.join(playFrom)
		vod_play_url = "$$$".join(videoList)
		
		
		typeName=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'类型：(.+?)简介：',Index=1)
		year=''
		area=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'地区：(.+?)类型：',Index=1)
		act=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'主演：(.+?)导演：',Index=1)
		dir=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'导演：(.+?)地区：',Index=1)
		content=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'div class="infor_intro">简介：(.+?)</div>',Index=1)
		# print(self.custom_removeHtml(txt=content))
		vod = {
			"vod_id": array[0],
			"vod_name": title,
			"vod_pic": pic,
			"type_name":self.custom_removeHtml(txt=typeName),
			"vod_year": self.custom_removeHtml(txt=year),
			"vod_area": self.custom_removeHtml(txt=area),
			"vod_remarks": '',
			"vod_actor":  self.custom_removeHtml(txt=act),
			"vod_director": self.custom_removeHtml(txt=dir),
			"vod_content": self.custom_removeHtml(txt=content)
		}
		vod['vod_play_from'] = vod_play_from
		vod['vod_play_url'] = vod_play_url

		result = {
			'list': [
				vod
			]
		}
		return result

	def searchContent(self,key,quick,pg='1'):
		headers = {
			'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
			'Host': 'www.sh5187.com'
		}
		htmlTxt=''
		url="https://sgbpmj.com/vodsearch/----------{1}---.html?wd={0}".format(urllib.parse.quote(key),pg)
		htmlTxt =  self.custom_webReadFile(urlStr=url)
		root = self.html(htmlTxt)
		nodes = root.xpath('//li[@class="active top-line-dot clearfix"]/div[@class="thumb"]')
		videos=self.custom_list(aList=nodes)
		
		result = {
			'list':videos
		}
		return result
	def playerContent(self,flag,id,vipFlags):
		result = {}
		Url=id
		parse=1
		htmlTxt =self.custom_webReadFile(urlStr=Url)#player_aaaa

		temporary=self.custom_RegexGetText(Text=htmlTxt,RegexText=r'var player_aaaa=(.+?)</script>',Index=1)
		if temporary!='':
			jRoot=json.loads(temporary)
			urlTxt=jRoot['url']
			if len(urlTxt)<5:
				Url=id		
			else:	
				parse=0
				Url=urlTxt
				if urlTxt.find('m3u8')<3:
					Url=id
					parse=1
		result["parse"] = parse#0=直接播放、1=嗅探
		result["playUrl"] =''
		result["url"] = Url
		# result['jx'] = jx#VIP解析,0=不解析、1=解析
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
	def custom_list(self,aList):
		videos = []
		head="https://sgbpmj.com"
		for a in aList:
			title=a.xpath('./a/@title')[0]
			img=a.xpath('./a/img/@src')[0]
			url=a.xpath("./a/@href")[0]
			# print(remarks)
			if url.find('://')<1:
				url=head+url
			if img.find('://')<1:
				img=head+img
			vod_id="{0}###{1}###{2}".format(title,url,img)
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
		req=urllib.request.Request(url=urlStr,headers=header)#,headers=header
		with  urllib.request.urlopen(req)  as response:
			html = response.read().decode(codeName)
			cookie=self.custom_RegexGetText(Text=html,RegexText=r'cookie\s*=\s*"(.+?)";',Index=1)
			if cookie=='':
				return html
			header['Cookie']=cookie
			req=urllib.request.Request(url=urlStr,headers=header)
			with  urllib.request.urlopen(req)  as response1:
				html = response1.read().decode(codeName)
		return html
	#取集数
	def custom_EpisodesList(self,nodes):
		videos = []
		head="https://sgbpmj.com"
		ListLi=nodes.xpath('./li/a')
		for vod in ListLi:
			title =vod.xpath("./text()")[0]
			url = vod.xpath("./@href")[0]
			# print(url)
			if len(url) == 0:
				continue
			videos.append(title+"$"+head+url)
		# print('共:'+str(len(videos)))
		return videos
	#删除html标签
	def custom_removeHtml(self,txt):
		soup = re.compile(r'<[^>]+>',re.S)
		txt =soup.sub('', txt)
		return txt.replace("&nbsp;"," ")

	
# 	def html(self,html):
# 		from lxml import etree
# 		root=etree.HTML(html)
# 		return root
# T=Spider()
# # l=T.searchContent(key='柯南',quick='')
# # l=T.homeVideoContent()
# # # # extend={'types':'netflix',"area":"韩国","year":"2023","lang":"韩语","sort":"score"}
# l=T.categoryContent(tid='1',pg='1',filter=False,extend={})
# for x in l['list']:
# 	print(x['vod_id'])
# mubiao=l['list'][1]['vod_id']
# # # # print(mubiao)
# playTabulation=T.detailContent(array=[mubiao,])
# # print(playTabulation)
# vod_play_from=playTabulation['list'][0]['vod_play_from']
# vod_play_url=playTabulation['list'][0]['vod_play_url']
# url=vod_play_url.split('$$$')
# vod_play_from=vod_play_from.split('$$$')[0]
# url=url[0].split('$')
# url=url[1].split('#')[0]
# print(url)
# m3u8=T.playerContent(flag=vod_play_from,id=url,vipFlags=True)
# print(m3u8)