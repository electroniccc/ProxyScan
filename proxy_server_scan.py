#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import random
import aiohttp
import asyncio

class ProxyServer:
	def __init__(self) -> None:
		self.f = open('proxy_servers.txt', 'a')
	
	def __del__(self):
		self.f.close()

	async def run(self):
		self.proxy_list = await self.get_proxy_list()
		self.proxy_list = list(dict.fromkeys(self.proxy_list))
		print('\a')
		print('\a')
		w = max(5, int(len(self.proxy_list)/20))
		tasks = [self.check_proxy_server(i) for i in range(0, w)]
		await asyncio.gather(*tasks)
		print('\a')

	async def get_proxy_list(self, total=40):
		session = aiohttp.ClientSession()
		proxy_list = []
		for i in range(1, total+1):
			print(f'\rgetting page[{i}/{total}]' + ' ' * 10, end='')
			# https://hidemy.name/cn/proxy-list/?start={(i-1)*64}#list
			# https://www.kuaidaili.com/free/intr/{i}/
			try:
				response = await session.get(
					f'https://www.kuaidaili.com/free/intr/{i}/',
					headers={
						'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36'
					},
					proxy='http://127.0.0.1:10809'
				)
				if response.status == 200:
					data = await response.text()
					proxy_list += re.findall(r'((?:\d{1,3}\.){3}\d+)(?:\D|\n)+(\d{2,5})', data)
				else:
					print('\rget page failed' + ' ' * 10, end='')
			except Exception:
				print('\rget page failed', end='')
			await asyncio.sleep(random.randint(5, 16))
		await session.close()
		return proxy_list

	async def check_proxy_server(self, id=0):
		while self.proxy_list:
			px = self.proxy_list.pop()
			(ip, port) = px
			valid = False
			try:
				async with aiohttp.ClientSession() as cliSession:
					resp = await cliSession.get('http://www.baidu.com', proxy=f'http://{ip}:{port}', timeout=10)
					if resp.status == 200:
						valid = True
						self.f.write(f'{ip}:{port}\n')
					await asyncio.sleep(0.0250)
			except Exception:
				pass
			print(f'\r[{id}] validate:[{ip}:{port}] {valid}, {len(self.proxy_list)} remain' + ' ' * 20, end='')
		
		

def main():
	ps = ProxyServer()
	loop = asyncio.new_event_loop()
	loop.run_until_complete(ps.run())
	loop.run_until_complete(asyncio.sleep(0.250))
	loop.close()

if __name__ == '__main__':
	main()
