# -*- coding: utf-8 -*-

#######################################
##contact: https://vk.com/id27919760 ##
## создал этот чат в рамках курсача  ##
## мб кому нить пригодится для своих ##
## поделок, и просто изучения питона ##
#######################################


from socket import socket as S
from threading import Thread as T
from pymongo import MongoClient as M
from pickle import loads as L
from pickle import dumps as D
from random import randint as I
from time import time as U

import traceback

def gen_token(username):
	token = '%s' % I(10000000,99999999)
	token = token.encode('hex')
	active_tokens.update({token:username})
	return token

active_tokens = {}

actual_methods = ['auth.user','messages.get','messages.send','deauth.user']

db = M().inst_project

class Client:
	conn = None
	def __init__(self,connect):
		self.conn = connect
		while True:
			data = self.recv_data()
			if not data:
				print 'user drop connection'
				self.conn.close()
				break
			try:
				datariki = L(data)
				print 'incoming: %s' % datariki
				self.process(datariki)
			except:
				traceback.print_exc()
				pass

	def process(self,data):
		if True:
			if not 'method' in data:
				return self.send_error('not found method params')
			else:
				if not data['method'] in actual_methods:
					return self.send_error('not actual method')

			if not 'values' in data:
				return self.send_error('not found values params')

			method_header = data['method'].split('.')
			if method_header[0] == 'auth':
				if method_header[1] == 'user':
					if not 'username' in data['values']:
						return self.send_error('not found username value in auth method')
					else:
						if data['values']['username'] in active_tokens.values():
							return self.send({'type':'auth','result':'use'})
						if not 'password' in data['values']:
							response = db.users.find({'username':data['values']['username']})
							if response.count() == 0:
								return self.send({'type':'auth','result':'new'})
							else:
								return self.send({'type':'auth','result':'bad'})
						else:
							if db.users.find({'username':data['values']['username']}).count() == 0:
								db.users.save({'username':data['values']['username'],'password':data['values']['password']})
								return self.send({'type':'token','result':gen_token(data['values']['username'])})
							else:
								response = db.users.find({'username':data['values']['username'],'password':data['values']['password']})
								if response.count() == 0:
									return self.send({'type':'auth','result':'badpass'})
								else:
									return self.send({'type':'token','result':gen_token(data['values']['username'])})
			else:
				if not 'token' in data:
					return self.send_error('need token,use auth.user method to get token')
				else:
					if not data['token'] in active_tokens:
						return self.send_error('invalid token')
				if method_header[0] == 'messages':
					if method_header[1] == 'send':
						if not 'text' in data['values']:
							return self.send_error('not found text value in messages method')
						else:
							db.messages.save({'unixtime':U(),'text':data['values']['text'],'username':active_tokens[data['token']],'id':db.messages.count()})
							return self.send({'type':'result','result':'ok'})
					if method_header[1] == 'get':
						if not 'unixtime' in data['values']:
							return self.send_error('not unixtime text value in messages method')
						if not 'out' in data['values']:
							out = False
						else:
							out = bool(data['values']['out'])
						if out:
							response = list(db.messages.find().where('this.unixtime > %s && this.username == "%s"' % (data['values']['unixtime'],active_tokens[data['token']])))
							for resp in range(0,len(response)):
								del response[resp]['_id']
							return self.send({'type':'result','result':response})
						else:
							response = list(db.messages.find().where('this.unixtime > %s && !(this.username == "%s")' % (data['values']['unixtime'],active_tokens[data['token']])))
							for resp in range(0,len(response)):
								del response[resp]['_id']
							return self.send({'type':'result','result':response})
				if method_header[0] == 'deauth':
					if method_header[1] == 'user':
						del active_tokens[data['token']]
						return self.send({'type':'result','result':'ok'})
				
			
	def send_error(self,msg):
		return self.send({'type':'error','result':msg})
		
	#def send_message(self,msg):
	#

	def send(self,data):
		try:
			datatariki = D(data)
			self.conn.send(datatariki.encode('utf8').encode('hex'))
			print 'outcoming: %s' % data
			return True	
		except:
			self.conn.close()
			print 'client its DOWN, close connection'
			return False		
				

	def recv_data(self):
		temporary = u''
		accept_data = u''
		BUFF_SIZE = 4096
		while True:
			temporary = self.conn.recv(BUFF_SIZE)
			accept_data += temporary
			if len(temporary) < BUFF_SIZE:
				return accept_data.decode('hex').decode('utf8')

class Server:
	def __init__(self,port = 1488,users = 128):
		self.socket = S()
		self.socket.bind(('',port))
		self.socket.listen(users)
		self.loop()

	def loop(self):
		while True:
			try:
				connection, address = self.socket.accept()
			except KeyboardInterrupt:
				self.socket.close()
				print 'abort server'
				return

			print 'new connection from: %s:%s' % address
			thread = T(target = Client, args = [connection])
			thread.daemon = True
			thread.start()
