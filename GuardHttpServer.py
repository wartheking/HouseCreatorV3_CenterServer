#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding:utf-8
import socket, json
import urllib.request
import sys, os, time, threading, traceback, platform, zipfile
from GuardCtrl import *

HTTP_PORT = 9000
MAX_PACKET_SIZE = 16 * 1024
SER_TAG_HTTP    = "HTTP"
SER_TAG_POST    = "POST"
SER_TAG_GET     = "GET"
SER_TAG_OPTIONS = "OPTIONS"
SER_TAG_UPLOAD  = "/upload"
SER_TAG_ZIPFILE = "/zipfiles"
SER_DIR_DATA    = "data"
SER_DIR_WEB     = "web"
SER_DIR_CMD     = "cmd"
SER_DIR_ACCESS  = "access"
SER_DIR_LOGS    = "logs"

SER_RTN_PATH = "path"
SER_RTN_STATE = "state"
SER_RTN_STATE_DONE = "done"
SER_RTN_STATE_ERROR = "error"

SER_RTN_MSG = "msg"
SER_RTN_MSG_PARAMSERR = "params error"
SER_RTN_MSG_NOTPERMIT = "not permit"
SER_RTN_MSG_PATHNOTFOUND = "path not found"
SER_RTN_MSG_FILENOTFOUND = "file not found"
SER_RTN_MSG_REQUESTERR = "request error"
SER_RTN_MSG_TIMEOUT = "time out"
SER_RTN_MSG_DELETEERR = "delete err"
SER_RTN_MSG_UNKNOWN = "unknown"
SER_RTN_DATA = "data"

SER_FILE_PATH  = "path"
SER_FILE_FILES = "files"
SER_FILE_SIZE  = "size"
SER_FILE_NAME  = "name"

SER_ZIP_PATH = "path"
SER_ZIP_FILES = "files"

SER_CONTYPE_CSS  = "text/css"
SER_CONTYPE_GIF  = "image/gif"
SER_CONTYPE_HTML = "text/html"
SER_CONTYPE_LOG  = "text/html"
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
SER_CONTYPE_DEFAULT = "text/plain"

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
SER_TYPE_LOG  = ".log"

class GuardHttpServer:

	gRootPath = os.path.abspath(os.path.join(sys.argv[0], ".."))

	def checkAndCreateDir(self, path):
		isExists = os.path.exists(path)
		if not isExists:
			os.makedirs(path) 
			self.log.info(path + ' 创建成功')
		else:
			self.log.info(path + ' 目录已存在')

	def getPathSeperater(self):
		if platform.platform().find("Windows") >= 0:
			return "\\"
		else:
			return "/"

	def decodepath(self, path):
		path = path.replace("%20", " ")
		path = path.replace("%2F", "/")
		return path

	def http_get_file_size(self, path):
		fileSize = -1
		fileSize = os.path.getsize(path)
		return fileSize

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
		respStr += "Content-Type: " + str(contentType) + ";charset=UTF-8\r\n"
		respStr += "Access-Control-Allow-Origin: *\r\n"
		respStr += "\r\n"
		sock.send(respStr.encode('utf-8'))

	def echo_download_206(self, sock, fileSize, start, to, sendLen):
		respStr  = "HTTP/1.1 206 Partial Content\r\n"
		respStr += "Content-Length: " + str(sendLen) + "\r\n"
		respStr += "Content-Range: bytes " + str(start) + "-" + str(to) + "/" + str(fileSize) + "\r\n"
		respStr += "Content-Type:application/octet-stream;charset=UTF-8\r\n"
		respStr += "Accept-Ranges: bytes\r\n"
		respStr += "Access-Control-Allow-Origin: *\r\n"
		respStr += "\r\n"
		sock.send(respStr.encode('utf-8'))

	def echo_download_200(self, sock, fileSize):
		respStr  = "HTTP/1.1 200 OK\r\n"
		respStr += "Content-Length: " + str(fileSize) + "\r\n"
		respStr += "Content-Type:application/octet-stream;charset=UTF-8\r\n"
		respStr += "Accept-Ranges: bytes\r\n"
		respStr += "Access-Control-Allow-Origin: *\r\n"
		respStr += "\r\n"
		sock.send(respStr.encode('utf-8'))

	def genSimpleRtnMsg(self, path, state, msg, data=""):
		result =  "{"
		result += ("\"" + SER_RTN_PATH  + "\":\"" + str(path) + "\",")
		result += ("\"" + SER_RTN_STATE + "\":\"" + str(state) + "\",")
		result += ("\"" + SER_RTN_MSG   + "\":\"" + str(msg) + "\"")
		if data != "":
			result += ","
			result += ("\"" + SER_RTN_DATA   + "\":" + str(data))
		result += "}"
		return result

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
		elif SER_TYPE_LOG in name:
			contentType = SER_CONTYPE_LOG
		return contentType 

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
					self.log.info("sock:" + str(sock.fileno()) + " echo_htmlfile() - write len:" + str(len(ret)))
		except FileNotFoundError:
			self.log.info("sock:" + str(sock.fileno()) + "file not found!!!")
		except IsADirectoryError:
			self.log.info("sock:" + str(sock.fileno()) + " is dir error!!!")
		except:
			self.log.info("sock:" + str(sock.fileno()) + "other exception!!!")
		finally:
			try:
				self.log.info("sock:" + str(sock.fileno()) + " echo_htmlfile() finally close file~~~~")
				file.close()
			except:
				self.log.info("sock:" + str(sock.fileno()) + " echo_htmlfile() finally close file error!!!")

	# ?path=/mnt/DCIM/xxxx&name=xxxx&filesize=xxxx
	def uploadOpt(self, sock, upload_content):
		self.log.info("enter sock:" + str(sock.fileno()) + " upload_content:" + upload_content)
		upload_content = upload_content.replace(SER_TAG_UPLOAD, "")
		upload_content = upload_content.replace("?", "")
		contentAry = upload_content.split("&")
		self.log.info("sock:" + str(sock.fileno()) + " uploadOpt() replace upload content:" + str(contentAry))
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
		self.log.info("sock:" + str(sock.fileno()) + " path:" + str(path) + " name:" + str(name) + " fileSize:" + str(fileSize))
		if path == "" or name == "" or fileSize < -1:
			self.echo_msg(sock, self.genSimpleRtnMsg(path, SER_RTN_STATE_ERROR, SER_RTN_MSG_PARAMSERR))
			return
		if not self.isSerPermitPath(path[1:]):
			self.echo_msg(sock, self.genSimpleRtnMsg(path, SER_RTN_STATE_ERROR, SER_RTN_MSG_NOTPERMIT))
			return
		dirPath = self.gRootPath + path
		if self.isAccessPath(path):
			dirPath = self.pathRemoveAccess(path)
		if os.path.isdir(dirPath):
			self.log.info("sock:" + str(sock.fileno()) + " uploadOpt() isDir")
		else:
			self.log.info("sock:" + str(sock.fileno()) + " uploadOpt() is not Dir!!!!")
			self.echo_msg(sock, self.genSimpleRtnMsg(path, SER_RTN_STATE_ERROR, SER_RTN_MSG_PATHNOTFOUND))
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
			self.log.info("sock:" + str(sock.fileno()) + " test get line in finding boundary retGetLine:" + str(retGetLine) + " \n" + tmpRecv)
			if retGetLine >= 0:
				if isFoundUserAgent == 0:
					if "User-Agent:" in tmpRecv:
						self.log.info("sock:" + str(sock.fileno()) + " finding boundary we find useragent:" + " \n" + tmpRecv)
						isFoundUserAgent = 1
						if "Mozilla" in tmpRecv:
							self.log.info("sock:" + str(sock.fileno()) + " finding boundary we find useragent mozilla:" + " \n" + tmpRecv)
							isMozilla = 1
				if "boundary=" in tmpRecv:
					self.log.info("sock:" + str(sock.fileno()) + " finding boundary line:" + " \n" + tmpRecv)
					aryStr = tmpRecv.split("boundary=")
					boundary = aryStr[1]
					self.log.info("sock:" + str(sock.fileno()) + " find boundary :" + " \n" + boundary)
					break
		if len(boundary) <= 0:
			self.echo_msg(sock, self.genSimpleRtnMsg(path, SER_RTN_STATE_ERROR, SER_RTN_MSG_REQUESTERR))
			return
		
		boundaryMid = "--" + boundary + "\n"
		boundaryEnd = "\r\n--" + boundary + "--\r\n"
		self.log.info("sock:" + str(sock.fileno()) + " boundaryMid:" + boundaryMid)
		self.log.info("sock:" + str(sock.fileno()) + " boundaryEnd:" + boundaryEnd)

		#if we did not find useragent in finding boundary, then enter here.
		retGetLine = 0
		if isFoundUserAgent == 0:
			while retGetLine >= 0:
				retGetLine, tmpRecv = self.getline(sock)
				self.log.info("sock:" + str(sock.fileno()) + " test get line in finding isFoundUserAgent retGetLine:" + str(retGetLine) + " \n" + tmpRecv)
				if retGetLine >= 0:
					if "User-Agent:" in tmpRecv:
						self.log.info("sock:" + str(sock.fileno()) + " finding boundary we find useragent:" + " \n" + tmpRecv)
						isFoundUserAgent = 1
						if "Mozilla" in tmpRecv:
							self.log.info("sock:" + str(sock.fileno()) + " finding boundary we find useragent mozilla:" + " \n" + tmpRecv)
							isMozilla = 1
						break
		
		#seek to the end of upload head(before file content)
		if isMozilla == 1:
			#browser, to get end line
			retGetLine = 0
			while retGetLine >= 0:
				retGetLine, tmpRecv = self.getline(sock)
				self.log.info("sock:" + str(sock.fileno()) + " test get line run over end retGetLine:" + str(retGetLine) + " \n" + tmpRecv)
				if "Content-Type: " in tmpRecv:
					self.log.info("sock:" + str(sock.fileno()) + " test get line find content-type")
					#ignore \r\n
					retGetLine, tmpRecv = self.getline(sock) 
					break
		else:
			#cellphone to get end lne
			isFoundMidBoundary = 0
			retGetLine = 0
			while retGetLine >= 0:
				retGetLine, tmpRecv = self.getline(sock)
				self.log.info("sock:" + str(sock.fileno()) + " test get line in finding midboundary retGetLine:" + str(retGetLine) + " \n" + tmpRecv)
				if retGetLine >= 0 and isFoundMidBoundary == 0 and boundaryMid in tmpRecv:
					isFoundMidBoundary = 1
					continue
				if isFoundMidBoundary == 1:
					self.log.info("sock:" + str(sock.fileno()) + " upload after get boundaryMid - found end line!")
					break
		filePath = dirPath + "/" + name
		try:
			file = open(filePath, "wb")
		except:
			self.log.info("sock:" + str(sock.fileno()) + " open file error!!!")
			self.echo_msg(sock, self.genSimpleRtnMsg(path, SER_RTN_STATE_ERROR, SER_RTN_MSG_NOTPERMIT))
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
			self.log.info("sock:" + str(sock.fileno()) + " read upload recvLen:" + str(lenRecv))
			#self.log.info("sock:" + str(sock.fileno()) + " read upload recvData:" + str(recvRet))
			if lenRecv <= 0:
				if writeRetTotal >= fileSize:
					self.log.info("sock:" + str(sock.fileno()) + " recv recvRet<=0 cause writeRetTotal >= fileSize")
					break
				self.log.info("sock:" + str(sock.fileno()) + " recv overtimecnt:" + str(cntOverTime) + " start")
				time.sleep(0.1)
				self.log.info("sock:" + str(sock.fileno()) + " recv overtimecnt:" + str(cntOverTime) + " end")
				cntOverTime += 1
				if cntOverTime == 5:
					break
			else:
				cntOverTime = 0
				if lenRecv >= len(boundaryEnd):
					self.log.info("sock:" + str(sock.fileno()) + " enter check boundaryend")
					lenExceptBoundaryEnd = lenRecv - len(boundaryEnd)
					self.log.info("sock:" + str(sock.fileno()) + " enter check boundaryend lenExceptBoundaryEnd:" + str(lenExceptBoundaryEnd))
					tail = recvRet[lenExceptBoundaryEnd:]
					self.log.info("sock:" + str(sock.fileno()) + " enter check boundaryend tail:" + str(tail))
					if tail == boundaryEnd.encode("utf-8"):
						self.log.info("sock:" + str(sock.fileno()) + " enter check boundaryend find boundary end")
						file.write(recvRet[0:lenExceptBoundaryEnd])
						writeRetTotal += (lenRecv - len(boundaryEnd))
						self.log.info("sock:" + str(sock.fileno()) + " remove boundaryend write")
					else:
						file.write(recvRet)
						writeRetTotal += lenRecv
						self.log.info("sock:" + str(sock.fileno()) + " write upload total:" + str(writeRetTotal) + " fileSize:" + str(fileSize))
			time.sleep(0.001)

		self.log.info("sock:" + str(sock.fileno()) + " upload while out fileSize:" + str(fileSize) + " writeRetTotal:" + str(writeRetTotal))
		uploadSucc = 0
		if writeRetTotal >= fileSize:
			uploadSucc = 1
		self.clear_sock(sock)
		if uploadSucc == 0:
			self.echo_msg(sock, self.genSimpleRtnMsg(path, SER_RTN_STATE_ERROR, SER_RTN_MSG_TIMEOUT))
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
		
		self.log.info("uploadOpt() --- end!!!")
		
	def downloadOpt(self, sock, path):
		self.log.info("downloadOpt sock:" + str(sock.fileno()) + " path:" + path)
		try:
			filePath = self.gRootPath + path
			if self.isAccessPath(path):
				filePath = self.pathRemoveAccess(path)
			#避免传进来的还是带download的
			if "?download" in filePath:
				filePath = filePath.replace("?download", "")
			file = open(filePath, "rb")
			fileSize = self.http_get_file_size(filePath)
			isGetRange = 0
			getLineRet = 0
			fromBytes = -1
			toBytes = -1
			sendLen = -1

			while isGetRange == 0 :
				getLineRet, buf = self.getline(sock)
				self.log.info("sock:" + str(sock.fileno()) + " getLineRet:" + str(getLineRet) + " buf:" + str(buf))
				if getLineRet < 0:
					self.log.info("sock:" + str(sock.fileno()) + " downloadopt get_line timeout maybe there was no range")
					break
				if "Range: bytes=" in buf:
					isGetRange = 1
					buf = buf.replace("Range: bytes=", "")
					aryStr = buf.split("-")
					self.log.info("--------------> aryStr:" + str(aryStr))
					fromBytes = int(aryStr[0])
					strToBytes = aryStr[1]
					if len(strToBytes) >= 1:
						toBytes = int(strToBytes)
					if toBytes == -1:
						toBytes = fileSize
					if fromBytes == -1:
						fromBytes = 0
					sendLen = toBytes - fromBytes + 1
			self.log.info("sock:" + str(sock.fileno()) + " fromBytes:" + str(fromBytes) + " toBytes:" + str(toBytes) + " sendLen:" + str(sendLen))
			self.clear_sock(sock)
			if isGetRange == 1:
				self.echo_download_206(sock, fileSize, fromBytes, toBytes, sendLen)
			else:
				self.echo_download_200(sock, fileSize)
			self.clear_sock(sock)
			sock.settimeout(60)

			writeRet = 0
			readData = 0

			timeCur = 0
			timeLast = 0
			timeLast = time.time()
			lenDataPreSec = 0
			lenDataCur = 0
			lenDataTotal = 0
			lenDataPackage = 0

			lenDataTotal = fileSize
			defaultPackSize = MAX_PACKET_SIZE

			if isGetRange == 1:
				if fromBytes > 0:
					file.seek(fromBytes)
				lenDataTotal = toBytes - fromBytes + 1
			self.log.info("sock:" + str(sock.fileno()) + " downloadOpt() - fileSize:" + str(fileSize) + " from:" + str(fromBytes) + " lenTotal:" + str(lenDataTotal))
			while True:
				if lenDataTotal - lenDataCur >= defaultPackSize:
					lenDataPackage = defaultPackSize
				else:
					lenDataPackage = lenDataTotal - lenDataCur

				readData = file.read(lenDataPackage)
				if len(readData) <= 0:
					self.log.info("sock:" + str(sock.fileno()) + " downloadOpt() - write end~~~")
					time.sleep(1)
					file.close()
					self.log.info("sock:" + str(sock.fileno()) + " downloadOpt() - write end~~~ and close socket~~~")
					break
				else:
					writeRet = sock.send(readData)
					#self.log.info("sock:" + str(sock.fileno()) + "read:" + str(len(readData)) + " write:" + str(writeRet) + " packLen:" + str(lenDataPackage))
					lenDataCur += writeRet
					lenDataPreSec += lenDataPackage
					timeCur = time.time()
					if timeCur - timeLast >= 1:
						self.log.info("sock:" + str(sock.fileno()) + " " + str(lenDataCur) + "/" + str(lenDataTotal) + " speed:" + str(lenDataPreSec))
						timeLast = time.time()
						lenDataPreSec = 0
					time.sleep(0.005)
		except FileNotFoundError:
			self.log.info("sock:" + str(sock.fileno()) + " file not found!!!")
			return -1
		except IsADirectoryError:
			self.log.info("sock:" + str(sock.fileno()) + " is dir error!!!")
		except BrokenPipeError:
			self.log.info("sock:" + str(sock.fileno()) + " BrokenPipeError!!!")
		except:
			self.log.info(traceback.format_exc())
			self.log.info("sock:" + str(sock.fileno()) + " other exception!!!")
		finally:
			try:
				self.log.info("sock:" + str(sock.fileno()) + " finally close file~~~~")
				file.close()
			except:
				self.log.info("sock:" + str(sock.fileno()) + " finally close file error!!!")
			return 0

	def deleteFile(self, sock, urlpath, path):
		self.log.info("sock:" + str(sock.fileno()) + " deleteFile() path:" + path)
		ret = 0
		try:
			filePath = self.gRootPath + path
			if self.isAccessPath(path):
				filePath = self.pathRemoveAccess(path)
			#避免传进来的还是带download的
			if "?delete" in filePath:
				filePath = filePath.replace("?delete", "")
			os.remove(filePath)
			ret = 1
		except:
			self.log.info("deleteFile path:" + filePath + " error!!!")
			self.log.info(traceback.format_exc())
			ret = 0
		time.sleep(0.2)
		if ret == 0:
			self.echo_msg(sock, self.genSimpleRtnMsg(urlpath, SER_RTN_STATE_ERROR, SER_RTN_MSG_DELETEERR))
		else:
			self.echo_msg(sock, self.genSimpleRtnMsg(urlpath, SER_RTN_STATE_DONE, ""))

	def echo_showfile(self, path, sock):
		self.clear_sock(sock)
		self.log.info("sock:" + str(sock.fileno()) + " echo_showfile() path:" + path)
		try:
			#去掉参数
			if "?" in path:
				urlpath = path
				aryPath = path.split("?")
				path = aryPath[0]
				tail = aryPath[1]
				if tail == "download":
					return self.downloadOpt(sock, path)
				elif tail == "delete":
					return self.deleteFile(sock, urlpath, path)
			filePath = self.gRootPath + path
			if self.isAccessPath(path):
				filePath = self.pathRemoveAccess(path)
			file = open(filePath, "rb")
			name = os.path.basename(filePath)
			contentType = self.getContentType(name)
			self.log.info("path:" + filePath + " name:" + name + " contentType:" + contentType)
			self.echo_200(sock, contentType)
			cntLen = 0
			while True:
				ret = file.read(MAX_PACKET_SIZE)
				if len(ret) <= 0:
					self.log.info("sock:" + str(sock.fileno()) + " echo_showfile() - write end~~~")
					file.close()
					break
				else:
					sock.send(ret)
					cntLen += len(ret)
					time.sleep(0.005)
					#self.log.info("sock:" + str(sock.fileno()) + " echo_htmlfile() - write len:" + str(len(ret)) + " cntLen:" + str(cntLen))
		except FileNotFoundError:
			self.log.info("sock:" + str(sock.fileno()) + " file not found!!!")
			self.echo_msg(sock, self.genSimpleRtnMsg(path, SER_RTN_STATE_ERROR, SER_RTN_MSG_FILENOTFOUND))
			return -1
		except IsADirectoryError:
			self.log.info("sock:" + str(sock.fileno()) + " is dir error!!!")
			self.echo_msg(sock, self.genSimpleRtnMsg(path, SER_RTN_STATE_ERROR, SER_RTN_MSG_FILENOTFOUND))
		except:
			self.log.info("sock:" + str(sock.fileno()) + " other exception!!!")
			self.log.info(traceback.format_exc())
			self.echo_msg(sock, self.genSimpleRtnMsg(path, SER_RTN_STATE_ERROR, SER_RTN_MSG_FILENOTFOUND))
		finally:
			try:
				self.log.info("sock:" + str(sock.fileno()) + " echo_showfile() finally close file~~~~")
				file.close()
			except:
				self.log.info("sock:" + str(sock.fileno()) + " echo_showfile() finally close file error!!!")
			return 0

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
	
	def isSerPermitPath(self, path):
		ret = 0
		#self.log.info("test ---- " + path[0:len(SER_DIR_DATA)] + " ---- " + path[0:len(SER_DIR_WEB)])
		if path[0:len(SER_DIR_DATA)] == SER_DIR_DATA or path[0:len(SER_DIR_WEB)] == SER_DIR_WEB or path[0:len(SER_DIR_CMD)] == SER_DIR_CMD or path[0:len(SER_DIR_ACCESS)] == SER_DIR_ACCESS or path[0:len(SER_DIR_LOGS)] == SER_DIR_LOGS:
			ret = 1
		return ret
	
	def listDir(self, path):
		aryFiles = []
		try:
			fullPath = self.gRootPath + path
			if self.isAccessPath(path):
				fullPath = self.pathRemoveAccess(path)
			fileList = os.listdir(fullPath)
			fileList.sort()
			for i in fileList:
				tmpObj = {}
				tmpSize = -1
				tFileFullPath = os.path.join(fullPath, i)
				try:
					if not (os.path.isdir(tFileFullPath)):
						tmpSize = os.path.getsize(tFileFullPath)
					tmpObj[SER_FILE_NAME] = i
					tmpObj[SER_FILE_SIZE] = tmpSize
					aryFiles.append(tmpObj)
				except:
					self.log.info("get " + str(tFileFullPath) + " file info error!!!")
					continue
		except:
			self.log.info("listDir() path:" + str(path) + " error!!!")
			self.log.info(traceback.format_exc())
			aryFiles = []
		
		rtnObj = {}
		rtnObj[SER_FILE_PATH] = path
		rtnObj[SER_FILE_FILES] = aryFiles
		strRtn = str(rtnObj)
		strRtn = strRtn.replace("\'", "\"")
		return strRtn
	
	def get_time_stamp(self):
		ct = time.time()
		local_time = time.localtime(ct)
		data_head = time.strftime("%Y%m%d_%H%M%S", local_time)
		data_secs = (ct - int(ct)) * 1000
		time_stamp = "%s%03d" % (data_head, data_secs)
		return time_stamp

	def zipfilesOpt(self, sock, path):
		contentData = self.getContentData(sock)
		self.clear_sock(sock)
		try:
			jObj = json.loads(contentData)
			destPath = jObj[SER_ZIP_PATH]
			files = jObj[SER_ZIP_FILES]
			fullDestPath = ""
			isAccessPath = 0
			if self.isAccessPath(destPath):
				fullDestPath = self.pathRemoveAccess(destPath)
				isAccessPath = 1
			else:
				fullDestPath = self.gRootPath + destPath
			zipFileName = self.get_time_stamp() + ".zip"
			zipFileDestPath = fullDestPath + "/" + zipFileName
			zipFiles = []
			for tmpPath in files:
				if self.isAccessPath(tmpPath):
					tmpPath = self.pathRemoveAccess(tmpPath)
				else:
					tmpPath = self.gRootPath + tmpPath
				zipFiles.append(tmpPath)

			self.log.info("sock:" + str(sock.fileno()) + " zipfiles() dest:" + str(zipFileDestPath) + " files:" + str(zipFiles))

			zipFile = zipfile.ZipFile(zipFileDestPath,'w')
			for tmpPath in zipFiles:
				if os.path.isdir(tmpPath):
					for dirpath, dirnames, filenames in os.walk(tmpPath):
						self.log.info("--->(" + str(tmpPath) + "):" + str(dirpath) + " " + str(dirnames) + " " + str(filenames))
						for filename in filenames:
							writePath = os.path.join(dirpath, filename)
							namePath = writePath
							if isAccessPath:
								namePath = namePath.replace(fullDestPath, "")
							else:
								namePath = namePath.replace(self.gRootPath, "")
								namePath = namePath.replace(destPath, "")
							self.log.info("write ->(" + str(namePath) + ")")
							zipFile.write(writePath, namePath)
				else:
					name = os.path.basename(tmpPath)
					zipFile.write(tmpPath, name, zipfile.ZIP_DEFLATED)
				
			zipFile.close()

			rtnStr = self.genSimpleRtnMsg(path, SER_RTN_STATE_DONE, destPath + "/" + zipFileName)
			self.echo_msg(sock, rtnStr)
		except:
			self.log.info(traceback.format_exc())
			rtnStr = self.genSimpleRtnMsg(path, SER_RTN_STATE_ERROR, SER_RTN_MSG_REQUESTERR)
			self.echo_msg(sock, rtnStr)

			
		
	def isAccessPath(self, path):
		ret = 0
		tmp = path[1:]
		tmp = tmp[:len(SER_DIR_ACCESS)]
		#self.log.info("isAccessPath() -- " + str(tmp))
		if tmp == SER_DIR_ACCESS:
			ret = 1
		return ret
	
	def pathRemoveAccess(self, path):
		if platform.platform().find("Windows") >= 0:
			tmp = path[(1+len(SER_DIR_ACCESS)+1): ]
			if len(tmp) == 1:
				#只有盘符的情况
				tmp += ":/"
			else:
				#这里要在盘符后面加上:
				disk = tmp[0:1]
				last = tmp[1:]
				tmp = disk + ":" + last
		else:
			#ios 少加1个1，为了保留第一个斜杠
			tmp = path[(1+len(SER_DIR_ACCESS)): ]
		self.log.info("pathRemoveAccess() ---> " + str(tmp))
		return tmp

	def handle_client(self, sock, server_socket):
		#self.log.info("handleclient() enter sock:" + str(sock.fileno()))
		# 获取头
		ret, rtnStr = self.getline(sock)
		if ret < 0:
			self.log.info("sock:" + str(sock.fileno()) + " get_first_line error!!!")
			sock.close()
			return
		else:
			#self.log.info("sock:" + str(sock.fileno()) + " get_first_line:" + rtnStr)
			# 获取method 和 path
			pathAry = rtnStr.split(" ")
			method = pathAry[0]
			path = pathAry[1]
			# path = self.decodepath(path)
			path = urllib.parse.unquote(path)
			self.log.info("sock:" + str(sock.fileno()) + " method:" + method + " path:" + path)
			if rtnStr.find(SER_TAG_HTTP) >= 0:
				#HTTP 协议
				if method == SER_TAG_POST and len(path) > len(SER_TAG_UPLOAD) and (path[0:len(SER_TAG_UPLOAD)] == SER_TAG_UPLOAD):
					self.uploadOpt(sock, path)
				elif method == SER_TAG_POST and path == SER_TAG_ZIPFILE:
					self.zipfilesOpt(sock, path)
				else:
					if path == "/favicon.ico":
						path = "/web/favicon.ico"
					if path == "/":
						path = "/web/jump2index.html"
					if self.isSerPermitPath(path[1:]):
						contentType = self.getContentType(path)
						testPath = self.gRootPath + path
						if self.isAccessPath(path):
							testPath = self.pathRemoveAccess(path)
						#self.log.info("testPath ---> " + str(testPath))
						if os.path.isdir(testPath):
							self.echo_msg(sock, self.listDir(path))
						else:
							if "?download" not in path and "?delete" not in path and contentType == SER_CONTYPE_MP4:
								self.downloadOpt(sock, path)
							else:
								#echo对应类型和网页
								self.echo_showfile(path, sock)
					else:
						contentData = self.getContentData(sock)
						rtnStr = ""
						if platform.platform().find("Windows") >= 0:
							rtnStr = self.ctrl.handleRecv(path, contentData)
							
						else:
							rtnStr = self.genSimpleRtnMsg(path, SER_RTN_STATE_ERROR, SER_RTN_MSG_UNKNOWN)
						self.echo_msg(sock, rtnStr)
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
		# global gStartSer
		# gStartSer = 0
		time.sleep(0.5)
		server_socket.close()
		self.log.info('close server end 888~~~!!!!')
		return
	
	def markdownIPAddr(self):
		pathWebJs = os.path.abspath(os.path.join(sys.argv[0], "..")) + "/web/IP.js"
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(('8.8.8.8', 80))
		ip = s.getsockname()[0]
		self.log.info("markdownIPAddr() --- ip:" + str(ip))
		fd = open(pathWebJs, "w")
		fd.write("var DEV_IP = \"http://" + str(ip) + ":" + str(HTTP_PORT) + "\";\n")
		fd.write("var DEV_UE4_IP = \"http://" + str(ip) + ":" + str(8000) + "\";\n")
		fd.write("var DEV_CENTER_IP = \"http://" + str(ip) + ":" + str(8100) + "\";\n")
		fd.close()

	def markdownStartUp(self):
		self.log.info("markdownStartUp()")
		if platform.platform().find("Windows") >= 0:
			pathStartUp = "C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Startup"
			if os.path.exists(pathStartUp):
				self.log.info("exists startup path~")
				pathVbsFilePath = pathStartUp + self.getPathSeperater() + "Guard.vbs"
				pathStartGuard = os.path.abspath(os.path.join(sys.argv[0], "..")) + self.getPathSeperater() + "startGuard.bat"
				try:
					vbsFile = open(pathVbsFilePath, "w")
					tmpStr = "set ws=WScript.CreateObject(\"WScript.Shell\")"
					tmpStr += "\n"
					tmpStr += ("ws.Run \"" + pathStartGuard + "\"" + ", 0")
					self.log.info("markdownStartUp() content - \n" + str(tmpStr))
					self.log.info("markdownStartUp() Guard.vbs location:" + pathVbsFilePath)
					vbsFile.write(tmpStr)
					# set ws=WScript.CreateObject("WScript.Shell")
					# ws.Run "Z:\Documents\python_files\ue4pro\CenterServer\startGuard.bat", 0
				except:
					self.log.info("markdownStartUp() error!!!")
					self.log.info(traceback.format_exc())

		else:
			self.log.info("markdownStartUp() not support in " + str(platform.platform()))

	def __init__(self, name=__name__, log=None):
		self.log = log
		self.log.info('init()')
		webDir = self.gRootPath + self.getPathSeperater() + SER_DIR_WEB
		self.checkAndCreateDir(webDir)
		dataDir = self.gRootPath + self.getPathSeperater() + SER_DIR_DATA
		self.checkAndCreateDir(dataDir)
		cmdDir = self.gRootPath + self.getPathSeperater() + SER_DIR_CMD
		self.checkAndCreateDir(cmdDir)
		self.markdownStartUp()
		self.markdownIPAddr()
		params = []
		if len(sys.argv) > 1:
			params = list(sys.argv[1:])
			self.log.info("init() params ---> " + str(params))
		if platform.platform().find("Windows") >= 0:
			self.ctrl = GuardCtrl(params, self.log)
			self.ctrl.setPathCmdDir(cmdDir)
			self.ctrl.setPathDataDir(dataDir)
		#server
		server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		server_socket.setsockopt(socket.SOL_SOCKET, socket.TCP_NODELAY, 1)
		#扩大这个5M，可以提速，download 16K  send间隔时间缩短到0.01
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 7 * 1024 * 1024)
		server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 7 * 1024 * 1024)
		bufsize = server_socket.getsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF)
		print("------>buf size:" + str(bufsize))
		bufsize = server_socket.getsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF)
		print("------>buf size:" + str(bufsize))
		server_socket.bind(("", HTTP_PORT))
		server_socket.listen(1024)
		t = threading.Thread(target=self.handle_serverAccept, args=(server_socket, ))
		t.start()
		