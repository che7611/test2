import time
import json
import requests


def get_landing(page=0):

	url='https://landing-sb.prdasbb18a1.com/zh-cn/Service/CentralService?GetData&ts='+str(int(time.time()*1000))

	post_data = {
		'CompetitionID': '-1',
		'IsEventMenu': 'false',
		'IsFirstLoad': 'true',
		'LiveCenterEventId': '0',
		'LiveCenterSportId': '0',
		'SportID': '1',
		'VersionF': '-1',
		'VersionH': '0',
		'VersionL': '-1',
		'VersionS': '-1',
		'VersionT': '-1',
		'VersionU': '0',
		'oIsFirstLoad': 'true',
		'oIsInplayAll': 'false',
		'oOddsType': '0',
		'oPageNo': '%s'%page,
		'oSortBy': '1',
		'reqUrl': '/zh-cn/sports/football/matches-by-date/today/full-time-asian-handicap-and-over-under'
	 }


	d = requests.post(url,data=post_data).text
	d = json.loads(d)


	# 获得分类
	# res = []
	# res_dt = {}

	# for i in d['lpd']['psm']['psmd']:
	# 	name = i['sen']
	# 	yname = i['sn']
	# 	for j in i['puc']:
	# 		t_name = j['cn']
	# 		for v in j['ces']:
	# 			res.append((name,yname,t_name,v['at'],v['eid'],v['en'],v['esd'],v['est'],v['ht']))
	# 			res_dt[v['eid']] = (name,yname,t_name,v['at'],v['eid'],v['en'],v['esd'],v['est'],v['ht'])



	res_pl = []

	for i in d['mod']['d']:
		name = i['n']
		yname = i['en']
		for j in i['c']:
			t_name = j['n']
			for v in j['e']:
				x2st = v['o'].get('1x21st',())
				if x2st:
					x2st = (float(x2st[1]),float(x2st[3]),float(x2st[5]))
				x1x = v['o'].get('1x2',())
				if x1x:
					x1x = (float(x1x[1]),float(x1x[3]),float(x1x[5]))
				res_pl.append((name,yname,t_name,v['k'],v['edt'],v['i'][0],v['i'][1],{'1x21st':x2st,'1x2':x1x}))

	return res_pl


def get_marathonbet():

	url = 'https://www.marathonbet.com/zh/betting/Football/?page=0&pageAction=getPage&_='+str(int(time.time()*1000))
	d = requests.get(url).text
	d = json.loads(d)


if __name__ == '__main__':
	land = get_landing(0)
	print(land)