import pandas as pd
import json
import datetime as dt
import numpy as np
from bs4 import BeautifulSoup
import traceback
import os
import time
from poi_funcs import *


def get_city_top(city_en):
	bs4 = get_soup(city_en)
	raw_a_list = []
	for box in bs4.findAll('div', {'class':'isortBox'}):
		raw_a_list += box.findAll('a')
	values = []
	for a in raw_a_list:
		if 'http://poi.mapbar.com/' + city_en + '/' in a['href']:
			values.append([a.text, a['href']])
	df = pd.DataFrame(values, columns=['topic', 'url'])
	df.to_excel('/data/%s_top.xlsx' % city_en)
	return df


def get_entity_url(url):
	print(url)
	bs4 = BeautifulSoup(get_res(url), 'lxml')
	values = []
	all_a = bs4.find('div', {'class':'sortC'})
	if not all_a:
		print('error url: %s' % url)
		time.sleep(30)
		return None
	for a in all_a.findAll('a'):
		values.append([a.text, a['href']])
	df = pd.DataFrame(values, columns=['entity', 'url'])
	return df

	
def get_entity_info(entity, url):
	try:
		bs4 = BeautifulSoup(get_res(url), 'lxml')
	except:
		traceback.print_exc()
		return {}
	raw_basic_info = bs4.find('ul', {'class':'POI_ulA'})

	try:
		update_time = replace_text(raw_basic_info.find('li').text.split('：')[-1])
		year = int(update_time.split('年')[0])
		month = int(update_time.split('年')[1].split('月')[0])
		day = int(update_time.split('年')[1].split('月')[1].split('日')[0])
		update_time = dt.date(year, month, day).strftime('%Y-%m-%d')

	except:
		update_time = None
	try:
		address_items = raw_basic_info.find('li').find_next_sibling()
		address = [a.text for a in address_items.findAll('a')] +\
				[replace_text(address_items.text).split('：')[-1]]
	except:
		address = []

	try:
		raw_tel = raw_basic_info.find('li', {'class':'telCls'}).text.replace('\t', 
				'').replace('\r', '').split('\n')
		tel = [x for x in raw_tel if len(x) > 0][1]
		if tel == '我来添加':
			tel = None
	except:
		tel = None
	try:
		raw_traffics = bs4.find('div', {'class':'POI_Map'}).findAll('p')[:2]
		stations = replace_text(raw_traffics[0].text).split('、')
		lines = replace_text(raw_traffics[1].text).split('、')

		stations[-1] = stations[-1].replace('。', '')
		lines[-1] = lines[-1].replace('。', '')

		if stations[-1][-1] == '等':
			stations[-1] = stations[-1][:-1]
		if lines[-1][-1] == '等':
			lines[-1] = lines[-1][:-1]
	except:
		stations, lines = [], []

	keys = ['entity', 'update_time', 'address', 'tel', 'bus_stations', 'bus_lines']
	values = [entity, update_time, address, tel, stations, lines]
	return {k: v for k, v in zip(keys, values)}


def get_topic_dict(city_en):
	path = os.getcwd() + '/data/' + city_en + '/top_level/'
	df_top = get_city_top(city_en)
	topics, urls = df_top['topic'].tolist(), df_top['url'].tolist()
	topic_dict = {replace_text(topic):get_entity_url(url)
				 for topic, url in zip(topics, urls)}
	for topic, df_topic in topic_dict.items():
		try:
			df_topic.to_excel('%stopic_%s.xlsx' % (path, topic))
		except:
			traceback.print_exc()
	return topic_dict


def get_city_info(topic_dict):
	topics = list(topic_dict.keys())
	columns = ['entity', 'update_time', 'address', 
			   'tel', 'bus_stations', 'bus_lines']

	path = os.getcwd() + '/data/' + city_en 
	if not os.path.exists(path):
		os.makedirs(path)

	for topic in topics:
		file_name = '%s/%s.xlsx' % (path, topic)
		if os.path.exists(file_name):
			continue
		df = topic_dict[topic]
		if len(df) == 0:
			continue
		values = []
		for ix in df.index:
			entity = df.at[ix, 'entity']
			url = df.at[ix, 'url']
			entity_info = get_entity_info(entity, url)
			if len(entity_info) == 0:
				continue
			values.append([entity_info[col] for col in columns])
			if ix % 100 == 0:
				progress = '{:.2%}'.format(ix / len(df))
				print('%s:%s' %(topic, progress))
		df_entity = pd.DataFrame(values, columns=columns)
		df_entity.to_excel(file_name)