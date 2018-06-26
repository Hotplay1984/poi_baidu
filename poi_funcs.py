
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

def get_res(url, proxy=False, stream=True, text=True, params=None):
	headers_setting = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'}
	proxy_setting = {
		'http':'http://119.28.222.122:8888',
		'https':'https://119.28.222.122:8888'
	}

	try_counter = 0
	res_text = None
	if res_text is None:
		with requests.Session() as session:
			retries = Retry(total=10,
					backoff_factor=0.1,
					status_forcelist=[403, 404, 500, 502, 503, 504 ])
			session.mount('http://',HTTPAdapter(max_retries=retries))
			if not proxy:
				res = session.get(url, 
					headers = headers_setting,
					timeout = 40, 
					stream=stream)
			else:
				print('Use proxy %s' % proxy_setting['http'])
				res = session.get(url, 
					headers = headers_setting,
					timeout = (40, 40), 
					proxies=self.proxy_setting)
		if text:
			return res.text
		else:
			return res.content 
	return


if __name__ == '__main__':
	url = 'http://www.baidu.com'
	res = get_res(url)
	print(res)
