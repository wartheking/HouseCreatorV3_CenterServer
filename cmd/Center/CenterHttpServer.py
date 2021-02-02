#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding:utf-8
import socket, json
import urllib.request
import sys, os, time, threading, traceback, platform, zipfile
import logging
from CenterCtrl import *

HTTP_PORT = 8100
MAX_PACKET_SIZE = 16 * 1024
SER_TAG_HTTP    = "HTTP"
SER_TAG_POST    = "POST"
SER_TAG_GET     = "GET"

SER_CONTYPE_JSON = "application/json"

URL_PATH_BYE   = "/bye"

class CenterHttpServer:

	gRootPath = os.path.abspath(os.path.join(sys.argv[0], ".."))
	#states array
	#每秒钟check的所有功能机群组的状态 都会按index来存储，存储可以导出jsonobj的字符串
	#这样就不需要CenterStatus.txt_0/1/2... 这些文件了
	ARY_STATUS = []
	STATUS_MAX_LENGTH = 50

	def getline(self, sock, timeout=0.5, overtime=1):
		ret = 0
		rtnStr = b''
		tmpByte = b''
		sock.settimeout(timeout)
		s_time = time.time()
		e_time = s_time
		while True:
			try:
				tmpByte = sock.recv(1)
				#判断是不是 \r\n
				if tmpByte == b'\r':
					nxtByte = sock.recv(1)
					if nxtByte == b'\n':
						break
					else:
						rtnStr += tmpByte
						rtnStr += nxtByte
				else:
					rtnStr += tmpByte
				#检查是不是获取太久了
				e_time = time.time()
				if e_time - s_time >= overtime:
					ret = -1
					self.log.info("sock:" + str(sock.fileno()) + " getline overtime!!!")
					break
			except socket.timeout:
				ret = -1
				# self.log.info("sock:" + str(sock.fileno()) + " getline time out exception!!!")
				break
			except:
				ret = -1
				self.log.info("sock:" + str(sock.fileno()) + " getline other exception!!!")
				break
		return ret, rtnStr.decode('utf-8')

	def clear_sock(self, sock):
		result = ""
		sock.settimeout(0.5)
		try:
			result = sock.recv(MAX_PACKET_SIZE)
			# self.log.info("sock:" + str(sock.fileno()) + " clearbuf:" + str(result))
		except:
			#self.log.info("sock:" + str(sock.fileno()) + " clear sock error!!!")
			pass
		return result

	def echo_200(self, sock, contentType):
		respStr  = "HTTP/1.1 200 OK\r\n"
		respStr += "Content-Type: " + str(contentType) + "\r\n"
		respStr += "Access-Control-Allow-Origin: *\r\n"
		respStr += "\r\n"
		sock.send(respStr.encode('utf-8'))

	def echo_msg(self, sock, msg):
		self.clear_sock(sock)
		self.echo_200(sock, SER_CONTYPE_JSON)
		sock.send(msg.encode('utf-8'))

	def getContentData(self, sock):
		contentData = ""
		contentLen = -1
		isFoundContentLen = 0
		while True:
			ret, rtnStr = self.getline(sock)
			#self.log.info("sock:" + str(sock.fileno()) + " test get line:" + str(rtnStr) + " and len:" + str(len(rtnStr)) + " ret:" + str(ret))
			if ret < 0:
				#滚到最后
				break
			else:
				if isFoundContentLen == 1 and len(rtnStr) == 0:
					break
				if isFoundContentLen == 0 and "Content-Length: " in rtnStr:
					isFoundContentLen = 1
					strContentLen = rtnStr.replace("Content-Length: ", "")
					try:
						contentLen = int(strContentLen)
					except:
						self.log.info("sock:" + str(sock.fileno()) + " contentLen(" + str(strContentLen) + ") to int error!!!")
		if contentLen <= 0:
			# self.log.info("sock:" + str(sock.fileno()) + " contentLen <= 0")
			pass
		else:
			sock.settimeout(1)
			try:
				contentData = sock.recv(contentLen)
				contentData = contentData.decode('utf-8')
			except:
				self.log.info("sock:" + str(sock.fileno()) + " get contentlen contentData error!!!")
			self.log.info("sock:" + str(sock.fileno()) + " contentLen=" + str(contentLen) + " contentData:" + str(contentData))
		return contentData
	
	def handle_client(self, sock, server_socket):
		self.log.info("handleclient() enter sock:" + str(sock.fileno()))
		# 获取头
		ret, rtnStr = self.getline(sock)
		if ret < 0:
			self.log.info("sock:" + str(sock.fileno()) + " get_first_line error!!!")
			sock.close()
			return
		else:
			self.log.info("sock:" + str(sock.fileno()) + " get_first_line:" + rtnStr)
			# 获取method 和 path
			pathAry = rtnStr.split(" ")
			method = pathAry[0]
			path = pathAry[1]
			# path = self.decodepath(path)
			path = urllib.parse.unquote(path)
			self.log.info("sock:" + str(sock.fileno()) + " method:" + method + " path:" + path)
			if rtnStr.find(SER_TAG_HTTP) >= 0:
				contentData = self.getContentData(sock)
				rtnStr = self.ctrl.handleRecv(path, contentData)
				self.echo_msg(sock, rtnStr)
				if path == URL_PATH_BYE:
					if "done" in rtnStr:
						t = threading.Thread(target=self.handle_serverExit, args=(server_socket,))
						t.start()
				sock.close()
			else:
				#其它协议
				self.log.info("sock:" + str(sock.fileno()) + " not HTTP protocol!!!")
				sock.close()
		
	def handle_serverAccept(self, server_socket):
		while True:
			try:
				client_socket, client_address = server_socket.accept()
				self.log.info("[%s, %s]connted" % client_address)
				t = threading.Thread(target=self.handle_client, args=(client_socket, server_socket,))
				t.start()
			except OSError:
				self.log.info('socket alreay closed 88!!!!!!!')
				return

	def handle_serverExit(self, server_socket):
		self.log.info('ready to close server in one sec~')
		time.sleep(0.5)
		server_socket.close()
		self.log.info('close server end 888~~~!!!!')
		return
	
	def __init__(self, log=None):
		self.log = log
		self.log.info('init()')

		self.log.info("remove old server first~~~~222!")
		try:
			url = "http://127.0.0.1:" + str(HTTP_PORT) + "/bye"
			f = urllib.request.urlopen(url)
			self.log.info(f.read().decode('utf-8'))
			f.close()
		except urllib.error.URLError:
			self.log.info("no exist server~~~~!")

		self.ctrl = CenterCtrl(self.log)

		#server
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server_socket.setsockopt(socket.SOL_SOCKET, socket.TCP_NODELAY, 1)
		server_socket.bind(("", HTTP_PORT))
		server_socket.listen(1024)
		#直接主线程来while循环，如果异常了就可以直接跳出来了
		self.handle_serverAccept(server_socket)
		