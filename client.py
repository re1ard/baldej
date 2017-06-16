# -*- coding: utf-8 -*-

#######################################
##contact: https://vk.com/id27919760 ##
## создал этот чат в рамках курсача  ##
## мб кому нить пригодится для своих ##
## поделок, и просто изучения питона ##
#######################################

from socket import socket as S
from threading import Thread as T
from pickle import loads as L
from pickle import dumps as D
from random import randint as I
from time import time as U
from time import sleep as P

import traceback

class Client:
	conn = None
	user_conn = None
	token = None
	time = U()
	username = None
	def __init__(self,server='localhost',port=1488):
		self.conn = S()
		self.conn.connect((server,port))
		self.user_conn = S()
		self.user_conn.connect((server,port))
		self.auth()

	def get_loop(self):
		self.send_data({'method':'messages.send','values':{'text':'%s присоединился к нашкй вечеринке!!!' % self.username},'token':str(self.token)})
		while 1:
			response = self.send_data({'method':'messages.get','token':str(self.token),'values':{'unixtime':self.time}},'user_conn')
			if response['type'] == 'result':
				if len(response['result']) > 0:
					for msg in response['result']:
						print '%s: %s' % (msg['username'],msg['text'])
						if msg['unixtime'] > self.time:
							self.time = msg['unixtime'] + 1
			P(1)

	def auth(self):
		if True:
			self.username = raw_input('Please enter your name: ')
			#q.send(dumps({'method':'auth.user','values':{'username':'coolboy','password':'net'}})+'~~~~~~')
			response = self.send_data({'method':'auth.user','values':{'username':self.username}})
			if response['type'] == 'auth':
				if response['result'] == 'new':
					password = raw_input('Hello %s, you need create password: ' % username)
					#{'method':'auth.user','values':{'username':'coolboy','password':'net'}
					response = self.send_data({'method':'auth.user','values':{'username':self.username,'password':password}})
					if response['type'] == 'token':
						self.token = response['result']
						return self.loop()
					else:
						print 'unknown error %s' % response
						return
				if response['result'] == 'bad':
					password = raw_input('Hello %s, you need enter your password: ' % self.username)
					response = self.send_data({'method':'auth.user','values':{'username':self.username,'password':password}})
					if response['type'] == 'token':
						self.token = response['result']
						return self.loop()
					if response['type'] == 'auth':
						if response['result'] == 'badpass':
							print 'You enter bad password... Restart loging'
							return self.auth()
						if response['type'] == 'token':
							self.token = response['result']
							return self.loop()
						else:
							print 'unknown error: %s' % response
							return
				if response['result'] == 'use':
					print 'You nickname already uses... Restart loging'
					return self.auth()
			else:
				print 'unknown error: %s' % response
				return

	def loop(self):
		new_msg = T(target = self.get_loop, args = [])
		new_msg.daemon = True
		new_msg.start()
		while True:
			try:
				msg = raw_input('>')
			except KeyboardInterrupt:
				self.send_data({'method':'messages.send','values':{'text':'ооо нет!! господа,нас покинул %s' % self.username},'token':str(self.token)})
				self.send_data({'method':'deauth.user','values':{},'token':str(self.token)})
				return
			#{'method':'messages.send','values':{'text':'hello food'},'token':str(w)})+'~~~~~~')
			if len(msg) < 256:
				self.send_data({'method':'messages.send','values':{'text':msg},'token':str(self.token)})
			else:
				print u'so many message len > 255!!!!' 
		

	def send_data(self,data,use_socket = 'conn'):
		if use_socket == 'conn':
			conn = self.conn
		else:
			conn = self.user_conn
		data = D(data).encode('utf8').encode('hex')
		conn.send(data)
		return L(self.recv_data(use_socket))

	def recv_data(self,use_socket = 'conn'):
		if use_socket == 'conn':
			conn = self.conn
		else:
			conn = self.user_conn
		temporary = u''
		accept_data = u''
		BUFF_SIZE = 4096
		while True:
			temporary = conn.recv(BUFF_SIZE)
			accept_data += temporary
			if len(temporary) < BUFF_SIZE:
				return accept_data.decode('hex').decode('utf8')



def main():
	Client()

if __name__ == '__main__':
	main()
