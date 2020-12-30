#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding:utf-8
import socket, json
import urllib.request
import sys, os, time, threading
from Logger import *
from UE4Ctrl import *
from Util import *

log = getLogger()

HTTP_PORT = 9000
MAX_PACKET_SIZE = 16 * 1024
SER_TAG_HTTP    = "HTTP"
SER_TAG_POST    = "POST"
SER_TAG_GET     = "GET"
SER_TAG_OPTIONS = "OPTIONS"
SER_TAG_UPLOAD  = "/upload"
SER_DIR_DATA    = "data"
SER_DIR_WEB     = "web"

SER_CONTYPE_CSS  = "text/css"
SER_CONTYPE_GIF  = "image/gif"
SER_CONTYPE_HTML = "text/html"
SER_CONTYPE_ICO  = "image/x-icon"
SER_CONTYPE_JPG  = "image/jpeg"
SER_CONTYPE_JPEG = "image/jpeg"
SER_CONTYPE_JS   = "text/javascript"
SER_CONTYPE_JSON = "application/json"
SER_CONTYPE_PDF  = "application/pdf"
SER_CONTYPE_PNG  = "image/png"
SER_CONTYPE_SVG  = "image/svg+xml"
SER_CONTYPE_SWF  = "application/x-shockwave-flash"
SER_CONTYPE_TIFF = "image/tiff"
SER_CONTYPE_TXT  = "text/plain"
SER_CONTYPE_WAV  = "audio/x-wav"
SER_CONTYPE_WMA  = "audio/x-ms-wma"
SER_CONTYPE_WMV  = "audio/x-ms-wmv"
SER_CONTYPE_XML  = "text/xml"
SER_CONTYPE_DOC  = "application/msword"
SER_CONTYPE_MP4  = "video/mpeg4"
SER_CONTYPE_MP3  = "audio/mp3"
SER_CONTYPE_PPS  = "application/vnd.ms-powerpoint"
SER_CONTYPE_PPT  = "application/vnd.ms-powerpoint"
SER_CONTYPE_XLS  = "application/x-xls"
SER_CONTYPE_APK  = "application/vnd.android.package-archive"
SER_CONTYPE_IPA  = "application/vnd.iphone"
SER_CONTYPE_DEFAULT = "application/octet-stream"

SER_TYPE_CSS  = ".css"
SER_TYPE_GIF  = ".gif"
SER_TYPE_HTML = ".html"
SER_TYPE_ICO  = ".ico"
SER_TYPE_JPG  = ".jpg"
SER_TYPE_JPEG = ".jpeg"
SER_TYPE_JS   = ".js"
SER_TYPE_JSON = ".json"
SER_TYPE_PDF  = ".pdf"
SER_TYPE_PNG  = ".png"
SER_TYPE_SVG  = ".svg"
SER_TYPE_SWF  = ".swf"
SER_TYPE_TIFF = ".tiff"
SER_TYPE_TXT  = ".txt"
SER_TYPE_WAV  = ".wav"
SER_TYPE_WMA  = ".wma"
SER_TYPE_WMV  = ".wmv"
SER_TYPE_XML  = ".xml"
SER_TYPE_DOC  = ".doc"
SER_TYPE_MP4  = ".mp4"
SER_TYPE_MP3  = ".mp3"
SER_TYPE_PPS  = ".pps"
SER_TYPE_PPT  = ".ppt"
SER_TYPE_XLS  = ".xls"
SER_TYPE_APK  = ".apk"
SER_TYPE_IPA  = ".ipa"

class GuardHttpServer:

	ue4Ctrl = UE4Ctrl()

	gRootPath = os.path.abspath(os.path.join(sys.argv[0], ".."))

	def decodepath(self, path):
		path = path.replace("%20", " ")
		path = path.replace("%2F", "/")
		return path

	def http_get_file_size(self, path):
		fileSize = -1
		fileSize = os.path.getsize(path)
		return fileSize

	def getline(self, sock, timeout=1, overtime=1):
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
				if e_time - s_time >= 1:
					ret = -1
					log.info("sock:" + str(sock.fileno()) + " getline overtime!!!")
					break
			except socket.timeout:
				ret = -1
				log.info("sock:" + str(sock.fileno()) + " getline time out exception!!!")
				break
			except:
				ret = -1
				log.info("sock:" + str(sock.fileno()) + " getline other exception!!!")
				break
		return ret, rtnStr.decode('utf-8')

	def clear_sock(self, sock):
		result = ""
		sock.settimeout(0.5)
		try:
			result = sock.recv(MAX_PACKET_SIZE)
			log.info("sock:" + str(sock.fileno()) + " clearbuf:" + str(result))
		except:
			#log.info("sock:" + str(sock.fileno()) + " clear sock error!!!")
			pass
		return result

	def echo_200(self, sock, contentType):
		respStr  = "HTTP/1.1 200 OK\r\n"
		respStr += "Content-Type: " + str(contentType) + "\r\n"
		respStr += "Access-Control-Allow-Origin: *\r\n"
		respStr += "\r\n"
		sock.send(respStr.encode('utf-8'))

	def echo_download_206(self, sock, fileSize, start, to, sendLen):
		respStr  = "HTTP/1.1 206 Partial Content\r\n"
		respStr += "Content-Length: " + str(sendLen) + "\r\n"
		respStr += "Content-Range: bytes " + str(start) + "-" + str(to) + "/" + str(fileSize) + "\r\n"
		respStr += "Content-Type:application/octet-stream\r\n"
		respStr += "Accept-Ranges: bytes\r\n"
		respStr += "Access-Control-Allow-Origin: *\r\n"
		respStr += "\r\n"
		sock.send(respStr.encode('utf-8'))

	def echo_download_200(self, sock, fileSize):
		respStr  = "HTTP/1.1 200 OK\r\n"
		respStr += "Content-Length: " + str(fileSize) + "\r\n"
		respStr += "Content-Type:application/octet-stream\r\n"
		respStr += "Accept-Ranges: bytes\r\n"
		respStr += "Access-Control-Allow-Origin: *\r\n"
		respStr += "\r\n"
		sock.send(respStr.encode('utf-8'))

	def echo_msg(self, sock, msg):
		self.clear_sock(sock)
		self.echo_200(sock, SER_CONTYPE_JSON)
		sock.send(msg.encode('utf-8'))

	def getHttpRtnStatusCode(self, errCode):
		#待实现
		return 400

	def getContentType(self, name):
		contentType = SER_CONTYPE_DEFAULT
		if SER_TYPE_CSS in name:
			contentType = SER_CONTYPE_CSS
		elif SER_TYPE_IPA in name:
			contentType = SER_CONTYPE_IPA
		elif SER_TYPE_APK in name:
			contentType = SER_CONTYPE_APK
		elif SER_TYPE_XLS in name:
			contentType = SER_CONTYPE_XLS
		elif SER_TYPE_PPT in name:
			contentType = SER_CONTYPE_PPT
		elif SER_TYPE_PPS in name:
			contentType = SER_CONTYPE_PPS
		elif SER_TYPE_MP3 in name:
			contentType = SER_CONTYPE_MP3
		elif SER_TYPE_MP4 in name:
			contentType = SER_CONTYPE_MP4
		elif SER_TYPE_DOC in name:
			contentType = SER_CONTYPE_DOC
		elif SER_TYPE_XML in name:
			contentType = SER_CONTYPE_XML
		elif SER_TYPE_WMV in name:
			contentType = SER_CONTYPE_WMV
		elif SER_TYPE_WMA in name:
			contentType = SER_CONTYPE_WMA
		elif SER_TYPE_WAV in name:
			contentType = SER_CONTYPE_WAV
		elif SER_TYPE_TXT in name:
			contentType = SER_CONTYPE_TXT
		elif SER_TYPE_TIFF in name:
			contentType = SER_CONTYPE_TIFF
		elif SER_TYPE_SWF in name:
			contentType = SER_CONTYPE_SWF
		elif SER_TYPE_SVG in name:
			contentType = SER_CONTYPE_SVG
		elif SER_TYPE_PNG in name:
			contentType = SER_CONTYPE_PNG
		elif SER_TYPE_PDF in name:
			contentType = SER_CONTYPE_PDF
		elif SER_TYPE_JSON in name:
			contentType = SER_CONTYPE_JSON
		elif SER_TYPE_JS in name:
			contentType = SER_CONTYPE_JS
		elif SER_TYPE_JPEG in name:
			contentType = SER_CONTYPE_JPEG
		elif SER_TYPE_JPG in name:
			contentType = SER_CONTYPE_JPG
		elif SER_TYPE_GIF in name:
			contentType = SER_CONTYPE_GIF
		elif SER_TYPE_HTML in name:
			contentType = SER_CONTYPE_HTML
		elif SER_TYPE_ICO in name:
			contentType = SER_CONTYPE_ICO
		return contentType 

	def echo_err(self, sock, status, code, msg):
		self.clear_sock(sock)
		respErrStr = "HTTP/1.1 " + str(status) + " " + str(code) + "\r\n"
		respErrStr += "Content-Type: text/html\r\n"
		respErrStr += "Access-Control-Allow-Origin: *\r\n"
		respErrStr += "\r\n"
		respErrStr += str(msg) + "\r\n"
		sock.send(respErrStr.encode('utf-8'))

	def echo_err_jsonmsg(self, sock, code, jsonMsg):
		self.clear_sock(sock)
		respErrStr = "HTTP/1.1 " + str(self.getHttpRtnStatusCode(code)) + " " + str(code) + "\r\n"
		respErrStr += "Content-Type: text/html\r\n"
		respErrStr += "Access-Control-Allow-Origin: *\r\n"
		respErrStr += "\r\n"
		respErrStr += str(jsonMsg) + "\r\n"
		sock.send(respErrStr.encode('utf-8'))

	def echo_err_code(self, sock, code):
		self.echo_err(sock, self.getHttpRtnStatusCode(code), code, code)

	def echo_htmlfile(self, filepath, sock):
		self.clear_sock(sock)
		try:
			# file = open(filename, "r")
			file = open(filename, "r")
			contentType = self.getContentType(path)
			self.echo_200(sock, contentType)
			while True:
				ret = file.read(1024)
				if len(ret) <= 0:
					file.close()
					break
				else:
					# sock.send(ret.encode('utf-8'))
					sock.send(ret)
					log.info("sock:" + str(sock.fileno()) + " echo_htmlfile() - write len:" + str(len(ret)))
		except FileNotFoundError:
			log.info("sock:" + str(sock.fileno()) + "file not found!!!")
		except IsADirectoryError:
			log.info("sock:" + str(sock.fileno()) + " is dir error!!!")
		except:
			log.info("sock:" + str(sock.fileno()) + "other exception!!!")
		finally:
			try:
				log.info("sock:" + str(sock.fileno()) + " echo_htmlfile() finally close file~~~~")
				file.close()
			except:
				log.info("sock:" + str(sock.fileno()) + " echo_htmlfile() finally close file error!!!")

	# ?path=/mnt/DCIM/xxxx&name=xxxx&filesize=xxxx
	def uploadOpt(self, sock, upload_content):
		log.info("enter sock:" + str(sock.fileno()) + " upload_content:" + upload_content)
		upload_content = upload_content.replace(SER_TAG_UPLOAD, "")
		upload_content = upload_content.replace("?", "")
		contentAry = upload_content.split("&")
		log.info("sock:" + str(sock.fileno()) + " uploadOpt() replace upload content:" + str(contentAry))
		path = ""
		name = ""
		fileSize = -1
		for tmp in contentAry:
			tmpAry = tmp.split("=")
			if len(tmpAry) < 2:
				continue
			else:
				if tmpAry[0] == "path":
					path = tmpAry[1]
				elif tmpAry[0] == "name":
					name = tmpAry[1]
				elif tmpAry[0] == "filesize":
					fileSize = int(tmpAry[1])
		log.info("sock:" + str(sock.fileno()) + " path:" + str(path) + " name:" + str(name) + " fileSize:" + str(fileSize))
		if path == "" or name == "" or fileSize < -1:
			self.echo_err_code(sock, "params error!")
			return
		if not self.isSerPermitPath(path[1:]):
			self.echo_err_code(sock, "not permit path")
			return
		dirPath = self.gRootPath + path
		if os.path.isdir(dirPath):
			log.info("sock:" + str(sock.fileno()) + " uploadOpt() isDir")
		else:
			log.info("sock:" + str(sock.fileno()) + " uploadOpt() is not Dir!!!!")
			self.echo_err_code(sock, "path not found")
			return
		
		retGetLine = 0
		#search boundary
		boundary = ""
		#some browser, useragent is ahead of  boundary
		#so, while seeking for boundary, maybe we'll find user-agent, then set isMozille and isFoundUserAgent value.
		isFoundUserAgent = 0
		isMozilla = 0
		while retGetLine >= 0:
			retGetLine, tmpRecv = self.getline(sock)
			log.info("sock:" + str(sock.fileno()) + " test get line in finding boundary retGetLine:" + str(retGetLine) + " \n" + tmpRecv)
			if retGetLine >= 0:
				if isFoundUserAgent == 0:
					if "User-Agent:" in tmpRecv:
						log.info("sock:" + str(sock.fileno()) + " finding boundary we find useragent:" + " \n" + tmpRecv)
						isFoundUserAgent = 1
						if "Mozilla" in tmpRecv:
							log.info("sock:" + str(sock.fileno()) + " finding boundary we find useragent mozilla:" + " \n" + tmpRecv)
							isMozilla = 1
				if "boundary=" in tmpRecv:
					log.info("sock:" + str(sock.fileno()) + " finding boundary line:" + " \n" + tmpRecv)
					aryStr = tmpRecv.split("boundary=")
					boundary = aryStr[1]
					log.info("sock:" + str(sock.fileno()) + " find boundary :" + " \n" + boundary)
					break
		if len(boundary) <= 0:
			self.echo_err_code(sock, "error request")
			return
		
		boundaryMid = "--" + boundary + "\n"
		boundaryEnd = "\r\n--" + boundary + "--\r\n"
		log.info("sock:" + str(sock.fileno()) + " boundaryMid:" + boundaryMid)
		log.info("sock:" + str(sock.fileno()) + " boundaryEnd:" + boundaryEnd)

		#if we did not find useragent in finding boundary, then enter here.
		retGetLine = 0
		if isFoundUserAgent == 0:
			while retGetLine >= 0:
				retGetLine, tmpRecv = self.getline(sock)
				log.info("sock:" + str(sock.fileno()) + " test get line in finding isFoundUserAgent retGetLine:" + str(retGetLine) + " \n" + tmpRecv)
				if retGetLine >= 0:
					if "User-Agent:" in tmpRecv:
						log.info("sock:" + str(sock.fileno()) + " finding boundary we find useragent:" + " \n" + tmpRecv)
						isFoundUserAgent = 1
						if "Mozilla" in tmpRecv:
							log.info("sock:" + str(sock.fileno()) + " finding boundary we find useragent mozilla:" + " \n" + tmpRecv)
							isMozilla = 1
						break
		
		#seek to the end of upload head(before file content)
		if isMozilla == 1:
			#browser, to get end line
			retGetLine = 0
			while retGetLine >= 0:
				retGetLine, tmpRecv = self.getline(sock)
				log.info("sock:" + str(sock.fileno()) + " test get line run over end retGetLine:" + str(retGetLine) + " \n" + tmpRecv)
				if "Content-Type: " in tmpRecv:
					log.info("sock:" + str(sock.fileno()) + " test get line find content-type")
					#ignore \r\n
					retGetLine, tmpRecv = self.getline(sock) 
					break
		else:
			#cellphone to get end lne
			isFoundMidBoundary = 0
			retGetLine = 0
			while retGetLine >= 0:
				retGetLine, tmpRecv = self.getline(sock)
				log.info("sock:" + str(sock.fileno()) + " test get line in finding midboundary retGetLine:" + str(retGetLine) + " \n" + tmpRecv)
				if retGetLine >= 0 and isFoundMidBoundary == 0 and boundaryMid in tmpRecv:
					isFoundMidBoundary = 1
					continue
				if isFoundMidBoundary == 1:
					log.info("sock:" + str(sock.fileno()) + " upload after get boundaryMid - found end line!")
					break
		filePath = dirPath + "/" + name
		try:
			file = open(filePath, "wb")
		except:
			log.info("sock:" + str(sock.fileno()) + " open file error!!!")
			self.echo_err_code(sock, "request not permit")
			return

		writeRetTotal = 0
		cntOverTime = 0
		while True:
			lenRecv = -1
			try:
				recvRet = sock.recv(MAX_PACKET_SIZE)
				lenRecv = len(recvRet)
			except:
				pass
			log.info("sock:" + str(sock.fileno()) + " read upload recvLen:" + str(lenRecv))
			#log.info("sock:" + str(sock.fileno()) + " read upload recvData:" + str(recvRet))
			if lenRecv <= 0:
				if writeRetTotal >= fileSize:
					log.info("sock:" + str(sock.fileno()) + " recv recvRet<=0 cause writeRetTotal >= fileSize")
					break
				log.info("sock:" + str(sock.fileno()) + " recv overtimecnt:" + str(cntOverTime) + " start")
				time.sleep(0.1)
				log.info("sock:" + str(sock.fileno()) + " recv overtimecnt:" + str(cntOverTime) + " end")
				cntOverTime += 1
				if cntOverTime == 5:
					break
			else:
				cntOverTime = 0
				if lenRecv >= len(boundaryEnd):
					log.info("sock:" + str(sock.fileno()) + " enter check boundaryend")
					lenExceptBoundaryEnd = lenRecv - len(boundaryEnd)
					log.info("sock:" + str(sock.fileno()) + " enter check boundaryend lenExceptBoundaryEnd:" + str(lenExceptBoundaryEnd))
					tail = recvRet[lenExceptBoundaryEnd:]
					log.info("sock:" + str(sock.fileno()) + " enter check boundaryend tail:" + str(tail))
					if tail == boundaryEnd.encode("utf-8"):
						log.info("sock:" + str(sock.fileno()) + " enter check boundaryend find boundary end")
						file.write(recvRet[0:lenExceptBoundaryEnd])
						writeRetTotal += (lenRecv - len(boundaryEnd))
						log.info("sock:" + str(sock.fileno()) + " remove boundaryend write")
					else:
						file.write(recvRet)
						writeRetTotal += lenRecv
						log.info("sock:" + str(sock.fileno()) + " write upload total:" + str(writeRetTotal) + " fileSize:" + str(fileSize))
			time.sleep(0.001)

		log.info("sock:" + str(sock.fileno()) + " upload while out fileSize:" + str(fileSize) + " writeRetTotal:" + str(writeRetTotal))
		uploadSucc = 0
		if writeRetTotal >= fileSize:
			uploadSucc = 1
		self.clear_sock(sock)
		if uploadSucc == 0:
			self.echo_err_code(sock, "request time out")
		else:
			#upload success
			if isMozilla == 1:
				#hack IE browser,
				#if echo_200 contenttype=application/json, it'll alert download dialog
				self.echo_200(sock, SER_CONTYPE_HTML)
			else:
				#hack cellphont upload tool
				#if echo_200 contentType= text/html, it'll return error.
				self.echo_200(sock, SER_CONTYPE_JSON)
		respStr = "{\"name\": \"upload\", \"state\": \"done\", \"parameters\": {\"path\": \"" + path + "\", \"name\": \"" + name + "\", \"fileSize\": " + str(fileSize) + "}}"
		sock.send(respStr.encode('utf-8'))
		
		log.info("uploadOpt() --- end!!!")

	def downloadOpt(self, sock, path):
		log.info("downloadOpt sock:" + str(sock.fileno()) + " path:" + path)
		try:
			filePath = self.gRootPath + path
			file = open(filePath, "rb")
			fileSize = self.http_get_file_size(filePath)
			isGetRange = 0
			getLineRet = 0
			fromBytes = -1
			toBytes = -1
			sendLen = -1

			while isGetRange == 0 :
				getLineRet, buf = self.getline(sock)
				log.info("sock:" + str(sock.fileno()) + " getLineRet:" + str(getLineRet) + " buf:" + str(buf))
				if getLineRet < 0:
					log.info("sock:" + str(sock.fileno()) + " downloadopt get_line timeout maybe there was no range")
					break
				if "Range: bytes=" in buf:
					isGetRange = 1
					buf = buf.replace("Range: bytes=", "")
					aryStr = buf.split("-")
					log.info("--------------> aryStr:" + str(aryStr))
					fromBytes = int(aryStr[0])
					strToBytes = aryStr[1]
					if len(strToBytes) >= 1:
						toBytes = int(strToBytes)
					if toBytes == -1:
						toBytes = fileSize
					if fromBytes == -1:
						fromBytes = 0
					sendLen = toBytes - fromBytes + 1
			log.info("sock:" + str(sock.fileno()) + " fromBytes:" + str(fromBytes) + " toBytes:" + str(toBytes) + " sendLen:" + str(sendLen))
			self.clear_sock(sock)
			if isGetRange == 1:
				self.echo_download_206(sock, fileSize, fromBytes, toBytes, sendLen)
			else:
				self.echo_download_200(sock, fileSize)
			self.clear_sock(sock)
			sock.settimeout(60)
			if isGetRange == 1:
				if fromBytes > 0:
					file.seek(fromBytes)
				lenTotal = toBytes - fromBytes + 1
				lenCurrent = 0
				lenPackage = 0
				lenSent = 0 
				
				while True:
					if lenTotal - lenCurrent >= MAX_PACKET_SIZE:
						lenPackage = MAX_PACKET_SIZE
					else:
						lenPackage = lenTotal - lenCurrent
					ret = file.read(lenPackage)
					if len(ret) <= 0:
						log.info("sock:" + str(sock.fileno()) + " downloadOpt() 206 - write end~~~")
						time.sleep(1)
						file.close()
						log.info("sock:" + str(sock.fileno()) + " downloadOpt() 206 - write end~~~ and close socket~~~")
						break
					else:
						sock.send(ret)
						lenCurrent += lenPackage
						log.info("sock:" + str(sock.fileno()) + " downloadOpt() - write len:" + str(len(ret)) + " lenCurrent:" + str(lenCurrent))
						time.sleep(0.01)
			else:
				# name = os.path.basename(path)
				# # contentType = SER_CONTYPE_DEFAULT
				# log.info("path:" + path + " name:" + name + " contentType:" + contentType + " fileSize:" + str(fileSize))
				# # echo_200(sock, contentType)
				cntLen = 0
				while True:
					ret = file.read(MAX_PACKET_SIZE)
					if len(ret) <= 0:
						log.info("sock:" + str(sock.fileno()) + " downloadOpt() - write end~~~")
						mCntTm = 1
						time.sleep(1)
						file.close()
						log.info("sock:" + str(sock.fileno()) + " downloadOpt() - write end~~~ and close socket~~~")
						break
					else:
						sock.send(ret)
						cntLen += len(ret)
						log.info("sock:" + str(sock.fileno()) + " downloadOpt() - write "+ str(cntLen) + "/" + str(fileSize) + "(" + str(float(cntLen/fileSize)) + ")")
						time.sleep(0.01)
		except FileNotFoundError:
			log.info("sock:" + str(sock.fileno()) + " file not found!!!")
			return -1
		except IsADirectoryError:
			log.info("sock:" + str(sock.fileno()) + " is dir error!!!")
		except BrokenPipeError:
			log.info("sock:" + str(sock.fileno()) + " BrokenPipeError!!!")
		except:
			log.info("sock:" + str(sock.fileno()) + " other exception!!!")
		finally:
			try:
				log.info("sock:" + str(sock.fileno()) + " finally close file~~~~")
				file.close()
			except:
				log.info("sock:" + str(sock.fileno()) + " finally close file error!!!")
			return 0

	def echo_showfile(self, path, sock):
		self.clear_sock(sock)
		log.info("sock:" + str(sock.fileno()) + " echo_showfile() path:" + path)
		try:
			path = self.gRootPath + path
			file = open(path, "rb")
			name = os.path.basename(path)
			contentType = self.getContentType(name)
			log.info("path:" + path + " name:" + name + " contentType:" + contentType)
			self.echo_200(sock, contentType)
			cntLen = 0
			while True:
				ret = file.read(MAX_PACKET_SIZE)
				if len(ret) <= 0:
					log.info("sock:" + str(sock.fileno()) + " echo_showfile() - write end~~~")
					file.close()
					break
				else:
					sock.send(ret)
					cntLen += len(ret)
					time.sleep(0.01)
					log.info("sock:" + str(sock.fileno()) + " echo_htmlfile() - write len:" + str(len(ret)) + " cntLen:" + str(cntLen))
		except FileNotFoundError:
			log.info("sock:" + str(sock.fileno()) + " file not found!!!")
			return -1
		except IsADirectoryError:
			log.info("sock:" + str(sock.fileno()) + " is dir error!!!")
		except:
			log.info("sock:" + str(sock.fileno()) + " other exception!!!")
		finally:
			try:
				log.info("sock:" + str(sock.fileno()) + " echo_showfile() finally close file~~~~")
				file.close()
			except:
				log.info("sock:" + str(sock.fileno()) + " echo_showfile() finally close file error!!!")
			return 0

	def getContentData(self, sock):
		contentData = ""
		contentLen = -1
		isFoundContentLen = 0
		while True:
			ret, rtnStr = self.getline(sock)
			log.info("sock:" + str(sock.fileno()) + " test get line:" + str(rtnStr) + " and len:" + str(len(rtnStr)) + " ret:" + str(ret))
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
						log.info("sock:" + str(sock.fileno()) + " contentLen(" + str(strContentLen) + ") to int error!!!")
		if contentLen <= 0:
			log.info("sock:" + str(sock.fileno()) + " contentLen <= 0")
		else:
			sock.settimeout(1)
			try:
				contentData = sock.recv(contentLen)
				contentData = contentData.decode('utf-8')
			except:
				log.info("sock:" + str(sock.fileno()) + " get contentlen contentData error!!!")
			log.info("sock:" + str(sock.fileno()) + " contentLen=" + str(contentLen) + " contentData:" + str(contentData))
		return contentData
	
	def isSerPermitPath(self, path):
		ret = 0
		log.info("test ---- " + path[0:len(SER_DIR_DATA)] + " ---- " + path[0:len(SER_DIR_WEB)])
		if path[0:len(SER_DIR_DATA)] == SER_DIR_DATA or path[0:len(SER_DIR_WEB)] == SER_DIR_WEB:
			ret = 1
		return ret

	def handle_client(self, sock, server_socket):
		log.info("handleclient() enter sock:" + str(sock.fileno()))
		# 获取头
		ret, rtnStr = self.getline(sock)
		if ret < 0:
			log.info("sock:" + str(sock.fileno()) + " get_first_line error!!!")
			sock.close()
			return
		else:
			log.info("sock:" + str(sock.fileno()) + " get_first_line:" + rtnStr)
			# 获取method 和 path
			pathAry = rtnStr.split(" ")
			method = pathAry[0]
			path = pathAry[1]
			path = self.decodepath(path)
			log.info("sock:" + str(sock.fileno()) + " method:" + method + " path:" + path)
			# echo_err(sock, 404, "badbad", "errmessage")
			if rtnStr.find(SER_TAG_HTTP) >= 0:
				#HTTP 协议
				if method == SER_TAG_POST and len(path) > len(SER_TAG_UPLOAD) and (path[0:len(SER_TAG_UPLOAD)] == SER_TAG_UPLOAD):
					self.uploadOpt(sock, path)
				else:
					if self.isSerPermitPath(path[1:]):
						contentType = self.getContentType(path)
						if contentType == SER_CONTYPE_MP4:
							self.downloadOpt(sock, path)
						else:
							#echo对应类型和网页
							self.echo_showfile(path, sock)
					else:
						contentData = self.getContentData(sock)
						rtnStr = self.ue4Ctrl.handleCtrl(path, contentData)
						self.echo_msg(sock, rtnStr)
				sock.close()
			else:
				#其它协议
				log.info("sock:" + str(sock.fileno()) + " not HTTP protocol!!!")
				sock.close()
		
	def handle_serverAccept(self, server_socket):
		while True:
			try:
				client_socket, client_address = server_socket.accept()
				log.info("[%s, %s]connted" % client_address)
				t = threading.Thread(target=self.handle_client, args=(client_socket, server_socket,))
				t.start()
			except OSError:
				log.info('socket alreay closed 88!!!!!!!')
				return

	def handle_serverExit(self, server_socket):
		log.info('ready to close server in one sec~')
		# global gStartSer
		# gStartSer = 0
		time.sleep(0.5)
		server_socket.close()
		log.info('close server end 888~~~!!!!')
		return

	def __init__(self, name=__name__):
		log.info('startServer()')

		webDir = self.gRootPath + getPathSeperater() + SER_DIR_WEB
		checkAndCreateDir(webDir)
		dataDir = self.gRootPath + getPathSeperater() + SER_DIR_DATA
		checkAndCreateDir(dataDir)

		#server
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		#扩大这个5M，可以提速，download 16K  send间隔时间缩短到0.01
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 5 * 1024 * 1024)
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 5 * 1024 * 1024)
		# bufsize = server_socket.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
		# print("------>buf size:" + str(bufsize))
		# bufsize = server_socket.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
		# print("------>buf size:" + str(bufsize))
		server_socket.bind(("", HTTP_PORT))
		server_socket.listen(256)
		t = threading.Thread(target=self.handle_serverAccept, args=(server_socket, ))
		t.start()
		