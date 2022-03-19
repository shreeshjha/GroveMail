#!/usr/bin/env python

import asyncio
import websockets
import threading
from collections import deque
import time

class SocketChannel(threading.Thread):

	async def handler(self, websocket, path):
		with self.lock:
			async for mail in websocket:
				self.producer(mail)

	def __init__(self, port=5005, listen=False):
		self.port = port
		threading.Thread.__init__(self)
		self.lock = threading.Lock()
		self.start()
		self.BUFF_MAX_LEN = 1000
		self.buff = deque(maxlen=self.BUFF_MAX_LEN)

	def run(self):
		with self.lock:
			print("Running on port = " + str(self.port))
			loop = asyncio.new_event_loop()
			self.loop = loop
			asyncio.set_event_loop(loop)

			loop.run_until_complete(websockets.serve(self.handler, 'localhost', self.port))
		loop.run_forever()

	def connect(self, host, port):
		self.otherIP = host
		self.otherport = port
		
	def close(self):
		pass

	def kill(self):
		print(str(self.port) + " Trying to kill myself")
		while(1):
			if self.lock.locked():
				time.sleep(1)
				print(str(self.port) + " Channel still in use...")
			else:
				with self.lock:
					print("Killing myself")
					self.loop.call_soon_threadsafe(self.loop.stop)
					break
	def send(self, msg):
		asyncio.get_event_loop().run_until_complete(self.ws_send('ws://' + self.otherIP + ':' + str(self.otherport), msg))

	def receive(self):
		msg = self.consumer()
		return msg
		
	async def ws_send(self, uri, msg):
		with self.lock:
			async with websockets.connect(uri) as websocket:
				await websocket.send(msg)

	def producer(self, msg):
		while len(self.buff) >= self.BUFF_MAX_LEN:
			time.sleep(1)
		self.buff.append(msg)

	def consumer(self):
		while len(self.buff) <= 0:
			time.sleep(1)
		msg = self.buff.pop()
		return msg
