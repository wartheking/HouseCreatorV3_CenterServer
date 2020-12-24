#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding:utf-8
import socket, json
import urllib.request
import sys, os, time, random, threading, multiprocessing
from multiprocessing import Process, Queue
from CenterGlobal import *
from light import *
from Logger import *
###########
gStartSer = 0
#记录当前是否在处理pro请求，每次只能处理一次pro，类似加锁
gIsHandlingPro = 0

log = getLogger()

#find non-busy servers and send req
def handle_SendReqToServers(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, mTaskId, mRatio):

	log.info("handle_SendReqToServers()")
	
	rtnMsg = "{\"" + JTAG_NAME + "\":\"" + mName + "\", \"" + JTAG_TASKTYPE + "\":\"" + mTaskType + "\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_BUSY + "\"}"
	
	jConfigStr = getSerConfigsStr()
	jConfig = json.loads(jConfigStr)

	jConfigAll = jConfig[JTAG_TASKTYPE_ALL]
	jConfigAllLen = len(jConfigAll)
	jConfigLight = jConfig[JTAG_TASKTYPE_LIGHT]
	jConfigLightLen = len(jConfigLight)
	jConfigDatafactory = jConfig[JTAG_TASKTYPE_DATAFACTORY]
	jConfigDatafactoryLen = len(jConfigDatafactory)
	
	mIndex = 0

	if mTaskType == JTAG_TASKTYPE_ALL:
		#遍历 all 群
		for jobj in jConfigAll:
			tName, tTaskType ,tState, tTaskId, tRatio, tStateStr = getCheckStateFromFile(mIndex)
			if tState == JTAG_STATE_DONE or tState == "":
				#done状态或者初始化状态就可以开始任务
				log.info("handle_SendReqToServers() find 'all' machine is ok index:" + str(mIndex))
				mSerIps, mSerAngles = getSerIpsAndSerAngles(jobj)
				return handle_SendReqToServers_all(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, mSerIps, mSerAngles, mTaskId, mRatio)
			elif tState == JTAG_STATE_ERROR:
				#错误状态的，server error 不能执行； 不是server error的可以执行（这些是有流程操作错误，最终还是完成了）
				if tStateStr.find(JTAG_MSG_SERVERERR) >= 0:
					#server err, 跳过吧
					mIndex += 1
					continue
				else:
					log.info("handle_SendReqToServers() find 'all' machine is error, but is ok index:" + str(mIndex))
					mSerIps, mSerAngles = getSerIpsAndSerAngles(jobj)
					return handle_SendReqToServers_all(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, mSerIps, mSerAngles, mTaskId, mRatio)
			else:
				mIndex += 1
				continue
			
		#如果遍历到最后了也没有机器可以运行这次任务，就返回默认的结果 isBusy
		return rtnMsg

	elif mTaskType == JTAG_TASKTYPE_LIGHT:
		#要加上all的数量
		mIndex = jConfigAllLen
		#遍历 light 群
		for ipStr in jConfigLight:
			tName, tTaskType, tState, tTaskId, tRatio, tStateStr = getCheckStateFromFile(mIndex)
			if tState == JTAG_STATE_DONE or tState == "":
				#done状态或者初始化状态就可以开始任务
				log.info("handle_SendReqToServers() find 'light' machine is ok index:" + str(mIndex))
				return handle_SendReqToServers_light(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, ipStr, mTaskId, mRatio)
			elif tState == JTAG_STATE_ERROR:
				#错误状态的，server error 不能执行； 不是server error的可以执行（这些是有流程操作错误，最终还是完成了）
				if tStateStr.find(JTAG_MSG_SERVERERR) >= 0:
					#server err, 跳过吧
					mIndex += 1
					continue
				else:
					log.info("handle_SendReqToServers() find 'light' machine is error, but is ok index:" + str(mIndex))
					return handle_SendReqToServers_light(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, ipStr, mTaskId, mRatio)
			else:
				mIndex += 1
				continue

		#如果遍历到最后了也没有机器可以运行这次任务，就返回默认的结果 isBusy
		return rtnMsg

	elif mTaskType == JTAG_TASKTYPE_DATAFACTORY:
		#要加上all + light的数量
		mIndex = jConfigAllLen + jConfigLightLen
		#遍历 datafactory 群
		for ipStr in jConfigDatafactory:
			tName, tTaskType, tState, tTaskId, tRatio, tStateStr = getCheckStateFromFile(mIndex)
			if tState == JTAG_STATE_DONE or tState == "":
				#done状态或者初始化状态就可以开始任务
				log.info("handle_SendReqToServers() find 'datafactory' machine is ok index:" + str(mIndex))
				return handle_SendReqToServers_datafactory(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, ipStr, mTaskId, mRatio)
			elif tState == JTAG_STATE_ERROR:
				#错误状态的，server error 不能执行； 不是server error的可以执行（这些是有流程操作错误，最终还是完成了）
				if tStateStr.find(JTAG_MSG_SERVERERR) >= 0:
					#server err, 跳过吧
					mIndex += 1
					continue
				else:
					log.info("handle_SendReqToServers() find 'datafactory' machine is error, but is ok index:" + str(mIndex))
					return handle_SendReqToServers_datafactory(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, ipStr, mTaskId, mRatio)
			else:
				mIndex += 1
				continue

		#如果遍历到最后了也没有机器可以运行这次任务，就返回默认的结果 isBusy
		return rtnMsg
	
#send 'all' request to servers one by one
def handle_SendReqToServers_all(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, mSerIps, mSerAngles, mTaskId, mRatio):
	cntServs = len(mSerIps)
	mIndex = -1
	rtnMsg = "{\"" + JTAG_NAME + "\":\"" + mName + "\", \"" + JTAG_TASKTYPE + "\":\"" + mTaskType + "\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_SERVERERR + "\"}"
	if cntServs <= 0:
		log.info("handle_SendReqToServers_all() SendReqSer Error servers cnt <=0 !!!!!")
	else:
		for ipStr in mSerIps:
			try:
				mIndex += 1
				#log.info("handle_SendReqToServers_all()[" + str(mIndex) + "]:" + "ip:" + ipStr + " position:" + str(mSerAngles[mIndex]))
				mAngle = mSerAngles[mIndex]
				dataStr = getJStrWithParams(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, mTaskId, mRatio)
				dataStrBytes = dataStr.encode('utf-8')
				#log.info("handle_SendReqToServers_all()[" + str(mIndex) + "]--dataStr:" + dataStr)
				url = ipStr + URL_PATH_PRO
				f = urllib.request.urlopen(url, dataStrBytes)
				rtnMsg = f.read().decode('utf-8')
				#log.info("handle_SendReqToServers_all()[" + str(mIndex) + "] rtn:" + rtnMsg)
				f.close()
				if rtnMsg.find(JTAG_STATE_ERROR) >= 0:
					log.info("handle_SendReqToServers_all()[" + str(mIndex) + "]:" + "ip:" + ipStr + "[" + rtnMsg + "] find rtn error!!!!")
					break
			except Exception:
				log.info("handle_SendReqToServers_all()[" + str(mIndex) + "]:" + "ip:" + ipStr + " request error!!!!")
				break
	return rtnMsg

#send 'light' request to server
def handle_SendReqToServers_light(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, ipStr, mTaskId, mRatio):
	rtnMsg = "{\"" + JTAG_NAME + "\":\"" + mName + "\", \"" + JTAG_TASKTYPE + "\":\"" + mTaskType + "\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_SERVERERR + "\"}"
	try:
		#log.info("handle_SendReqToServers_light() ip:" + ipStr)
		dataStr = getJStrWithParams(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, mTaskId, mRatio)
		dataStrBytes = dataStr.encode('utf-8')
		#log.info("handle_SendReqToServers_light()--dataStr:" + dataStr)
		url = ipStr + URL_PATH_PRO
		f = urllib.request.urlopen(url, dataStrBytes)
		rtnMsg = f.read().decode('utf-8')
		#log.info("handle_SendReqToServers_light() rtn:" + rtnMsg)
		f.close()
		if rtnMsg.find(JTAG_STATE_ERROR) >= 0:
			log.info("handle_SendReqToServers_light():" + "ip:" + ipStr + "[" + rtnMsg + "] find rtn error!!!!")
			
	except Exception:
		log.info("handle_SendReqToServers_light():" + "ip:" + ipStr + " request error!!!!")
				
	return rtnMsg

#send 'datafactory' request to server
def handle_SendReqToServers_datafactory(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, ipStr, mTaskId, mRatio):
	rtnMsg = "{\"" + JTAG_NAME + "\":\"" + mName + "\", \"" + JTAG_TASKTYPE + "\":\"" + mTaskType + "\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_SERVERERR + "\"}"
	try:
		#log.info("handle_SendReqToServers_light() ip:" + ipStr)
		dataStr = getJStrWithParams(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, mTaskId, mRatio)
		dataStrBytes = dataStr.encode('utf-8')
		#log.info("handle_SendReqToServers_light()--dataStr:" + dataStr)
		url = ipStr + URL_PATH_PRO
		f = urllib.request.urlopen(url, dataStrBytes)
		rtnMsg = f.read().decode('utf-8')
		#log.info("handle_SendReqToServers_light() rtn:" + rtnMsg)
		f.close()
		if rtnMsg.find(JTAG_STATE_ERROR) >= 0:
			log.info("handle_SendReqToServers_datafactory():" + "ip:" + ipStr + "[" + rtnMsg + "] find rtn error!!!!")
			
	except Exception:
		log.info("handle_SendReqToServers_datafactory():" + "ip:" + ipStr + " request error!!!!")
				
	return rtnMsg

def handle_CheckState():
	jConfigStr = getSerConfigsStr()
	jConfig = json.loads(jConfigStr)

	jConfigAll = jConfig[JTAG_TASKTYPE_ALL]
	jConfigAllLen = len(jConfigAll)
	#计数每个status文件
	mIndex = 0
	for jobj in jConfigAll:
		handle_CheckStatePreSec_allitem(mIndex, jobj)
		mIndex += 1

	jConfigLight = jConfig[JTAG_TASKTYPE_LIGHT]
	jConfigLightLen = len(jConfigLight)
	for ipStr in jConfigLight:
		handle_CheckStatePreSec_lightitem(mIndex, ipStr)
		mIndex += 1
	
	jConfigDatafactory = jConfig[JTAG_TASKTYPE_DATAFACTORY]
	jConfigDatafactoryLen = len(jConfigDatafactory)
	for ipStr in jConfigDatafactory:
		handle_CheckStatePreSec_datafactoryitem(mIndex, ipStr)
		mIndex += 1

# when get req pro 
# get every server state pre sec, until all done
def handle_CheckStatePreSec():
	global gStartSer
	while True:
		log.info("handle_CheckStatePreSec")
		handle_CheckState()
		if 	gStartSer == 0:
			log.info("server close, stop checking 88~~~~")
			return
		#keep sleep
		checkLogger()
		time.sleep(1)
		#break

def handle_CheckStatePreSec_allitem(index, jobj):
	#log.info("handle_CheckStatePreSec_allitem() [" + str(index) +"]")
	mSerIps, mSerAngles = getSerIpsAndSerAngles(jobj)
	cntServs = len(mSerIps)
	mIndex = -1
	mStateStr = "["
	mTmpStr = ""
	for ipStr in mSerIps:
		mIndex += 1
		#log.info("[" + str(mIndex) + "]:" + "ip:" + ipStr)
		try:
			url = ipStr + URL_PATH_CHECK
			f = urllib.request.urlopen(url)
			mTmpStr =  f.read().decode('utf-8')
			#log.info("[" + str(mIndex) + "]:" + mTmpStr)
			if mIndex == (cntServs - 1):
				mStateStr += mTmpStr
				mStateStr += "]"
			else:
				mStateStr += mTmpStr
				mStateStr += ","
			f.close()
		except urllib.error.URLError:
			log.info("[" + str(mIndex) + "]: check state error!!!!")
			# server err, will fill err info into state info
			errMsg = "{\"" + JTAG_NAME + "\":\"\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_SERVERERR + "\"}"
			if mIndex == (cntServs - 1):
				mStateStr += errMsg
				mStateStr += "]"
			else:
				mStateStr += errMsg
				mStateStr += ","
			continue
		except Exception:
			log.info("[" + str(mIndex) + "]: check state other error!!!!")
			errMsg = "{\"" + JTAG_NAME + "\":\"\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_SERVERERR + "\"}"
			if mIndex == (cntServs - 1):
				mStateStr += errMsg
				mStateStr += "]"
			else:
				mStateStr += errMsg
				mStateStr += ","

	log.info("all>>>[" + str(index) + "]combine str:" + mStateStr)
	setStausStrToStatusAry(index, mStateStr)

def handle_CheckStatePreSec_lightitem(index, ip):
	#log.info("handle_CheckStatePreSec_lightitem() [" + str(index) +"]")
	mStateStr = "["
	try:
		url = ip + URL_PATH_CHECK
		f = urllib.request.urlopen(url)
		mTmpStr =  f.read().decode('utf-8')
		log.info("[" + str(index) + "]:" + mTmpStr)
		mStateStr += mTmpStr
		mStateStr += "]"
		f.close()
	except urllib.error.URLError:
		log.info("[" + str(index) + "]: check state error!!!!")
		# server err, will fill err info into state info
		errMsg = "{\"" + JTAG_NAME + "\":\"\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_SERVERERR + "\"}"
		mStateStr += errMsg
		mStateStr += "]"
	except Exception:
		log.info("[" + str(index) + "]: check state other error!!!!")
		errMsg = "{\"" + JTAG_NAME + "\":\"\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_SERVERERR + "\"}"
		mStateStr += errMsg
		mStateStr += "]"

	log.info("light>>>[" + str(index) + "]combine str:" + mStateStr)
	setStausStrToStatusAry(index, mStateStr)

def handle_CheckStatePreSec_datafactoryitem(index, ip):
	#log.info("handle_CheckStatePreSec_lightitem() [" + str(index) +"]")
	mStateStr = "["
	try:
		url = ip + URL_PATH_CHECK
		f = urllib.request.urlopen(url)
		mTmpStr =  f.read().decode('utf-8')
		log.info("[" + str(index) + "]:" + mTmpStr)
		mStateStr += mTmpStr
		mStateStr += "]"
		f.close()
	except urllib.error.URLError:
		log.info("[" + str(index) + "]: check state error!!!!")
		# server err, will fill err info into state info
		errMsg = "{\"" + JTAG_NAME + "\":\"\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_SERVERERR + "\"}"
		mStateStr += errMsg
		mStateStr += "]"
	except Exception:
		log.info("[" + str(index) + "]: check state other error!!!!")
		errMsg = "{\"" + JTAG_NAME + "\":\"\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_SERVERERR + "\"}"
		mStateStr += errMsg
		mStateStr += "]"

	log.info("datafactory>>>[" + str(index) + "]combine str:" + mStateStr)
	setStausStrToStatusAry(index, mStateStr)

#handle accept socket request
def handle_client(client_socket, server_socket):
	request_data = client_socket.recv(10240)
	request_data_str = request_data.decode('utf-8')
	strAry = request_data_str.split('\r\n')
	#log.info("strAry:\n" + str(strAry))
	header = strAry[0]
	#log.info("[header]:" + header)
	headerAry = header.split()
	#log.info("headerAry:" + str(headerAry))
	mMethod = headerAry[0]
	mPath   = headerAry[1]
	#log.info("req method:" + mMethod + " path:" + mPath)
	#header
	response_start_line = "HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n"
	response_headers = "Server: 4Dage Center\r\n"
	
	#不是check的命令才打印完整的http请求信息
	if mPath != URL_PATH_CHECK:
		log.info("request_data:\n" + request_data_str)

	# if-else 处理各种请求
	if mPath == URL_PATH_GETLIGHTINFO:
		#get data from http req header content
		mContent = ""
		mIndex = -1
		isFindCntData = 0
		cntStrAry = len(strAry)
		for tmp in strAry:
			mIndex += 1
			#print("rptest[" + str(mIndex) + "]" + tmp)
			# find empty then next one is the last one , the next one is json data
			if tmp == "":
				if (mIndex + 1) < cntStrAry:
					nxtStr = strAry[mIndex + 1]
					nxtStrLen = len(nxtStr)
					#print("rptest nxtStr:" + nxtStr + " len:" + str(nxtStrLen) + " [0]:" + nxtStr[0])
					if nxtStrLen >= 1 and nxtStr[0] == "{":
						isFindCntData = 1
						#log.info("strary[" + str(mIndex) + "]" + tmp + " find contentdata")
						continue
			if isFindCntData == 1:
				mContent += tmp
		log.info("handle_client() recv 'getLightInfo' contentdata:" + mContent)
		isRightParams = 1
		resultStr = ""
		try:
			deploy = LightingDeploy()
			resultStr = deploy.deploy(mContent)
			log.info("getLightInfo() succ rtn:" + resultStr)
		except:
			log.info("handle_client() recv 'getLightInfo' --- run deploy error!!!!!!")
			isRightParams = 0

		if isRightParams == 1:
			response_body = "{\"" + JTAG_NAME + "\":\""+ mPath + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_DONE + "\",\"" + JTAG_MSG + "\":" + resultStr + "}"
		else:
			response_body = "{\"" + JTAG_NAME + "\":\""+ mPath + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_PARAMSERR + "\"}"
	#req history
	elif mPath == URL_PATH_HISTORY:
		response_body = readHistoryReqPro()
	#req check
	elif mPath == URL_PATH_CHECK:
		#get data from http req header content
		mContent = ""
		mIndex = -1
		isFindCntData = 0
		cntStrAry = len(strAry)
		for tmp in strAry:
			mIndex += 1
			#print("rptest[" + str(mIndex) + "]" + tmp)
			# find empty then next one is the last one , the next one is json data
			if tmp == "":
				if (mIndex + 1) < cntStrAry:
					nxtStr = strAry[mIndex + 1]
					nxtStrLen = len(nxtStr)
					#print("rptest nxtStr:" + nxtStr + " len:" + str(nxtStrLen) + " [0]:" + nxtStr[0])
					if nxtStrLen >= 1 and nxtStr[0] == "{":
						isFindCntData = 1
						#log.info("strary[" + str(mIndex) + "]" + tmp + " find contentdata")
						continue
			if isFindCntData == 1:
				mContent += tmp
		log.info("handle_client() recv 'check' contentdata:" + mContent)
		resultStr, result = getCheckState(mContent)
		if result < 0:
			response_body = "{\"" + JTAG_NAME + "\":\""+ mPath + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_PARAMSERR + "\"}"
		else:
			response_body = "{\"" + JTAG_NAME + "\":\""+ mPath + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_DONE + "\",\"" + JTAG_MSG + "\":" + resultStr + "}"
	
	#get configs
	elif mPath == URL_PATH_GETCFG:
		configStr = getSerConfigsStr()
		response_body = "{"
		response_body += "\"" + JTAG_NAME + "\":\"" + mPath + "\","
		response_body += "\"" + JTAG_STATE + "\":\"" + JTAG_STATE_DONE + "\","
		response_body += "\"" + JTAG_PARAMS + "\":" + configStr
		response_body += "}"
	
	#config servers 
	elif mPath == URL_PATH_CFG:
		isBusy = checkHasServerBusy()
		if isBusy:
			response_body = "{\"" + JTAG_NAME + "\":\""+ mPath + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_BUSY + "\"}"
		else:
			#get data from http req header content
			mContent = ""
			mIndex = -1
			isFindCntData = 0
			cntStrAry = len(strAry)
			for tmp in strAry:
				mIndex += 1
				#print("rptest[" + str(mIndex) + "]" + tmp)
				# find empty then next one is the last one , the next one is json data
				if tmp == "":
					if (mIndex + 1) < cntStrAry:
						nxtStr = strAry[mIndex + 1]
						nxtStrLen = len(nxtStr)
						#print("rptest nxtStr:" + nxtStr + " len:" + str(nxtStrLen) + " [0]:" + nxtStr[0])
						if nxtStrLen >= 1 and nxtStr[0] == "{":
							isFindCntData = 1
							#log.info("strary[" + str(mIndex) + "]" + tmp + " find contentdata")
							continue
				if isFindCntData == 1:
					mContent += tmp
			#log.info("contentdata:" + mContent)
			result = setConfigsFromJContent(mContent)
			if result >= 0:
				response_body = "{\"" + JTAG_NAME + "\":\""+ mPath + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_DONE + "\"}"
			else:
				response_body = "{\"" + JTAG_NAME + "\":\""+ mPath + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_PARAMSERR + "\"}"
	#byebye option
	elif mPath == URL_PATH_BYE:
		isBusy = checkHasServerBusy()
		if isBusy:
			response_body = "{\"" + JTAG_NAME + "\":\""+ mPath + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_BUSY + "\"}"
		else:
			response_body = "{\"" + JTAG_NAME + "\":\""+ mPath + "\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_DONE + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_BYE + "\"}"
			t = threading.Thread(target=handle_serverExit, args=(server_socket,))
			t.start()
	
	#handle pro
	elif mPath == URL_PATH_PRO:
		global gIsHandlingPro
		if gIsHandlingPro == 1:
			log.info("req pro but isHandlingPro return isBusy error!!!")
			response_body = "{\"" + JTAG_NAME + "\":\""+ mPath + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_BUSY + "\"}"
		else:
			gIsHandlingPro = 1
			#get data from http req header content
			mContent = ""
			mIndex = -1
			isFindCntData = 0
			cntStrAry = len(strAry)
			for tmp in strAry:
				mIndex += 1
				#print("rptest[" + str(mIndex) + "]" + tmp)
				# find empty then next one is the last one , the next one is json data
				if tmp == "":
					if (mIndex + 1) < cntStrAry:
						nxtStr = strAry[mIndex + 1]
						nxtStrLen = len(nxtStr)
						#print("rptest nxtStr:" + nxtStr + " len:" + str(nxtStrLen) + " [0]:" + nxtStr[0])
						if nxtStrLen >= 1 and nxtStr[0] == "{":
							isFindCntData = 1
							#log.info("strary[" + str(mIndex) + "]" + tmp + " find contentdata")
							continue
				if isFindCntData == 1:
					mContent += tmp
			#log.info("contentdata:" + mContent)
			mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, mTaskId, mRatio, result = getInfosFromJContent(mContent)
			#params error
			if result != 0:
				response_body = "{\"" + JTAG_NAME + "\":\""+ str(mName) + "\",\"" + JTAG_TASKTYPE + "\":\"" + mTaskType + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_PARAMSERR + "\"}"
				gIsHandlingPro = 0
			else:
				response_body = handle_SendReqToServers(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, mTaskId, mRatio)
				if response_body.find(JTAG_STATE_ERROR) >= 0:
					#包含错误的话，直接返回吧
					gIsHandlingPro = 0
				else:
					#直接更新状态再返回吧
					time.sleep(0.5)
					handle_CheckState()
					gIsHandlingPro = 0
					writeHistoryReqPro(mContent)
	#unknow
	else:
		response_body = "{\"" + JTAG_NAME + "\":\""+ mPath + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_UNKNOWN + "\"}"

	response = response_start_line + response_headers + "\r\n" + response_body
	#send resp
	client_socket.send(response.encode('utf-8'))
	#close socket
	client_socket.close()

def handle_serverAccept(server_socket):
	while True:
		try:
			client_socket, client_address = server_socket.accept()
			log.info("[%s, %s]connted" % client_address)
			t = threading.Thread(target=handle_client, args=(client_socket, server_socket,))
			t.start()
		except OSError:
			log.info('socket alreay closed 88!!!!!!!')
			return

def handle_serverExit(server_socket):
	log.info('ready to close server in one sec~')
	global gStartSer
	gStartSer = 0
	time.sleep(0.5)
	server_socket.close()
	log.info('close server end 888~~~!!!!')
	return

def startServer():
	#close recent server
	log.info("remove old server first~~~~222!")
	try:
		url = "http://127.0.0.1:" + str(HTTP_PORT) + URL_PATH_BYE
		f = urllib.request.urlopen(url)
		log.info(f.read().decode('utf-8'))
		f.close()
	except urllib.error.URLError:
		log.info("no exist server~~~~!")
	#init files
	initFiles()
	#server
	server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server_socket.bind(("", HTTP_PORT))
	server_socket.listen(10)
	t = threading.Thread(target=handle_serverAccept, args=(server_socket,))
	t.start()
	global gStartSer
	gStartSer = 1
	#check servs state
	t = threading.Thread(target=handle_CheckStatePreSec, args=())
	t.start()
	
	time.sleep(1)
	log.info('start server really successful~!')