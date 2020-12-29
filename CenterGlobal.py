#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding:utf-8
import socket, sys, os, json
import uuid, random, re, time

#states array
#每秒钟check的所有功能机群组的状态 都会按index来存储，存储可以导出jsonobj的字符串
#这样就不需要CenterStatus.txt_0/1/2... 这些文件了
ARY_STATUS = []
STATUS_MAX_LENGTH = 50

def initAryStatus():
	index = 0
	while index < STATUS_MAX_LENGTH:
		ARY_STATUS.append("")
		index += 1

#从statusAry 获取 某个机组的状态
def getStatusStrFromStatusAry(index):
	return ARY_STATUS[index]

#设置statusAry 某个机组的状态
def setStausStrToStatusAry(index, strStatus):
	ARY_STATUS[index] = strStatus

#normal
#DIR_PATH = os.path.abspath(os.path.dirname(__file__)) + "/SerFiles"
#windows for debug
DIR_PATH = os.path.abspath(os.path.join(sys.argv[0], "..")) + "/SerFiles"
LOG_DIR_PATH = DIR_PATH + "/log"
HISTORY_DIR_PATH = DIR_PATH + "/history"
INPUT_DIR_PATH = 'D:/OneKeyDecorate/Input/'
OUTPUT_DIR_PATH = 'D:/OneKeyDecorate/Output/'
FILE_PATH = DIR_PATH + "/CenterStatus.txt"
FILE_PARAM_PATH = DIR_PATH + "/CenterParams.txt"
FILE_DEV_PATH = DIR_PATH + "/CenterSerinfo.txt"
FILE_CFG_PATH = DIR_PATH + "/CenterSerConfigs.txt"
HTTP_PORT = 8100
HTTP_METHOD_GET = "GET"
HTTP_METHOD_POST = "POST"
HTTP_METHOD_CONTENTLENGTH = "Content-Length"
URL_PATH_CHECK = "/check"
URL_PATH_BYE   = "/bye"
URL_PATH_PRO   = "/pro"
URL_PATH_CFG   = "/config"
URL_PATH_GETCFG   = "/getConfig"
URL_PATH_HISTORY = "/history"
URL_PATH_GETLIGHTINFO = "/getLightInfo"
URL_PATH_FIXMODEL = "/fixmodel"
JTAG_NAME  = "name"
JTAG_TASKTYPE = "taskType"
JTAG_TASKTYPE_ALL = "all"
JTAG_TASKTYPE_LIGHT = "light"
JTAG_TASKTYPE_DATAFACTORY = "datafactory"
JTAG_TASKTYPE_FIXMODEL = "fixmodel"
JTAG_MAP   = "map"
JTAG_ANGLE = "angle"
JTAG_IDS = "ids"
JTAG_POSITION_INDEX = "index"
JTAG_POSITION_LEN   = "len"
JTAG_RESOLUTION = "resolution"
JTAG_QUALITY = "quality"
JTAG_RATIO = "ratio"
JTAG_TASKID = "taskId"
JTAG_POSTFIX = "postfix"
JTAG_SERIPS  = "SER_IPS"
JTAG_SERANGLES = "SER_ANGLES"
JTAG_SIMPLEMODEL = "simpleModel"
JTAG_PROGRESS = "progress"
JTAG_MSG   = "msg"
JTAG_MSG_BUSY = "isBusy"
JTAG_MSG_BYE  = "byebye"
JTAG_MSG_UNKNOWN  = "unknown"
JTAG_MSG_PARAMSERR = "params error"
JTAG_MSG_SERVERERR = "server error"
JTAG_STATE            = "state"
JTAG_PARAMS           = "params"
JTAG_STATE_DONE       = "done"
JTAG_STATE_ERROR      = "error"
JTAG_STATE_READY      = "ready"
JTAG_STATE_INPROGRESS = "inprogress"
JTAG_STATE_READYRENDER = "readyrender"
JTAG_STATE_INRENDER = "inrender"
JTAG_STATE_READYCOMPRESS = "readycompress"
JTAG_STATE_INCOMPRESS = "incompress"
JTAG_STATE_NONE = "none"

def checkAndCreateDir(path):
	#创建SerFiles文件夹
	isExists = os.path.exists(path)
 
	# 判断结果
	if not isExists:
		# 如果不存在则创建目录
		# 创建目录操作函数
		os.makedirs(path) 
		print(path + ' 创建成功')
	else:
		# 如果目录存在则不创建，并提示目录已存在
		print(path + ' 目录已存在')

#这里才导入logger，因为logger也引用Global，先将全局的定义先加载
#不然logger用到Global的时候会找不到定义
from Logger import *
log = getLogger()

#init files
def initFiles():

	#check 文件夹都创建没有
	checkAndCreateDir(DIR_PATH)
	checkAndCreateDir(LOG_DIR_PATH)
	checkAndCreateDir(HISTORY_DIR_PATH)

	#init status_ary
	initAryStatus()

	#log.info("DIR_PATH:" + DIR_PATH)
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(('8.8.8.8', 80))
	ip = s.getsockname()[0]
	s.close()
	identity = str(uuid.uuid4()).encode('ascii')
	code = str(identity) + str(ip)
	code = code.replace(".", "")
	code = code.replace("'", "")
	code = str(random.randrange(0, 1000, 2)) + code
	log.info("ser info - [ip:" + ip + "][port:" + str(HTTP_PORT) + "][platform:" + sys.platform + "]")
	#write server infos
	try:
		log.info("serinfo.txt - " + FILE_DEV_PATH)
		file = open(FILE_DEV_PATH, "w")
		file.write("{\"ip\":\""+ str(ip) + "\",\"port\":" + str(HTTP_PORT) + ",\"uuid\":\"" + code + "\"}")
		file.close()
	except IOError:
		log.info("serinfo.txt file error!!!")
	log.info("starting server~")
	#clear state.txt
	#暂时不用吧
	# try:
	# 	file = open(FILE_PATH, "w")
	# 	file.write("[]")
	# 	file.close()
	# except IOError:
	# 	log.info("serinfo.txt file error!!!")
	#create params.txt
	try:
		file = open(FILE_PARAM_PATH, "w")
		file.close()
	except IOError:
		log.info("serinfo.txt file error!!!")

#get server info from serinfo.txt
def getSerInfo():
	mIp   = ""
	mPort = HTTP_PORT
	mUUID = ""
	try:
		file = open(FILE_DEV_PATH, "r")
		tmpStr = file.read(1024)
		#log.info('file content:' + tmpStr + ' len:' + str(len(tmpStr)))
		jobj = json.loads(tmpStr)
		if("ip" in jobj.keys()):
			mIp  = jobj["ip"]
		if("port" in jobj.keys()):
			mPort  = jobj["port"]
		if("uuid" in jobj.keys()):
			mUUID = jobj["uuid"]
		file.close()
	except IOError :
		log.info("ser file error, now try create one!!!")
		file = open(FILE_PATH, "w")
		file.close()
	except json.decoder.JSONDecodeError:
		log.info("ser file does not contain json data!!!")
	log.info("getSerInfo -- ip:" + mIp + " port:" + str(mPort) + " uuid:" + mUUID)
	return mIp, mPort, mUUID

#get infos from request content json string
def getInfosFromJContent(jContent):
	mName= ""
	mTaskType = JTAG_TASKTYPE_ALL
	mMap = ""
	mAngle = [0, 1, 2, 3, 4, 5]
	mIds = [-1]
	mResolution = 1024
	mQuality = 0
	mTaskId = ""
	mRatio = ""
	mPostfix = ""
	result = 0
	while(1):
		try:
			jobj = json.loads(jContent)
			#check name
			if(JTAG_NAME in jobj.keys()):
				mName  = jobj[JTAG_NAME]
				mName, result = checkName(mName)
				if result < 0:
					break
			else:
				log.info("content json data name not find error!!!")
				result = -1
				break
			#check tasktype
			if(JTAG_TASKTYPE in jobj.keys()):
				mTaskType = jobj[JTAG_TASKTYPE]
				mTaskType, result = checkTaskType(mTaskType)
				if result < 0:
					break
			else:
				log.info("content json data resolution not find error!!!")
				result = -1
				break

			#if taskType == light
			#check taskId and Ratio
			if mTaskType == JTAG_TASKTYPE_LIGHT:
				#check taskId
				if (JTAG_TASKID in jobj.keys()):
					mTaskId = jobj[JTAG_TASKID]
					mTaskId, result = checkTaskId(mTaskId)
					if result < 0:
						break
				else:
					log.info("content json data taskId not find error!!!")
					result = -1
					break
				#check ratio
				if (JTAG_RATIO in jobj.keys()):
					mRatio = jobj[JTAG_RATIO]
					mRatio, result = checkRatio(mRatio)
					if result < 0:
						break
				else:
					log.info("content json data ratio not find error!!!")
					result = -1
					break
			
			#if taskType == datafactory
			# taskId,postfix必须有
			if mTaskType == JTAG_TASKTYPE_DATAFACTORY:
				#check taskId
				if (JTAG_TASKID in jobj.keys()):
					mTaskId = jobj[JTAG_TASKID]
					mTaskId, result = checkTaskId(mTaskId)
					if result < 0:
						break
				else:
					log.info("content json data taskId not find error!!!")
					result = -1
					break
				#check postfix
				if (JTAG_POSTFIX in jobj.keys()):
					mPostfix = jobj[JTAG_POSTFIX]
					mPostfix, result = checkPostfix(mPostfix)
					if result < 0:
						break
				else:
					log.info("content json data postfix not find error!!!")
					result = -1
					break

			if mTaskType != JTAG_TASKTYPE_DATAFACTORY:
				#check map
				if(JTAG_MAP in jobj.keys()):
					mMap  = jobj[JTAG_MAP]
					mMap, result = checkMap(mMap)
					if result < 0:
						break
				else:
					log.info("content json data map not find error!!!")
					result = -1
					break
				#check quality
				if(JTAG_QUALITY in jobj.keys()):
					mQuality  = jobj[JTAG_QUALITY]
					mQuality, result = checkQuality(mQuality)
					if result < 0:
						break
				#check ids
				if(JTAG_IDS in jobj.keys()):
					mIds = jobj[JTAG_IDS]
					mIds, result = checkIds(mIds)
					if result < 0:
						break
				else:
					log.info("content json data position not find error!!!")
					result = -1
					break
				#check angle
				if(JTAG_ANGLE in jobj.keys()):
					mAngle  = jobj[JTAG_ANGLE]
					mAngle, result = checkAngle(mAngle)
					if result < 0:
						break
				#check resolution
				if(JTAG_RESOLUTION in jobj.keys()):
					mResolution  = jobj[JTAG_RESOLUTION]
					mResolution, result = checkResolution(mResolution)
					if result < 0:
						break
				else:
					log.info("content json data resolution not find error!!!")
					result = -1
					break
			#check end break while
			break
		except json.decoder.JSONDecodeError:
			result = -1
			log.info("conntent json data error!!!")
			break
	log.info("getInfosFromJContent -- name:" + str(mName) + " map:" + str(mMap) + " angle:" + str(mAngle) + " ids:" + str(mIds) + " resolution:" + str(mResolution) + " quality:" + str(mQuality) + " taskType:" + str(mTaskType) + " taskId:" + str(mTaskId) + " ratio:" + str(mRatio) + " postfix:" + str(mPostfix)  + " result:" + str(result))
	return mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, mTaskId, mRatio, mPostfix, result

def checkName(name):
	result = -1
	if not isinstance(name, str):
		log.info("name is not string error!!!")
		result = -1
	elif name == "":
		log.info("name is empty error!!!")
		result = -1
	else:
		result = 0
	return name, result

def checkMap(map):
	result = -1
	if not isinstance(map, str):
		log.info("map is not string error!!!")
		result = -1
	elif map == "":
		log.info("map is empty error!!!")
		result = -1
	else:
		result = 0
	return map, result

def checkQuality(quality):
	result = -1
	if not isinstance(quality, int):
		log.info("quality is not int error!!!")
		result = -1
	elif quality != 0 and quality != 1 and quality != 2:
		log.info("quality out of range error!!!")
		result = -1
	else:
		result = 0
	return quality, result

def checkIds(ids):
	result = -1
	if not isinstance(ids, list):
		log.info("ids is not list!!!")
		result = -1
	elif len(ids) < 1:
		log.info("ids length error!!!")
		result = -1
	elif not (len(ids) == 1 and isinstance(ids[0], int) and ids[0] > -2):
		#如果只有一个值，只能是-1 或者大于0
		log.info("ids len = 1 and ids[0] < -1 error!!!")
		result = -1
	else:
		index = -1
		for tmp in ids:
			index += 1
			if not isinstance(tmp, int) or tmp < 0:
				if index == 0 and tmp == -1:
					continue
				result = -1
				log.info("ids's child is not int or < 0 error!!!")
				return ids, result 
		result = 0
	return ids, result

def checkAngle(angle):
	result = -1
	if not isinstance(angle, list):
		log.info("angle is not list error!!!")
		result = -1
	elif len(angle) <= 0:
		log.info("angle length <= 0 error!!!")
		result = -1
	else:
		for tmp in angle:
			if not isinstance(tmp, int) or tmp < 0 or tmp > 5:
				result = -1
				log.info("angle's child is not int or < 0 or > 5 error!!!")
				return angle, result
		#check have the same number
		index = 0
		for num1 in angle:
			curIndex = 0
			for num2 in angle:
				#log.info("num1:" + str(num1) + " num2:" + str(num2) + " curIndex:" + str(curIndex) + " index:" + str(index))
				if curIndex > index:
					if num1 == num2:
						log.info("angle's child has same number error!!!")
						return angle, result
				curIndex += 1
			index += 1
		result = 0
	return angle, result

def checkResolution(resolution):
	result = -1
	if not isinstance(resolution, int):
		log.info("resolution is not int error!!!")
		result = -1
	elif resolution != 1024 and resolution != 2048 and resolution != 4096:
		log.info("resolution out of range error!!!")
		result = -1
	else:
		result = 0
	return resolution, result

def checkTaskType(taskType):
	result = -1
	if not isinstance(taskType, str):
		log.info("taskType is not str error!!!")
		result = -1
	elif taskType != JTAG_TASKTYPE_ALL and taskType != JTAG_TASKTYPE_LIGHT and taskType != JTAG_TASKTYPE_DATAFACTORY:
		log.info("taskType not right error!!!")
		result = -1
	else:
		result = 0
	return taskType, result

def checkTaskId(taskId):
	result = -1
	if not isinstance(taskId, str):
		log.info("taskId is not str error!!!")
		result = -1
	elif len(taskId) <= 0:
		log.info("taskId len <= 0 error!!!")
		result = -1
	else:
		result = 0
	return taskId, result

def checkRatio(ratio):
	result = -1
	if not isinstance(ratio, str):
		log.info("ratio is not str error!!!")
		result = -1
	elif len(ratio) <= 0:
		log.info("ratio len <= 0 error!!!")
		result = -1
	else:
		result = 0
	return ratio, result

def checkPostfix(postfix):
	result = -1
	if not isinstance(postfix, str):
		log.info("postfix is not string error!!!")
		result = -1
	elif postfix == "":
		log.info("postfix is empty error!!!")
		result = -1
	else:
		result = 0
	return postfix, result

#检查状态， 返回多个或单个状态
#如果jContentStr 不为空，及包含 name 和 taskType 就返回对应的状态回去（如果多个 name 和 taskType 相同，会返回多个）
#如果jContentStr 为空，就会返回所有状态文件的状态回去
#如果参数由问题，就返回参数有错误
def getCheckState(jContentStr):
	#log.info("getCheckState() - jContentStr:" + str(jContentStr))
	resultStr = ""
	result = 0
	mName = ""
	mTaskType = ""
	mTaskId = ""
	mRatio = ""
	isShowAll = False
	if len(jContentStr) <= 0:
		isShowAll = True
	else:
		while True:
			try:
				jobj = json.loads(jContentStr)

				#check taskType
				if JTAG_TASKTYPE in jobj.keys():
					mTaskType = jobj[JTAG_TASKTYPE]
					mTaskType, result = checkTaskType(mTaskType)
					if result < 0:
						log.info("getCheckState() read json mTaskType error!!!")
						result = -1
						break
				else:
					log.info("getCheckState() read json not find tasktype error!!!")
					result = -1
					break

				#check name
				if JTAG_NAME in jobj.keys():
					mName = jobj[JTAG_NAME]
					#tasktype all 才要判断 name有没有问题
					#tasktype datafactory 也要判断name有没有问题，敬然说name是标识，taskId只是存个文件夹
					if mTaskType == JTAG_TASKTYPE_ALL or mTaskType == JTAG_TASKTYPE_DATAFACTORY :
						mName, result = checkName(mName)
						if result < 0:
							log.info("getCheckState() read json name error!!!")
							break
				else:
					#tasktype all 才要判断 name是否是空
					#tasktype datafactory 也要判断name有没有问题，敬然说name是标识，taskId只是存个文件夹
					if mTaskType == JTAG_TASKTYPE_ALL or mTaskType == JTAG_TASKTYPE_DATAFACTORY :
						log.info("getCheckState() read json not find name!!!")
						result = -1
						break
				
				#check taskid 是否存在
				if mTaskType == JTAG_TASKTYPE_LIGHT:
					if JTAG_TASKID in jobj.keys():
						mTaskId = jobj[JTAG_TASKID]
						mTaskId, result = checkTaskId(mTaskId)
						if result < 0:
							log.info("getCheckState() read json taskId error!!!")
							break
					else:
						log.info("getCheckState() read json not find taskId!!!")
						result = -1
						break

				# 两个都没问题就直接找对口的返回吧
				break
			except:
				log.info("getCheckState() read json error!!!")
				result = -1
				break
	
	if result < 0:
		#参数有错误，直接返回
		return resultStr, result

	#开始封装返回数据
	resultStr = "["

	jConfigStr = getSerConfigsStr()
	jConfig = json.loads(jConfigStr)

	jConfigAll = jConfig[JTAG_TASKTYPE_ALL]
	jConfigAllLen = len(jConfigAll)

	jConfigLight = jConfig[JTAG_TASKTYPE_LIGHT]
	jConfigLightLen = len(jConfigLight)

	jConfigDatafactory = jConfig[JTAG_TASKTYPE_DATAFACTORY]
	jConfigDatafactoryLen = len(jConfigDatafactory)

	#计数每个status文件
	mIndex = 0
	#遍历 all 群
	for jobj in jConfigAll:
		tName, tTaskType ,tState, tTaskId, tRatio, tPostfix, tStateStr = getCheckStateFromFile(mIndex)
		if isShowAll:
			resultStr += tStateStr
			resultStr += ","
		else:
			if mTaskType == JTAG_TASKTYPE_ALL and tName == mName and tTaskType == mTaskType:
				resultStr += tStateStr
				resultStr += ","
		mIndex += 1
	#遍历 light 群
	for ipStr in jConfigLight:
		tName, tTaskType ,tState, tTaskId, tRatio, tPostfix, tStateStr = getCheckStateFromFile(mIndex)
		#修复原本是light，显示all，因默认都是all，这里将all转化成light，好看一点
		if tTaskType == JTAG_TASKTYPE_ALL:
			tStateStr = tStateStr.replace(JTAG_TASKTYPE_ALL, JTAG_TASKTYPE_LIGHT)
		if isShowAll:
			resultStr += tStateStr
			resultStr += ","
		else:
			if mTaskType == JTAG_TASKTYPE_LIGHT and tTaskId == mTaskId and tTaskType == mTaskType:
				resultStr += tStateStr
				resultStr += ","
		mIndex += 1
	
	#遍历 datafactory 群
	for ipStr in jConfigDatafactory:
		tName, tTaskType ,tState, tTaskId, tRatio, tPostfix, tStateStr = getCheckStateFromFile(mIndex)
		#修复原本是light，显示all，因默认都是all，这里将all转化成datafactory，好看一点
		if tTaskType == JTAG_TASKTYPE_ALL:
			tStateStr = tStateStr.replace(JTAG_TASKTYPE_ALL, JTAG_TASKTYPE_DATAFACTORY)
		if isShowAll:
			resultStr += tStateStr
			resultStr += ","
		else:
			if mTaskType == JTAG_TASKTYPE_DATAFACTORY and tName == mName and tTaskType == mTaskType:
				resultStr += tStateStr
				resultStr += ","
		mIndex += 1
	
	log.info("getCheckState() -- tmp result str["+ resultStr +"]")
	#去掉最后一个逗号
	totalLen = len(resultStr)
	if not isShowAll and totalLen <= 1:
		log.info("getCheckState() -- can not find["+ mName +"]["+ mTaskType +"]" + " state!!!")
	else:
		if totalLen > 1:
			resultStr = resultStr[0:(totalLen-1)]
	#完成整个返回数据的封装	
	resultStr += "]"

	log.info("getCheckState() -- " + resultStr)
	return resultStr, result

#get now server state file info-state info-name and paramsAry of each server
def getCheckStateFromFile(index):
	#log.info("getCheckStateFromFile() index:" + str(index))
	#for return
	mName = ""
	mTaskType = JTAG_TASKTYPE_ALL
	mState = JTAG_STATE_ERROR
	mSimpleModel = JTAG_STATE_NONE
	mMsg = ""
	mProgress = 0
	mProgressAry = []
	mTaskId = ""
	mRatio = ""
	mPostfix = ""
	mStateStr = "{"
	mStateStr += "\"" + JTAG_NAME + "\":\"" + mName + "\","
	mStateStr += "\"" + JTAG_TASKTYPE + "\":\"" + mTaskType + "\","
	mStateStr += "\"" + JTAG_STATE + "\":\"" + mState + "\","
	mStateStr += "\"" + JTAG_PROGRESS + "\":" + str(mProgress) + ","
	mStateStr += "\"" + JTAG_TASKID + "\":\"" + mTaskId + "\","
	mStateStr += "\"" + JTAG_RATIO + "\":\"" + mRatio + "\","
	mStateStr += "\"" + JTAG_POSTFIX + "\":\"" + mPostfix + "\","
	mStateStr += "\"" + JTAG_MSG + "\":\"" + mMsg + "\","
	mStateStr += "\"" + JTAG_SIMPLEMODEL + "\":\"" + JTAG_STATE_NONE + "\","
	mStateStr += "\"" + JTAG_PARAMS + "\":[]"
	mStateStr += "}"
	#tmp
	tName  = ""
	tState = ""
	try:
		tmpStr = getStatusStrFromStatusAry(index)
		jobj = json.loads(tmpStr)
		mIndex = -1
		aryName = []
		aryState = []
		for tmpObj in jobj:
			mIndex += 1
			tName  = ""
			tState = ""
			if(JTAG_NAME in tmpObj.keys()):
				tName  = tmpObj[JTAG_NAME]
				aryName.append(tName)
			if(JTAG_STATE in tmpObj.keys()):
				tState  = tmpObj[JTAG_STATE]
				aryState.append(tState)
				if tState == JTAG_STATE_ERROR and JTAG_MSG in tmpObj.keys() and mMsg != JTAG_MSG_SERVERERR:
					mMsg = tmpObj[JTAG_MSG]
			if(JTAG_SIMPLEMODEL in tmpObj.keys()):
				#MARK "simpleModel":{"name":"xxx", "simpleModel":"done"}
				tSimpleModelObj = tmpObj[JTAG_SIMPLEMODEL]
				if tSimpleModelObj != None and (JTAG_SIMPLEMODEL in tSimpleModelObj.keys()):
					mSimpleModel = tSimpleModelObj[JTAG_SIMPLEMODEL]
			if(JTAG_TASKTYPE in tmpObj.keys()):
				mTaskType = tmpObj[JTAG_TASKTYPE]
			if(JTAG_PROGRESS in tmpObj.keys()):
				#记录所有的progress，最后算平均数
				mProgressAry.append(tmpObj[JTAG_PROGRESS])
				#第一个progress直接赋值
				# if mIndex == 0:
				# 	mProgress = tmpObj[JTAG_PROGRESS]
				# else:
				# 	#找最小的那个progress
				# 	if mProgress > tmpObj[JTAG_PROGRESS]:
				# 		mProgress = tmpObj[JTAG_PROGRESS]
			#获取taskId 和 ratio 和 postfix
			if mIndex == 0:
				if JTAG_TASKID in tmpObj.keys() :
					mTaskId = tmpObj[JTAG_TASKID]
				if JTAG_RATIO in tmpObj.keys() :
					mRatio = tmpObj[JTAG_RATIO]
				if JTAG_POSTFIX in tmpObj.keys():
					mPostfix = tmpObj[JTAG_POSTFIX]


		cntAryName = len(aryName)
		if cntAryName > 0 :
			mName = aryName[0]
		#TODO - check names are the same
		cntAryState = len(aryState)
		#TODO check cntAryState <= 0
		countDone = 0
		countEmpty = 0
		countError = 0
		for tmpState in aryState:
			if tmpState == JTAG_STATE_DONE:
				countDone += 1
			elif tmpState == "":
				countEmpty += 1
			elif tmpState == JTAG_STATE_ERROR:
				countError += 1
		if countDone == cntAryState:
			#log.info("all done~~~")
			mState = JTAG_STATE_DONE
		elif countEmpty == cntAryState:
			#log.info("all empty~~~")
			mState = ""
		elif (countDone + countEmpty) == cntAryState:				
			#log.info("all finished, empty and done~~~")
			mState = ""
		elif countDone + countEmpty + countError == cntAryState:
			#log.info("all finished, but have errors!!!!!!")
			mState = JTAG_STATE_ERROR
		else:
			#log.info("inprogressing~~~")
			mState = JTAG_STATE_INPROGRESS

		#求progress平均数
		lenProgressAry =  len(mProgressAry)
		if lenProgressAry <= 0:
			log.info("len progressAry <= 0 get average progress error!!!")
		else:
			sumProgress = 0
			for progress in mProgressAry:
				sumProgress += progress
			mProgress = round(sumProgress / lenProgressAry)
		# log.info("------------> progressary:" + str(mProgressAry))

		#log.info("aryName:" + str(aryName) + " aryState:" + str(aryState) + " name:" + mName + " taskType:" + mTaskType + " state:" + mState + " countDone:" + str(countDone) + " countEmpty:" + str(countEmpty) + " countError:" + str(countError))
		mStateStr = "{"
		mStateStr += "\"" + JTAG_NAME + "\":\"" + mName + "\","
		mStateStr += "\"" + JTAG_TASKTYPE + "\":\"" + mTaskType + "\","
		mStateStr += "\"" + JTAG_STATE + "\":\"" + mState + "\","
		mStateStr += "\"" + JTAG_PROGRESS + "\":" + str(mProgress) + ","
		mStateStr += "\"" + JTAG_TASKID + "\":\"" + mTaskId + "\","
		mStateStr += "\"" + JTAG_RATIO + "\":\"" + mRatio + "\","
		mStateStr += "\"" + JTAG_POSTFIX + "\":\"" + mPostfix + "\","
		mStateStr += "\"" + JTAG_MSG + "\":\"" + mMsg + "\","
		mStateStr += "\"" + JTAG_SIMPLEMODEL + "\":\"" + mSimpleModel + "\","
		mStateStr += "\"" + JTAG_PARAMS + "\":" + tmpStr
		mStateStr += "}"
	except IOError :
		log.info("state file error, now try create one!!!")
	except json.decoder.JSONDecodeError:
		log.info("state file does not contain json data!!!")
	#except Exception :
	#	log.info("state file data error!!!")
	#log.info("getCheckStateFromFile -- name:" + mName + " taskType:" + mTaskType + " state:" + mState + " progress:" + str(mProgress) + " taskId:" + str(mTaskId) + " ratio:" + str(mRatio) + " postfix:" + str(mPostfix) + " mStateStr:" + mStateStr)
	return mName, mTaskType ,mState, mTaskId, mRatio, mPostfix, mStateStr

#get jsonstr with all params
def getJStrWithParams(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, mTaskId, mRatio, mPostfix):
	rtnStr = "{"
	rtnStr += "\"" + JTAG_NAME + "\":\"" + mName + "\","
	rtnStr += "\"" + JTAG_TASKTYPE + "\":\"" + mTaskType + "\","
	rtnStr += "\"" + JTAG_MAP + "\":\"" + mMap + "\","
	rtnStr += "\"" + JTAG_ANGLE + "\":" + str(mAngle) + ","
	rtnStr += "\"" + JTAG_IDS + "\":" + str(mIds) + ","
	rtnStr += "\"" + JTAG_RESOLUTION + "\":" + str(mResolution) + ","
	rtnStr += "\"" + JTAG_QUALITY + "\":" + str(mQuality) + ","
	rtnStr += "\"" + JTAG_TASKID + "\":\"" + mTaskId + "\","
	rtnStr += "\"" + JTAG_RATIO + "\":\"" + mRatio + "\","
	rtnStr += "\"" + JTAG_POSTFIX + "\":\"" + mPostfix + "\""
	rtnStr += "}"
	return rtnStr

#get configs file content
def getSerConfigsStr():
	rtnStr = "{\"" + JTAG_TASKTYPE_ALL + "\":[], \"" + JTAG_TASKTYPE_LIGHT + "\":[], \""+ JTAG_TASKTYPE_DATAFACTORY + "\":[]}"
	try:
		file = open(FILE_CFG_PATH, "r")
		tmpStr = file.read()
		#log.info('config file content:' + tmpStr + ' len:' + str(len(tmpStr)))
		jobj = json.loads(tmpStr)
		if(JTAG_TASKTYPE_ALL in jobj.keys()) and (JTAG_TASKTYPE_LIGHT in jobj.keys()) and (JTAG_TASKTYPE_DATAFACTORY in jobj.keys()):
			rtnStr = tmpStr
		file.close()
	except IOError :
		log.info("config file error!!!")
	except json.decoder.JSONDecodeError:
		log.info("config file does not contain json data!!!")
	except:
		log.info("getSerConfigsStr other exception!!!")
	return rtnStr

#get SER_IPS and SER_ANGLES from configfiles json item
def getSerIpsAndSerAngles(jobj):
	mSerIps = []
	mSerAngles = []
	try:
		if(JTAG_SERIPS in jobj.keys()):
			mSerIps  = jobj[JTAG_SERIPS]
		if(JTAG_SERANGLES in jobj.keys()):
			mSerAngles  = jobj[JTAG_SERANGLES]
	except IOError :
		log.info("config file error!!!")
	except json.decoder.JSONDecodeError:
		log.info("config file does not contain json data!!!")
	#log.info("getSerIpsAndSerAngles -- mSerIps:" + str(mSerIps) + " mSerAngles:" + str(mSerAngles))
	return mSerIps, mSerAngles

#get configs from request content json string
#then set to config files 
def setConfigsFromJContent(jContent):
	result = 0
	try:
		jobj = json.loads(jContent)
		while True:
			#check 'all'
			if(JTAG_TASKTYPE_ALL in jobj.keys() and isinstance(jobj[JTAG_TASKTYPE_ALL], list)):
				aryAll = jobj[JTAG_TASKTYPE_ALL]
				aryAllLen = len(aryAll)
				#允许置空吧
				# if aryAllLen <= 0:
				# 	log.info("config json data 'all' ary len < 0 error!!!")
				# 	result = -1
				# 	break
				for tmpObj in aryAll:
					result = checkConfigSerAllItem(tmpObj)
					if result < 0:
						result = -1
						break
				if result < 0:
					break
			else:
				log.info("config json data 'all' not find or not list error!!!")
				result = -1
				break

			#check 'light'
			if(JTAG_TASKTYPE_LIGHT in jobj.keys() and isinstance(jobj[JTAG_TASKTYPE_LIGHT], list)):
				aryLight = jobj[JTAG_TASKTYPE_LIGHT]
				aryLightLen = len(aryLight)
				#允许置空吧
				# if aryLightLen <= 0:
				# 	log.info("config json data 'light' ary len < 0 error!!!")
				# 	result = -1
				# 	break
				for tmpObj in aryLight:
					if isinstance(tmpObj, str):
						result = checkConfigIp(tmpObj)
						if result < 0:
							result = -1
							break
					else:
						log.info("config json data 'light' 's IP  is not str error!!!")
						result = -1
						break
				if result < 0:
					break
			else:
				log.info("config json data 'light' not find or not list error!!!")
				result = -1
				break
			#check 'datafactory'
			if(JTAG_TASKTYPE_DATAFACTORY in jobj.keys() and isinstance(jobj[JTAG_TASKTYPE_DATAFACTORY], list)):
				aryDatafactory = jobj[JTAG_TASKTYPE_DATAFACTORY]
				aryDatafactoryLen = len(aryDatafactory)
				#允许置空吧
				# if aryLightLen <= 0:
				# 	log.info("config json data 'light' ary len < 0 error!!!")
				# 	result = -1
				# 	break
				for tmpObj in aryDatafactory:
					if isinstance(tmpObj, str):
						result = checkConfigIp(tmpObj)
						if result < 0:
							result = -1
							break
					else:
						log.info("config json data 'datafactory' 's IP  is not str error!!!")
						result = -1
						break
				if result < 0:
					break
			else:
				log.info("config json data 'datafactory' not find or not list error!!!")
				result = -1
				break
			break
		if result >= 0:
			file = open(FILE_CFG_PATH, "w")
			file.write(jContent)
			file.close()
		else:
			log.info("config json data ok but write file error!!!")
			result = -1
	except json.decoder.JSONDecodeError:
		result = -1
		log.info("config json data error!!!")
	except:
		result = -1
		log.info("config json other error!!!")
	log.info("setConfigsFromJContent -- result:" + str(result))
	return result

#检查配置文件， all里面的其中一个item里面的SER_IPS 和 SER_ANGLES
def checkConfigSerAllItem(jobj):
	result = -1
	while True:
		if(JTAG_SERIPS in jobj.keys()):
			mSerIps  = jobj[JTAG_SERIPS]
			mSerIps , result = checkConfigSerIps(mSerIps)
			if result < 0:
				break
		else:
			log.info("config json data mSerIps not find error!!!")
			result = -1
			break
		if(JTAG_SERANGLES in jobj.keys()):
			mSerAngles  = jobj[JTAG_SERANGLES]
			mSerAngles, result = checkConfigSerAngles(mSerAngles)
			if result < 0:
				break
		else:
			log.info("config json data mSerAngles not find error!!!")
			result = -1
			break
		#check length is the same 
		cntIps = len(mSerIps)
		cntAngles = len(mSerAngles)
		if cntAngles != cntIps:
			log.info("config json data cntAngles != cntIps error!!!")
			result = -1
		break
	return result

#检查IP地址 正规性
def checkConfigIp(ip):
	result = 0
	regex = re.compile(
			r'^(?:http|ftp)s?://' # http:// or https://
			r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
			r'localhost|' #localhost...
			r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
			r'(?::\d+)?' # optional port
			r'(?:/?|[/?]\S+)$', re.IGNORECASE)
	ret = regex.match(ip)
	if ret == None:
		result = -1
		log.info("is not right ip regex error!!!")
	return result

def checkConfigSerIps(mSerIps):
	result = 0
	# not list
	if not isinstance(mSerIps, list):
		log.info("mSerIps is not list error!!!")
		result = -1
	else:
		regex = re.compile(
			r'^(?:http|ftp)s?://' # http:// or https://
			r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|' #domain...
			r'localhost|' #localhost...
			r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})' # ...or ip
			r'(?::\d+)?' # optional port
			r'(?:/?|[/?]\S+)$', re.IGNORECASE)
		#check each ip
		for tmp in mSerIps:
			if not isinstance(tmp, str):
				#not string
				result = -1
				log.info("mSerIps' child  is not string error!!!")
				break
			else:
				#check ip regex
				ret = regex.match(tmp)
				if ret == None:
					result = -1
					log.info("mSerIps' child  is not right ip regex error!!!")
					break
		#check have the same ip addr
		index = 0
		for item1 in mSerIps:
			curIndex = 0
			for item2 in mSerIps:
				#log.info("item1:" + str(item1) + " item2:" + str(item2) + " curIndex:" + str(curIndex) + " index:" + str(index))
				if curIndex > index:
					if item1 == item2:
						log.info("mSerIps's child has same itme error!!!")
						result = -1
						break
				curIndex += 1
			index += 1
	return mSerIps, result

#检查 all 里面 angles数组里面的内容
def checkConfigSerAngles(mSerAngles):
	result = 0
	if not isinstance(mSerAngles, list):
		log.info("mSerAngles is not list error!!!")
		result = -1
	else:
		cntAngles = len(mSerAngles)
		for tmp in mSerAngles:
			rtnAngle, rtn = checkAngle(tmp)
			if rtn < 0:
				result = -1
				break

	return mSerAngles, result

def checkHasServerBusy():
	#log.info("checkHasServerBusy()")
	result = 0

	jConfigStr = getSerConfigsStr()
	jConfig = json.loads(jConfigStr)

	jConfigAll = jConfig[JTAG_TASKTYPE_ALL]
	jConfigAllLen = len(jConfigAll)

	#计数每个status文件
	mIndex = 0
	#遍历 all 群
	for jobj in jConfigAll:
		tName, tTaskType ,tState, tTaskId, tRatio, tPostfix, tStateStr = getCheckStateFromFile(mIndex)
		if tState != JTAG_STATE_DONE and tState != "" and tState != JTAG_STATE_ERROR:
			result = 1
			return result
		mIndex += 1

	jConfigLight = jConfig[JTAG_TASKTYPE_LIGHT]
	jConfigLightLen = len(jConfigLight)
	#遍历 light 群
	for ipStr in jConfigLight:
		tName, tTaskType ,tState, tTaskId, tRatio, tPostfix, tStateStr = getCheckStateFromFile(mIndex)
		if tState != JTAG_STATE_DONE and tState != "" and tState != JTAG_STATE_ERROR:
			result = 1
			return result
		mIndex += 1
	
	jConfigDatafactory = jConfig[JTAG_TASKTYPE_DATAFACTORY]
	jConfigDatafactoryLen = len(jConfigDatafactory)
	#遍历 datafactory 群
	for ipStr in jConfigDatafactory:
		tName, tTaskType ,tState, tTaskId, tRatio, tPostfix, tStateStr = getCheckStateFromFile(mIndex)
		if tState != JTAG_STATE_DONE and tState != "" and tState != JTAG_STATE_ERROR:
			result = 1
			return result
		mIndex += 1
	
	return result
	
#最多记录多少条历史记录
HISTORY_LENGTH_MAX = 10

#记录历史记录
ARY_HISTORY_REQ_PRO = []

def get_time_stamp():
    ct = time.time()
    local_time = time.localtime(ct)
    data_head = time.strftime("%Y%m%d%H%M%S", local_time)
    data_secs = (ct - int(ct)) * 1000
    time_stamp = "%s%03d" % (data_head, data_secs)
    return time_stamp

#记录req pro的记录
def writeHistoryReqPro(content):
	strTime = get_time_stamp()
	strHistory = "{"
	strHistory += "\"time\":\"" + strTime + "\","
	strHistory += "\"" + JTAG_PARAMS + "\":" + content
	strHistory += "}"
	#log.info("writeHistoryReqPro() --- " + strHistory)
	if len(ARY_HISTORY_REQ_PRO) >= HISTORY_LENGTH_MAX:
		ARY_HISTORY_REQ_PRO.pop(0)
	ARY_HISTORY_REQ_PRO.append(strHistory)
	#log.info("writeHistoryReqPro() --- " + str(len(ARY_HISTORY_REQ_PRO)) + " " + str(ARY_HISTORY_REQ_PRO))

#读取req pro的记录
def readHistoryReqPro():
	result = "["
	lenHistory = len(ARY_HISTORY_REQ_PRO)
	index = lenHistory - 1
	while index >= 0:
		result += ARY_HISTORY_REQ_PRO[index]
		if index > 0:
			result += ","
		index -= 1
	result += "]"
	#log.info("readHistoryReqPro() --- " + result)
	return result


############################################################################
# Fix model part
############################################################################

#get FixModel infos from request content json string
def getFixModelInfosFromJContent(jContent):
	mName = ""
	mTaskId = ""
	result = 0
	while(1):
		try:
			jobj = json.loads(jContent)
			#check name
			if(JTAG_NAME in jobj.keys()):
				mName  = jobj[JTAG_NAME]
				mName, result = checkName(mName)
				if result < 0:
					break
			else:
				log.info("content json data name not find error!!!")
				result = -1
				break
			#check taskId
			if(JTAG_TASKID in jobj.keys()):
				mTaskId  = jobj[JTAG_TASKID]
				mTaskId, result = checkTaskId(mTaskId)
				if result < 0:
					break
			else:
				log.info("content json data taskid not find error!!!")
				result = -1
				break
			#check end break while
			break
		except json.decoder.JSONDecodeError:
			result = -1
			log.info("conntent json data error!!!")
			break
	log.info("getFixModelInfosFromJContent -- name:" + str(mName) + " taskId:" + str(mTaskId) + " result:" + str(result))
	return mName, mTaskId, result