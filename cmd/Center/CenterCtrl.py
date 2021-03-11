#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding:utf-8
import socket, sys, os, json
import uuid, random, re, time, traceback, threading
import urllib.request
from light import *
import smtplib
from email.mime.text import MIMEText
from email.header import Header

DIR_PATH = os.path.abspath(os.path.join(sys.argv[0], "..")) + "/SerFiles"
FILE_PATH = DIR_PATH + "/CenterStatus.txt"
FILE_PARAM_PATH = DIR_PATH + "/CenterParams.txt"
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
URL_PATH_SYNCMODEL = "/syncmodel"
URL_PATH_DOWNLOADMODEL = "/downloadmodel"
JTAG_NAME  = "name"
JTAG_TASKTYPE = "taskType"
JTAG_TASKTYPE_ALL = "all"
JTAG_TASKTYPE_LIGHT = "light"
JTAG_TASKTYPE_DATAFACTORY = "datafactory"
JTAG_TASKTYPE_FIXMODEL = "fixmodel"
JTAG_TASKTYPE_MODELPREVIEW = "modelPreview"
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
JTAG_VIDEO = "video"
JTAG_SERIPS  = "SER_IPS"
JTAG_SERANGLES = "SER_ANGLES"
JTAG_SIMPLEMODEL = "simpleModel"
JTAG_PROGRESS = "progress"
JTAG_VERSION = "version"
JTAG_PARAMS1 = "params1"
JTAG_MSG   = "msg"
JTAG_MSG_BUSY = "isBusy"
JTAG_MSG_BYE  = "byebye"
JTAG_MSG_UNKNOWN  = "unknown"
JTAG_MSG_PARAMSERR = "params error"
JTAG_MSG_SERVERERR = "server error"
JTAG_MSG_OVERTMERR = "overtime error"
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

class CenterCtrl:

    gRootPath = os.path.abspath(os.path.join(sys.argv[0], ".."))

    def checkAndCreateDir(self, path):
        isExists = os.path.exists(path)
        if not isExists:
            os.makedirs(path) 
            self.log.info(path + ' 创建成功')
        else:
            self.log.info(path + ' 目录已存在')

    ##############################################################
    #status start
    ##############################################################

    #status array
    #每秒钟check的所有功能机群组的状态 都会按index来存储，存储可以导出jsonobj的字符串
    #这样就不需要CenterStatus.txt_0/1/2... 这些文件了
    ARY_STATUS = []
    STATUS_MAX_LENGTH = 50

    def initAryStatus(self):
        index = 0
        while index < self.STATUS_MAX_LENGTH:
            self.ARY_STATUS.append("")
            index += 1
    
    #从statusAry 获取 某个机组的状态
    def getStatusStrFromStatusAry(self, index):
        return self.ARY_STATUS[index]

    #设置statusAry 某个机组的状态
    def setStausStrToStatusAry(self, index, strStatus):
        self.ARY_STATUS[index] = strStatus

    #get now server state file info-state info-name and paramsAry of each server
    def getCheckStateFromFile(self, index):
        #self.log.info("getCheckStateFromFile() index:" + str(index))
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
        mVideo = ""
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
        mStateStr += "\"" + JTAG_VIDEO + "\":\"" + JTAG_STATE_NONE + "\","
        mStateStr += "\"" + JTAG_PARAMS + "\":[]"
        mStateStr += "}"
        #tmp
        tName  = ""
        tState = ""
        try:
            tmpStr = self.getStatusStrFromStatusAry(index)
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
                if(JTAG_VIDEO in tmpObj.keys()):
                    #MARK "simpleModel":{"name":"xxx", "simpleModel":"done"}
                    tVideoObj = tmpObj[JTAG_VIDEO]
                    if tVideoObj != None and (JTAG_VIDEO in tVideoObj.keys()):
                        mVideo = tVideoObj[JTAG_VIDEO]
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
                #self.log.info("all done~~~")
                mState = JTAG_STATE_DONE
            elif countEmpty == cntAryState:
                #self.log.info("all empty~~~")
                mState = ""
            elif (countDone + countEmpty) == cntAryState:				
                #self.log.info("all finished, empty and done~~~")
                mState = ""
            elif countDone + countEmpty + countError == cntAryState:
                #self.log.info("all finished, but have errors!!!!!!")
                mState = JTAG_STATE_ERROR
            else:
                #self.log.info("inprogressing~~~")
                mState = JTAG_STATE_INPROGRESS

            #求progress平均数
            lenProgressAry =  len(mProgressAry)
            if lenProgressAry <= 0:
                self.log.info("len progressAry <= 0 get average progress error!!!")
            else:
                sumProgress = 0
                for progress in mProgressAry:
                    sumProgress += progress
                mProgress = round(sumProgress / lenProgressAry)
            # self.log.info("------------> progressary:" + str(mProgressAry))

            #self.log.info("aryName:" + str(aryName) + " aryState:" + str(aryState) + " name:" + mName + " taskType:" + mTaskType + " state:" + mState + " countDone:" + str(countDone) + " countEmpty:" + str(countEmpty) + " countError:" + str(countError))
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
            mStateStr += "\"" + JTAG_VIDEO + "\":\"" + mVideo + "\","
            mStateStr += "\"" + JTAG_PARAMS + "\":" + tmpStr
            mStateStr += "}"
        except :
            self.log.info("getCheckStateFromFile() error!!!")
            self.log.info(traceback.format_exc())
        return mName, mTaskType ,mState, mTaskId, mRatio, mPostfix, mStateStr

    ##############################################################
    #status end
    ##############################################################

    ##############################################################
    #/pro start
    ##############################################################

    gIsHandlingPro = 0

    def handleRecv_pro(self, path, contentData):
        if self.gIsHandlingPro == 1 or self.gIsConfiging == 1:
            self.log.info("req pro but isHandlingPro return isBusy gIsHandlingPro:" + str(self.gIsHandlingPro) + " gIsConfiging:" + str(self.gIsConfiging) +  " error!!!")
            response_body = "{\"" + JTAG_NAME + "\":\""+ path + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_BUSY + "\"}"
        else:
            self.gIsHandlingPro = 1
            mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, mTaskId, mRatio, mPostfix, mParams1, result = self.getInfosFromJContent(contentData)
            #params error
            if result != 0:
                response_body = "{\"" + JTAG_NAME + "\":\""+ str(mName) + "\",\"" + JTAG_TASKTYPE + "\":\"" + mTaskType + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_PARAMSERR + "\"}"
                self.gIsHandlingPro = 0
            else:
                response_body = self.handle_SendReqToServers(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, mTaskId, mRatio, mPostfix, mParams1)
                if response_body.find(JTAG_STATE_ERROR) >= 0:
                    #包含错误的话，直接返回吧
                    self.gIsHandlingPro = 0
                else:
                    #直接更新状态再返回吧
                    time.sleep(0.5)
                    self.checkState()
                    self.gIsHandlingPro = 0
                    self.writeHistoryReqPro(contentData)
        return response_body

    #find non-busy servers and send req
    def handle_SendReqToServers(self, mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, mTaskId, mRatio, mPostfix, mParams1):

        self.log.info("handle_SendReqToServers()")

        rtnMsg = "{\"" + JTAG_NAME + "\":\"" + mName + "\", \"" + JTAG_TASKTYPE + "\":\"" + mTaskType + "\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_BUSY + "\"}"

        jConfigStr = self.getSerConfigsStr()
        jConfig = json.loads(jConfigStr)

        jConfigAll = jConfig[JTAG_TASKTYPE_ALL]
        jConfigAllLen = len(jConfigAll)
        jConfigLight = jConfig[JTAG_TASKTYPE_LIGHT]
        jConfigLightLen = len(jConfigLight)
        jConfigDatafactory = jConfig[JTAG_TASKTYPE_DATAFACTORY]
        jConfigDatafactoryLen = len(jConfigDatafactory)

        mIndex = 0
        if mTaskType == JTAG_TASKTYPE_ALL:
            hasServerErr = 0
            #遍历 all 群
            for jobj in jConfigAll:
                tName, tTaskType ,tState, tTaskId, tRatio, tPostfix, tStateStr = self.getCheckStateFromFile(mIndex)
                if tState == JTAG_STATE_DONE or tState == "":
                    #done状态或者初始化状态就可以开始任务
                    self.log.info("handle_SendReqToServers() find 'all' machine is ok index:" + str(mIndex))
                    mSerIps, mSerAngles = self.getSerIpsAndSerAngles(jobj)
                    return self.handle_SendReqToServers_all(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, mSerIps, mSerAngles, mTaskId, mRatio, mPostfix, mParams1)
                elif tState == JTAG_STATE_ERROR:
                    #错误状态的，server error 不能执行； 不是server error的可以执行（这些是有流程操作错误，最终还是完成了）
                    if tStateStr.find(JTAG_MSG_SERVERERR) >= 0:
                        #server err, 跳过吧
                        mIndex += 1
                        hasServerErr = 1
                        continue
                    else:
                        self.log.info("handle_SendReqToServers() find 'all' machine is error, but is ok index:" + str(mIndex))
                        mSerIps, mSerAngles = self.getSerIpsAndSerAngles(jobj)
                        return self.handle_SendReqToServers_all(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, mSerIps, mSerAngles, mTaskId, mRatio, mPostfix, mParams1)
                else:
                    mIndex += 1
                    continue
                
            #如果运行到最后，没机器运行任务，且发现有机器server error了就返回server error
            #同理没有配置到机器的也报error吧
            if hasServerErr == 1 or jConfigAllLen <= 0:
                if hasServerErr == 1:
                    self.log.info("发现all机群有server error!!!!")
                if jConfigAllLen <= 0:
                    self.log.info("发现all机群没有配置 server error!!!!")
                rtnMsg = "{\"" + JTAG_NAME + "\":\"" + mName + "\", \"" + JTAG_TASKTYPE + "\":\"" + mTaskType + "\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_SERVERERR + "\"}"
            #如果遍历到最后了也没有机器可以运行这次任务，就返回默认的结果 isBusy
            return rtnMsg

        elif mTaskType == JTAG_TASKTYPE_LIGHT:
            hasServerErr = 0
            #要加上all的数量
            mIndex = jConfigAllLen
            #遍历 light 群
            for ipStr in jConfigLight:
                tName, tTaskType, tState, tTaskId, tRatio, tPostfix, tStateStr = self.getCheckStateFromFile(mIndex)
                if tState == JTAG_STATE_DONE or tState == "":
                    #done状态或者初始化状态就可以开始任务
                    self.log.info("handle_SendReqToServers() find 'light' machine is ok index:" + str(mIndex))
                    return self.handle_SendReqToServers_light(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, ipStr, mTaskId, mRatio, mPostfix, mParams1)
                elif tState == JTAG_STATE_ERROR:
                    #错误状态的，server error 不能执行； 不是server error的可以执行（这些是有流程操作错误，最终还是完成了）
                    if tStateStr.find(JTAG_MSG_SERVERERR) >= 0:
                        #server err, 跳过吧
                        mIndex += 1
                        hasServerErr = 1
                        continue
                    else:
                        self.log.info("handle_SendReqToServers() find 'light' machine is error, but is ok index:" + str(mIndex))
                        return self.handle_SendReqToServers_light(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, ipStr, mTaskId, mRatio, mPostfix, mParams1)
                else:
                    mIndex += 1
                    continue

            #如果运行到最后，没机器运行任务，且发现有机器server error了就返回server error
            #同理没有配置到机器的也报error吧
            if hasServerErr == 1 or jConfigLightLen <= 0:
                if hasServerErr == 1:
                    self.log.info("发现light机群有server error!!!!")
                if jConfigLightLen <= 0:
                    self.log.info("发现light机群没有配置 server error!!!!")
                rtnMsg = "{\"" + JTAG_NAME + "\":\"" + mName + "\", \"" + JTAG_TASKTYPE + "\":\"" + mTaskType + "\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_SERVERERR + "\"}"
            #如果遍历到最后了也没有机器可以运行这次任务，就返回默认的结果 isBusy
            return rtnMsg

        elif mTaskType == JTAG_TASKTYPE_DATAFACTORY:
            hasServerErr = 0
            #要加上all + light的数量
            mIndex = jConfigAllLen + jConfigLightLen
            #遍历 datafactory 群
            for ipStr in jConfigDatafactory:
                tName, tTaskType, tState, tTaskId, tRatio, tPostfix, tStateStr = self.getCheckStateFromFile(mIndex)
                if tState == JTAG_STATE_DONE or tState == "":
                    #done状态或者初始化状态就可以开始任务
                    self.log.info("handle_SendReqToServers() find 'datafactory' machine is ok index:" + str(mIndex))
                    return self.handle_SendReqToServers_datafactory(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, ipStr, mTaskId, mRatio, mPostfix, mParams1)
                elif tState == JTAG_STATE_ERROR:
                    #错误状态的，server error 不能执行； 不是server error的可以执行（这些是有流程操作错误，最终还是完成了）
                    if tStateStr.find(JTAG_MSG_SERVERERR) >= 0:
                        #server err, 跳过吧
                        mIndex += 1
                        hasServerErr = 1
                        continue
                    else:
                        self.log.info("handle_SendReqToServers() find 'datafactory' machine is error, but is ok index:" + str(mIndex))
                        return self.handle_SendReqToServers_datafactory(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, ipStr, mTaskId, mRatio, mPostfix, mParams1)
                else:
                    mIndex += 1
                    continue
            #如果运行到最后，没机器运行任务，且发现有机器server error了就返回server error
            #同理没有配置到机器的也报error吧
            if hasServerErr == 1 or jConfigDatafactoryLen <= 0:
                if hasServerErr == 1:
                    self.log.info("发现datafactory机群有server error!!!!")
                if jConfigDatafactoryLen <= 0:
                    self.log.info("发现datafactory机群没有配置 server error!!!!")
                rtnMsg = "{\"" + JTAG_NAME + "\":\"" + mName + "\", \"" + JTAG_TASKTYPE + "\":\"" + mTaskType + "\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_SERVERERR + "\"}"
            #如果遍历到最后了也没有机器可以运行这次任务，就返回默认的结果 isBusy
            return rtnMsg
        
        elif mTaskType == JTAG_TASKTYPE_MODELPREVIEW:
            hasServerErr = 0
            #用light机器来执行
            #要加上all的数量
            mIndex = jConfigAllLen
            #遍历 light 群
            for ipStr in jConfigLight:
                tName, tTaskType, tState, tTaskId, tRatio, tPostfix, tStateStr = self.getCheckStateFromFile(mIndex)
                if tState == JTAG_STATE_DONE or tState == "":
                    #done状态或者初始化状态就可以开始任务
                    self.log.info("handle_SendReqToServers() find 'light' machine is ok index:" + str(mIndex))
                    return self.handle_SendReqToServers_light(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, ipStr, mTaskId, mRatio, mPostfix, mParams1)
                elif tState == JTAG_STATE_ERROR:
                    #错误状态的，server error 不能执行； 不是server error的可以执行（这些是有流程操作错误，最终还是完成了）
                    if tStateStr.find(JTAG_MSG_SERVERERR) >= 0:
                        #server err, 跳过吧
                        mIndex += 1
                        hasServerErr = 1
                        continue
                    else:
                        self.log.info("handle_SendReqToServers() find 'light' machine is error, but is ok index:" + str(mIndex))
                        return self.handle_SendReqToServers_light(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, ipStr, mTaskId, mRatio, mPostfix, mParams1)
                else:
                    mIndex += 1
                    continue
            #如果运行到最后，没机器运行任务，且发现有机器server error了就返回server error
            #同理没有配置到机器的也报error吧
            if hasServerErr == 1 or jConfigLightLen <= 0:
                if hasServerErr == 1:
                    self.log.info("发现light机群有server error!!!!")
                if jConfigLightLen <= 0:
                    self.log.info("发现light机群没有配置 server error!!!!")
                rtnMsg = "{\"" + JTAG_NAME + "\":\"" + mName + "\", \"" + JTAG_TASKTYPE + "\":\"" + mTaskType + "\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_SERVERERR + "\"}"
            #如果遍历到最后了也没有机器可以运行这次任务，就返回默认的结果 isBusy
            return rtnMsg

    #send 'all' request to servers one by one
    def handle_SendReqToServers_all(self, mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, mSerIps, mSerAngles, mTaskId, mRatio, mPostfix, mParams1):
        cntServs = len(mSerIps)
        mIndex = -1
        rtnMsg = "{\"" + JTAG_NAME + "\":\"" + mName + "\", \"" + JTAG_TASKTYPE + "\":\"" + mTaskType + "\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_SERVERERR + "\"}"
        if cntServs <= 0:
            self.log.info("handle_SendReqToServers_all() SendReqSer Error servers cnt <=0 !!!!!")
        else:
            for ipStr in mSerIps:
                try:
                    mIndex += 1
                    #self.log.info("handle_SendReqToServers_all()[" + str(mIndex) + "]:" + "ip:" + ipStr + " position:" + str(mSerAngles[mIndex]))
                    mAngle = mSerAngles[mIndex]
                    dataStr = self.getJStrWithParams(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, mTaskId, mRatio, mPostfix, mParams1)
                    dataStrBytes = dataStr.encode('utf-8')
                    self.log.info("handle_SendReqToServers_all()-- ip:" + str(ipStr) + " dataStr:" + str(dataStr))
                    url = ipStr + URL_PATH_PRO
                    f = urllib.request.urlopen(url, dataStrBytes, timeout=30)
                    rtnMsg = f.read().decode('utf-8')
                    self.log.info("handle_SendReqToServers_all()-- ip:" + str(ipStr) + " dataStr:" + str(dataStr) + " rtn:" + str(rtnMsg))
                    f.close()
                    if rtnMsg.find(JTAG_STATE_ERROR) >= 0:
                        self.log.info("handle_SendReqToServers_all()[" + str(mIndex) + "]:" + "ip:" + str(ipStr) + "[" + str(rtnMsg) + "] find rtn error!!!!")
                        break
                    time.sleep(0.1)
                except Exception:	
                    self.log.info("handle_SendReqToServers_all()[" + str(mIndex) + "]:" + "ip:" + str(ipStr) + " request error!!!!")
                    self.log.info(traceback.format_exc())
                    break
        return rtnMsg

    #send 'light' request to server
    def handle_SendReqToServers_light(self, mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, ipStr, mTaskId, mRatio, mPostfix, mParams1):
        rtnMsg = "{\"" + JTAG_NAME + "\":\"" + mName + "\", \"" + JTAG_TASKTYPE + "\":\"" + mTaskType + "\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_SERVERERR + "\"}"
        try:
            #log.info("handle_SendReqToServers_light() ip:" + ipStr)
            dataStr = self.getJStrWithParams(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, mTaskId, mRatio, mPostfix, mParams1)
            dataStrBytes = dataStr.encode('utf-8')
            self.log.info("handle_SendReqToServers_light()-- ip:" + str(ipStr) + " dataStr:" + str(dataStr))
            url = ipStr + URL_PATH_PRO
            f = urllib.request.urlopen(url, dataStrBytes, timeout=30)
            rtnMsg = f.read().decode('utf-8')
            self.log.info("handle_SendReqToServers_light()-- ip:" + str(ipStr) + " dataStr:" + str(dataStr) + " rtn:" + str(rtnMsg))
            f.close()
            if rtnMsg.find(JTAG_STATE_ERROR) >= 0:
                self.log.info("handle_SendReqToServers_light():" + "ip:" + str(ipStr) + "[" + str(rtnMsg) + "] find rtn error!!!!")
                
        except Exception:
            self.log.info("handle_SendReqToServers_light():" + "ip:" + str(ipStr) + " request error!!!!")
            self.log.info(traceback.format_exc())
                    
        return rtnMsg

    #send 'datafactory' request to server
    def handle_SendReqToServers_datafactory(self, mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, ipStr, mTaskId, mRatio, mPostfix, mParams1):
        rtnMsg = "{\"" + JTAG_NAME + "\":\"" + mName + "\", \"" + JTAG_TASKTYPE + "\":\"" + mTaskType + "\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_SERVERERR + "\"}"
        try:
            #log.info("handle_SendReqToServers_light() ip:" + ipStr)
            dataStr = self.getJStrWithParams(mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, mTaskId, mRatio, mPostfix, mParams1)
            dataStrBytes = dataStr.encode('utf-8')
            self.log.info("handle_SendReqToServers_datafactory()-- ip:" + str(ipStr) + " dataStr:" + str(dataStr))
            url = ipStr + URL_PATH_PRO
            f = urllib.request.urlopen(url, dataStrBytes, timeout=30)
            rtnMsg = f.read().decode('utf-8')
            self.log.info("handle_SendReqToServers_datafactory()-- ip:" + str(ipStr) + " dataStr:" + str(dataStr) + " rtn:" + str(rtnMsg))
            f.close()
            if rtnMsg.find(JTAG_STATE_ERROR) >= 0:
                self.log.info("handle_SendReqToServers_datafactory():" + "ip:" + str(ipStr) + "[" + str(rtnMsg) + "] find rtn error!!!!")
                
        except Exception:
            self.log.info("handle_SendReqToServers_datafactory():" + "ip:" + str(ipStr) + " request error!!!!")
                    
        return rtnMsg

    #get infos from request content json string
    def getInfosFromJContent(self, jContent):
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
        mParams1 = ""
        result = 0
        while(1):
            try:
                jobj = json.loads(jContent)
                #check name
                if(JTAG_NAME in jobj.keys()):
                    mName  = jobj[JTAG_NAME]
                    mName, result = self.checkName(mName)
                    if result < 0:
                        break
                else:
                    self.log.info("content json data name not find error!!!")
                    result = -1
                    break
                #check tasktype
                if(JTAG_TASKTYPE in jobj.keys()):
                    mTaskType = jobj[JTAG_TASKTYPE]
                    mTaskType, result = self.checkTaskType(mTaskType)
                    if result < 0:
                        break
                else:
                    self.log.info("content json data resolution not find error!!!")
                    result = -1
                    break

                #if taskType == light
                #check taskId and Ratio
                if mTaskType == JTAG_TASKTYPE_LIGHT:
                    #check taskId
                    if (JTAG_TASKID in jobj.keys()):
                        mTaskId = jobj[JTAG_TASKID]
                        mTaskId, result = self.checkTaskId(mTaskId)
                        if result < 0:
                            break
                    else:
                        self.log.info("content json data taskId not find error!!!")
                        result = -1
                        break
                    #check ratio
                    if (JTAG_RATIO in jobj.keys()):
                        mRatio = jobj[JTAG_RATIO]
                        mRatio, result = self.checkRatio(mRatio)
                        if result < 0:
                            break
                    else:
                        self.log.info("content json data ratio not find error!!!")
                        result = -1
                        break
                
                #if taskType == datafactory
                # taskId,postfix必须有
                if mTaskType == JTAG_TASKTYPE_DATAFACTORY:
                    #check taskId
                    if (JTAG_TASKID in jobj.keys()):
                        mTaskId = jobj[JTAG_TASKID]
                        mTaskId, result = self.checkTaskId(mTaskId)
                        if result < 0:
                            break
                    else:
                        self.log.info("content json data taskId not find error!!!")
                        result = -1
                        break
                    #check postfix
                    if (JTAG_POSTFIX in jobj.keys()):
                        mPostfix = jobj[JTAG_POSTFIX]
                        mPostfix, result = self.checkPostfix(mPostfix)
                        if result < 0:
                            break
                    else:
                        self.log.info("content json data postfix not find error!!!")
                        result = -1
                        break
                
                if mTaskType == JTAG_TASKTYPE_MODELPREVIEW:
                    #check taskId
                    if (JTAG_TASKID in jobj.keys()):
                        mTaskId = jobj[JTAG_TASKID]
                        mTaskId, result = self.checkTaskId(mTaskId)
                        if result < 0:
                            break
                    else:
                        self.log.info("content json data taskId not find error!!!")
                        result = -1
                        break

                    #check params1
                    if (JTAG_PARAMS1 in jobj.keys()):
                        mParams1 = jobj[JTAG_PARAMS1]
                        mParams1, result = self.checkParams1(mParams1)
                        if result < 0:
                            break
                    else:
                        self.log.info("content json data mParams1 not find error!!!")
                        result = -1
                        break

                if mTaskType != JTAG_TASKTYPE_DATAFACTORY and mTaskType != JTAG_TASKTYPE_MODELPREVIEW:
                    #check map
                    if(JTAG_MAP in jobj.keys()):
                        mMap  = jobj[JTAG_MAP]
                        mMap, result = self.checkMap(mMap)
                        if result < 0:
                            break
                    else:
                        self.log.info("content json data map not find error!!!")
                        result = -1
                        break
                    #check quality
                    if(JTAG_QUALITY in jobj.keys()):
                        mQuality  = jobj[JTAG_QUALITY]
                        mQuality, result = self.checkQuality(mQuality)
                        if result < 0:
                            break
                    #check ids
                    if(JTAG_IDS in jobj.keys()):
                        mIds = jobj[JTAG_IDS]
                        mIds, result = self.checkIds(mIds)
                        if result < 0:
                            break
                    else:
                        self.log.info("content json data position not find error!!!")
                        result = -1
                        break
                    #check angle
                    if(JTAG_ANGLE in jobj.keys()):
                        mAngle  = jobj[JTAG_ANGLE]
                        mAngle, result = self.checkAngle(mAngle)
                        if result < 0:
                            break
                    #check resolution
                    if(JTAG_RESOLUTION in jobj.keys()):
                        mResolution  = jobj[JTAG_RESOLUTION]
                        mResolution, result = self.checkResolution(mResolution)
                        if result < 0:
                            break
                    else:
                        self.log.info("content json data resolution not find error!!!")
                        result = -1
                        break
                #check end break while
                break
            except json.decoder.JSONDecodeError:
                result = -1
                self.log.info("conntent json data error!!!")
                break
        self.log.info("getInfosFromJContent -- name:" + str(mName) + " map:" + str(mMap) + " angle:" + str(mAngle) + " ids:" + str(mIds) + " resolution:" + str(mResolution) + " quality:" + str(mQuality) + " taskType:" + str(mTaskType) + " taskId:" + str(mTaskId) + " ratio:" + str(mRatio) + " postfix:" + str(mPostfix) + " params1:" + str(mParams1) + " result:" + str(result))
        return mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, mTaskId, mRatio, mPostfix, mParams1, result

    #get jsonstr with all params
    def getJStrWithParams(self, mName, mTaskType, mMap, mAngle, mIds, mResolution, mQuality, mTaskId, mRatio, mPostfix, mParams1):
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
        rtnStr += "\"" + JTAG_POSTFIX + "\":\"" + mPostfix + "\","
        if isinstance(mParams1, str):
            rtnStr += "\"" + JTAG_PARAMS1 + "\":\"" + str(mParams1) + "\""
        else:
            #判断是不是obj
            try:
                mParams1 = str(mParams1)
                mParams1 = mParams1.replace("'", "\"")
                jobj = json.loads(mParams1)
                rtnStr += "\"" + JTAG_PARAMS1 + "\":" + mParams1
            except:
                self.log.info("getJStrWithParams() --- mParams1 不是字符串也不是 json, 直接往后加了!!!")
                rtnStr += "\"" + JTAG_PARAMS1 + "\":" + mParams1
        rtnStr += "}"
        return rtnStr

    def get_time_stamp(self):
        ct = time.time()
        local_time = time.localtime(ct)
        data_head = time.strftime("%Y%m%d%H%M%S", local_time)
        data_secs = (ct - int(ct)) * 1000
        time_stamp = "%s%03d" % (data_head, data_secs)
        return time_stamp

    def checkAngle(self, angle):
        result = -1
        if not isinstance(angle, list):
            self.log.info("angle is not list error!!!")
            result = -1
        elif len(angle) <= 0:
            self.log.info("angle length <= 0 error!!!")
            result = -1
        else:
            for tmp in angle:
                if not isinstance(tmp, int) or tmp < 0 or tmp > 5:
                    result = -1
                    self.log.info("angle's child is not int or < 0 or > 5 error!!!")
                    return angle, result
            #check have the same number
            index = 0
            for num1 in angle:
                curIndex = 0
                for num2 in angle:
                    #self.log.info("num1:" + str(num1) + " num2:" + str(num2) + " curIndex:" + str(curIndex) + " index:" + str(index))
                    if curIndex > index:
                        if num1 == num2:
                            self.log.info("angle's child has same number error!!!")
                            return angle, result
                    curIndex += 1
                index += 1
            result = 0
        return angle, result

    def checkTaskType(self, taskType):
        result = -1
        if not isinstance(taskType, str):
            self.log.info("taskType is not str error!!!")
            result = -1
        elif taskType != JTAG_TASKTYPE_ALL and taskType != JTAG_TASKTYPE_LIGHT and taskType != JTAG_TASKTYPE_DATAFACTORY and taskType != JTAG_TASKTYPE_MODELPREVIEW:
            self.log.info("taskType not right error!!!")
            result = -1
        else:
            result = 0
        return taskType, result

    def checkName(self, name):
        result = -1
        if not isinstance(name, str):
            self.log.info("name is not string error!!!")
            result = -1
        elif name == "":
            self.log.info("name is empty error!!!")
            result = -1
        else:
            result = 0
        return name, result

    def checkMap(self, map):
        result = -1
        if not isinstance(map, str):
            self.log.info("map is not string error!!!")
            result = -1
        elif map == "":
            self.log.info("map is empty error!!!")
            result = -1
        else:
            result = 0
        return map, result

    def checkQuality(self, quality):
        result = -1
        if not isinstance(quality, int):
            self.log.info("quality is not int error!!!")
            result = -1
        elif quality != 0 and quality != 1 and quality != 2:
            self.log.info("quality out of range error!!!")
            result = -1
        else:
            result = 0
        return quality, result

    def checkIds(self, ids):
        result = -1
        if not isinstance(ids, list):
            self.log.info("ids is not list!!!")
            result = -1
        elif len(ids) < 1:
            self.log.info("ids length error!!!")
            result = -1
        elif not (len(ids) == 1 and isinstance(ids[0], int) and ids[0] > -2):
            #如果只有一个值，只能是-1 或者大于0
            self.log.info("ids len = 1 and ids[0] < -1 error!!!")
            result = -1
        else:
            index = -1
            for tmp in ids:
                index += 1
                if not isinstance(tmp, int) or tmp < 0:
                    if index == 0 and tmp == -1:
                        continue
                    result = -1
                    self.log.info("ids's child is not int or < 0 error!!!")
                    return ids, result 
            result = 0
        return ids, result

    def checkResolution(self, resolution):
        result = -1
        if not isinstance(resolution, int):
            self.log.info("resolution is not int error!!!")
            result = -1
        elif resolution != 1024 and resolution != 2048 and resolution != 4096:
            self.log.info("resolution out of range error!!!")
            result = -1
        else:
            result = 0
        return resolution, result

    def checkTaskId(self, taskId):
        result = -1
        if not isinstance(taskId, str):
            self.log.info("taskId is not str error!!!")
            result = -1
        elif len(taskId) <= 0:
            self.log.info("taskId len <= 0 error!!!")
            result = -1
        else:
            result = 0
        return taskId, result

    def checkRatio(self, ratio):
        result = -1
        if not isinstance(ratio, str):
            self.log.info("ratio is not str error!!!")
            result = -1
        elif len(ratio) <= 0:
            self.log.info("ratio len <= 0 error!!!")
            result = -1
        else:
            result = 0
        return ratio, result

    def checkPostfix(self, postfix):
        result = -1
        if not isinstance(postfix, str):
            self.log.info("postfix is not string error!!!")
            result = -1
        elif postfix == "":
            self.log.info("postfix is empty error!!!")
            result = -1
        else:
            result = 0
        return postfix, result

    def checkParams1(self, params1):
        result = -1
        if not isinstance(params1, object):
            log.info("params1 is not jobj error!!!")
            result = -1
        else:
            result = 0
        return params1, result

    ##############################################################
    #/pro end
    ##############################################################

    ##############################################################
    #config/getconfig start
    ##############################################################

    def handleRecv_config(self, path, contentData):
        isBusy = self.checkHasServerBusy()
        if isBusy or self.gIsConfiging == 1:
            response_body = "{\"" + JTAG_NAME + "\":\""+ path + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_BUSY + "\"}"
        else:
            result = self.setConfigsFromJContent(contentData)
            if result >= 0:
                response_body = "{\"" + JTAG_NAME + "\":\""+ path + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_DONE + "\"}"
            else:
                response_body = "{\"" + JTAG_NAME + "\":\""+ path + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_PARAMSERR + "\"}"
        return response_body

    def handleRecv_getConfig(self, path, contentData):
        configStr = self.getSerConfigsStr()
        response_body = "{"
        response_body += "\"" + JTAG_NAME + "\":\"" + path + "\","
        response_body += "\"" + JTAG_STATE + "\":\"" + JTAG_STATE_DONE + "\","
        response_body += "\"" + JTAG_PARAMS + "\":" + configStr
        response_body += "}"
        return response_body

    def checkHasServerBusy(self):
        #log.info("checkHasServerBusy()")
        result = 0

        jConfigStr = self.getSerConfigsStr()
        jConfig = json.loads(jConfigStr)

        jConfigAll = jConfig[JTAG_TASKTYPE_ALL]
        jConfigAllLen = len(jConfigAll)

        #计数每个status文件
        mIndex = 0
        #遍历 all 群
        for jobj in jConfigAll:
            tName, tTaskType ,tState, tTaskId, tRatio, tPostfix, tStateStr = self.getCheckStateFromFile(mIndex)
            if tState != JTAG_STATE_DONE and tState != "" and tState != JTAG_STATE_ERROR:
                result = 1
                return result
            mIndex += 1

        jConfigLight = jConfig[JTAG_TASKTYPE_LIGHT]
        jConfigLightLen = len(jConfigLight)
        #遍历 light 群
        for ipStr in jConfigLight:
            tName, tTaskType ,tState, tTaskId, tRatio, tPostfix, tStateStr = self.getCheckStateFromFile(mIndex)
            if tState != JTAG_STATE_DONE and tState != "" and tState != JTAG_STATE_ERROR:
                result = 1
                return result
            mIndex += 1
        
        jConfigDatafactory = jConfig[JTAG_TASKTYPE_DATAFACTORY]
        jConfigDatafactoryLen = len(jConfigDatafactory)
        #遍历 datafactory 群
        for ipStr in jConfigDatafactory:
            tName, tTaskType ,tState, tTaskId, tRatio, tPostfix, tStateStr = self.getCheckStateFromFile(mIndex)
            if tState != JTAG_STATE_DONE and tState != "" and tState != JTAG_STATE_ERROR:
                result = 1
                return result
            mIndex += 1
        
        return result

    #检查IP地址 正规性
    def checkConfigIp(self, ip):
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
            self.log.info("is not right ip regex error!!!")
        return result

    #检查 all 里面 angles数组里面的内容
    def checkConfigSerAngles(self, mSerAngles):
        result = 0
        if not isinstance(mSerAngles, list):
            self.log.info("mSerAngles is not list error!!!")
            result = -1
        else:
            cntAngles = len(mSerAngles)
            for tmp in mSerAngles:
                rtnAngle, rtn = self.checkAngle(tmp)
                if rtn < 0:
                    result = -1
                    break

        return mSerAngles, result

    def checkConfigSerIps(self, mSerIps):
        result = 0
        # not list
        if not isinstance(mSerIps, list):
            self.log.info("mSerIps is not list error!!!")
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
                    self.log.info("mSerIps' child  is not string error!!!")
                    break
                else:
                    #check ip regex
                    ret = regex.match(tmp)
                    if ret == None:
                        result = -1
                        self.log.info("mSerIps' child  is not right ip regex error!!!")
                        break
            #check have the same ip addr
            index = 0
            for item1 in mSerIps:
                curIndex = 0
                for item2 in mSerIps:
                    #self.log.info("item1:" + str(item1) + " item2:" + str(item2) + " curIndex:" + str(curIndex) + " index:" + str(index))
                    if curIndex > index:
                        if item1 == item2:
                            self.log.info("mSerIps's child has same itme error!!!")
                            result = -1
                            break
                    curIndex += 1
                index += 1
        return mSerIps, result

    #检查配置文件， all里面的其中一个item里面的SER_IPS 和 SER_ANGLES
    def checkConfigSerAllItem(self, jobj):
        result = -1
        while True:
            if(JTAG_SERIPS in jobj.keys()):
                mSerIps  = jobj[JTAG_SERIPS]
                mSerIps , result = self.checkConfigSerIps(mSerIps)
                if result < 0:
                    break
            else:
                self.log.info("config json data mSerIps not find error!!!")
                result = -1
                break
            if(JTAG_SERANGLES in jobj.keys()):
                mSerAngles  = jobj[JTAG_SERANGLES]
                mSerAngles, result = self.checkConfigSerAngles(mSerAngles)
                if result < 0:
                    break
            else:
                self.log.info("config json data mSerAngles not find error!!!")
                result = -1
                break
            #check length is the same 
            cntIps = len(mSerIps)
            cntAngles = len(mSerAngles)
            if cntAngles != cntIps:
                self.log.info("config json data cntAngles != cntIps error!!!")
                result = -1
            break
        return result

    #get configs file content
    def getSerConfigsStr(self):
        rtnStr = "{\"" + JTAG_TASKTYPE_ALL + "\":[], \"" + JTAG_TASKTYPE_LIGHT + "\":[], \""+ JTAG_TASKTYPE_DATAFACTORY + "\":[]}"
        try:
            file = open(FILE_CFG_PATH, "r")
            tmpStr = file.read()
            #self.log.info('config file content:' + tmpStr + ' len:' + str(len(tmpStr)))
            jobj = json.loads(tmpStr)
            if(JTAG_TASKTYPE_ALL in jobj.keys()) and (JTAG_TASKTYPE_LIGHT in jobj.keys()) and (JTAG_TASKTYPE_DATAFACTORY in jobj.keys()):
                rtnStr = tmpStr
            file.close()
        except:
            self.log.info("getSerConfigsStr() error!!!")
            self.log.info(traceback.format_exc())
        return rtnStr
    
    #get SER_IPS and SER_ANGLES from configfiles json item
    def getSerIpsAndSerAngles(self, jobj):
        mSerIps = []
        mSerAngles = []
        try:
            if(JTAG_SERIPS in jobj.keys()):
                mSerIps  = jobj[JTAG_SERIPS]
            if(JTAG_SERANGLES in jobj.keys()):
                mSerAngles  = jobj[JTAG_SERANGLES]
        except:
            self.log.info("getSerIpsAndSerAngles() error!!!")
            self.log.info(traceback.format_exc())
        #self.log.info("getSerIpsAndSerAngles -- mSerIps:" + str(mSerIps) + " mSerAngles:" + str(mSerAngles))
        return mSerIps, mSerAngles
    
    gIsConfiging = 0

    #/config
    def setConfigsFromJContent(self, jContent):
        self.gIsConfiging = 1
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
                    # 	self.log.info("config json data 'all' ary len < 0 error!!!")
                    # 	result = -1
                    # 	break
                    for tmpObj in aryAll:
                        result = self.checkConfigSerAllItem(tmpObj)
                        if result < 0:
                            result = -1
                            break
                    if result < 0:
                        break
                else:
                    self.log.info("config json data 'all' not find or not list error!!!")
                    result = -1
                    break

                #check 'light'
                if(JTAG_TASKTYPE_LIGHT in jobj.keys() and isinstance(jobj[JTAG_TASKTYPE_LIGHT], list)):
                    aryLight = jobj[JTAG_TASKTYPE_LIGHT]
                    aryLightLen = len(aryLight)
                    #允许置空吧
                    # if aryLightLen <= 0:
                    # 	self.log.info("config json data 'light' ary len < 0 error!!!")
                    # 	result = -1
                    # 	break
                    for tmpObj in aryLight:
                        if isinstance(tmpObj, str):
                            result = self.checkConfigIp(tmpObj)
                            if result < 0:
                                result = -1
                                break
                        else:
                            self.log.info("config json data 'light' 's IP  is not str error!!!")
                            result = -1
                            break
                    if result < 0:
                        break
                else:
                    self.log.info("config json data 'light' not find or not list error!!!")
                    result = -1
                    break
                #check 'datafactory'
                if(JTAG_TASKTYPE_DATAFACTORY in jobj.keys() and isinstance(jobj[JTAG_TASKTYPE_DATAFACTORY], list)):
                    aryDatafactory = jobj[JTAG_TASKTYPE_DATAFACTORY]
                    aryDatafactoryLen = len(aryDatafactory)
                    #允许置空吧
                    # if aryLightLen <= 0:
                    # 	self.log.info("config json data 'light' ary len < 0 error!!!")
                    # 	result = -1
                    # 	break
                    for tmpObj in aryDatafactory:
                        if isinstance(tmpObj, str):
                            result = self.checkConfigIp(tmpObj)
                            if result < 0:
                                result = -1
                                break
                        else:
                            self.log.info("config json data 'datafactory' 's IP  is not str error!!!")
                            result = -1
                            break
                    if result < 0:
                        break
                else:
                    self.log.info("config json data 'datafactory' not find or not list error!!!")
                    result = -1
                    break
                break
            if result >= 0:
                file = open(FILE_CFG_PATH, "w")
                file.write(jContent)
                file.close()
                self.initAryStatus()
            else:
                self.log.info("config json data ok but write file error!!!")
                result = -1
        except:
            result = -1
            self.log.info("setConfigsFromJContent() error!!!")
            self.log.info(traceback.format_exc())
        self.log.info("setConfigsFromJContent -- result:" + str(result))
        self.gIsConfiging = 0
        return result

    ##############################################################
    #config/getconfig end
    ##############################################################
    

    ##############################################################
    #/check start
    ##############################################################
    
    def handleRecv_check(self, path, contentData):
        resultStr, result = self.getCheckState(contentData)
        if result < 0:
            response_body = "{\"" + JTAG_NAME + "\":\""+ path + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_PARAMSERR + "\"}"
        else:
            response_body = "{\"" + JTAG_NAME + "\":\""+ path + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_DONE + "\",\"" + JTAG_MSG + "\":" + resultStr + "}"
        return response_body
    
    gCheckPrec = 1

    #每秒检查状态
    def checkStatePreSec(self):
        self.cntCheck = 0
        while self.gCheckPrec:
            # self.log.info("checkStatePreSec")
            self.checkState()
            time.sleep(1)
        self.log.info("server close, stop checking 88~~~~")

    #结束检查
    def endCheckStatePreSec(self):
        self.gCheckPrec = 0

    PRINT_ALLCHECK_TM = 10

    #检查所有功能机状态
    def checkState(self):
        jConfigStr = self.getSerConfigsStr()
        jConfig = json.loads(jConfigStr)

        jConfigAll = jConfig[JTAG_TASKTYPE_ALL]
        jConfigAllLen = len(jConfigAll)
        #计数每个status文件
        mIndex = 0
        for jobj in jConfigAll:
            self.checkStatePreSec_allitem(mIndex, jobj)
            mIndex += 1

        jConfigLight = jConfig[JTAG_TASKTYPE_LIGHT]
        jConfigLightLen = len(jConfigLight)
        for ipStr in jConfigLight:
            self.checkStatePreSec_lightitem(mIndex, ipStr)
            mIndex += 1
        
        jConfigDatafactory = jConfig[JTAG_TASKTYPE_DATAFACTORY]
        jConfigDatafactoryLen = len(jConfigDatafactory)
        for ipStr in jConfigDatafactory:
            self.checkStatePreSec_datafactoryitem(mIndex, ipStr)
            mIndex += 1

        self.cntCheck += 1
        if self.cntCheck >= self.PRINT_ALLCHECK_TM:
            self.cntCheck = 0
            self.log.info(str(self.PRINT_ALLCHECK_TM) + "sec check print:" + str(self.ARY_STATUS))
    
    def checkStatePreSec_allitem(self, index, jobj):
        #self.log.info("handle_CheckStatePreSec_allitem() [" + str(index) +"]")
        mSerIps, mSerAngles = self.getSerIpsAndSerAngles(jobj)
        cntServs = len(mSerIps)
        mIndex = -1
        mStateStr = "["
        mTmpStr = ""
        for ipStr in mSerIps:
            mIndex += 1
            #self.log.info("[" + str(mIndex) + "]:" + "ip:" + ipStr)
            try:
                url = ipStr + URL_PATH_CHECK
                f = urllib.request.urlopen(url)
                mTmpStr =  f.read().decode('utf-8')
                #self.log.info("[" + str(mIndex) + "]:" + mTmpStr)
                if mIndex == (cntServs - 1):
                    mStateStr += mTmpStr
                    mStateStr += "]"
                else:
                    mStateStr += mTmpStr
                    mStateStr += ","
                f.close()
            except :
                self.log.info("[" + str(mIndex) + " " + str(ipStr) + "]: check all dev state error!!!")
                self.log.info(traceback.format_exc())
                errMsg = "{\"" + JTAG_NAME + "\":\"\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_SERVERERR + "\"}"
                if mIndex == (cntServs - 1):
                    mStateStr += errMsg
                    mStateStr += "]"
                else:
                    mStateStr += errMsg
                    mStateStr += ","

                self.sendCheckErrMail(ipStr, self.genSendMailMsg(ipStr, JTAG_TASKTYPE_ALL, self.MAIL_ERR_MSG_CHECKERR))

        #self.log.info("all>>>[" + str(index) + "]combine str:" + mStateStr)
        self.setStausStrToStatusAry(index, mStateStr)

    def checkStatePreSec_lightitem(self, index, ip):
        #self.log.info("handle_CheckStatePreSec_lightitem() [" + str(index) +"]")
        mStateStr = "["
        try:
            url = ip + URL_PATH_CHECK
            f = urllib.request.urlopen(url)
            mTmpStr =  f.read().decode('utf-8')
            #self.log.info("[" + str(index) + "]:" + mTmpStr)
            mStateStr += mTmpStr
            mStateStr += "]"
            f.close()
        except :
            self.log.info("[" + str(index) + " " + str(ip) + "]: check light dev state error!!!!")
            self.log.info(traceback.format_exc())
            errMsg = "{\"" + JTAG_NAME + "\":\"\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_SERVERERR + "\"}"
            mStateStr += errMsg
            mStateStr += "]"
            self.sendCheckErrMail(ip, self.genSendMailMsg(ip, JTAG_TASKTYPE_LIGHT, self.MAIL_ERR_MSG_CHECKERR))

        #self.log.info("light>>>[" + str(index) + "]combine str:" + mStateStr)
        self.setStausStrToStatusAry(index, mStateStr)

    def checkStatePreSec_datafactoryitem(self, index, ip):
        #self.log.info("handle_CheckStatePreSec_lightitem() [" + str(index) +"]")
        mStateStr = "["
        try:
            url = ip + URL_PATH_CHECK
            f = urllib.request.urlopen(url)
            mTmpStr =  f.read().decode('utf-8')
            #self.log.info("[" + str(index) + "]:" + mTmpStr)
            mStateStr += mTmpStr
            mStateStr += "]"
            f.close()
        except :
            self.log.info("[" + str(index) + " " + str(ip) + "]: check datafactory state error!!!!")
            self.log.info(traceback.format_exc())
            errMsg = "{\"" + JTAG_NAME + "\":\"\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_SERVERERR + "\"}"
            mStateStr += errMsg
            mStateStr += "]"
            self.sendCheckErrMail(ip, self.genSendMailMsg(ip, JTAG_TASKTYPE_DATAFACTORY, self.MAIL_ERR_MSG_CHECKERR))

        #self.log.info("datafactory>>>[" + str(index) + "]combine str:" + mStateStr)
        self.setStausStrToStatusAry(index, mStateStr)

    #检查状态， 返回多个或单个状态
    #如果jContentStr 不为空，及包含 name 和 taskType 就返回对应的状态回去（如果多个 name 和 taskType 相同，会返回多个）
    #如果jContentStr 为空，就会返回所有状态文件的状态回去
    #如果参数由问题，就返回参数有错误
    def getCheckState(self, jContentStr):
        #self.log.info("getCheckState() - jContentStr:" + str(jContentStr))
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
                        mTaskType, result = self.checkTaskType(mTaskType)
                        if result < 0:
                            self.log.info("getCheckState() read json mTaskType error!!!")
                            result = -1
                            break
                    else:
                        self.log.info("getCheckState() read json not find tasktype error!!!")
                        result = -1
                        break

                    #check name
                    if JTAG_NAME in jobj.keys():
                        mName = jobj[JTAG_NAME]
                        #tasktype all 才要判断 name有没有问题
                        #tasktype datafactory 也要判断name有没有问题，敬然说name是标识，taskId只是存个文件夹
                        if mTaskType == JTAG_TASKTYPE_ALL or mTaskType == JTAG_TASKTYPE_DATAFACTORY :
                            mName, result = self.checkName(mName)
                            if result < 0:
                                self.log.info("getCheckState() read json name error!!!")
                                break
                    else:
                        #tasktype all 才要判断 name是否是空
                        #tasktype datafactory 也要判断name有没有问题，敬然说name是标识，taskId只是存个文件夹
                        if mTaskType == JTAG_TASKTYPE_ALL or mTaskType == JTAG_TASKTYPE_DATAFACTORY or mTaskType == JTAG_TASKTYPE_MODELPREVIEW:
                            self.log.info("getCheckState() read json not find name!!!")
                            result = -1
                            break
                    
                    #check taskid 是否存在
                    if mTaskType == JTAG_TASKTYPE_LIGHT:
                        if JTAG_TASKID in jobj.keys():
                            mTaskId = jobj[JTAG_TASKID]
                            mTaskId, result = self.checkTaskId(mTaskId)
                            if result < 0:
                                self.log.info("getCheckState() read json taskId error!!!")
                                break
                        else:
                            self.log.info("getCheckState() read json not find taskId!!!")
                            result = -1
                            break

                    # 两个都没问题就直接找对口的返回吧
                    break
                except:
                    self.log.info("getCheckState() read json error!!!")
                    result = -1
                    break
        
        if result < 0:
            #参数有错误，直接返回
            return resultStr, result

        #开始封装返回数据
        resultStr = "["

        jConfigStr = self.getSerConfigsStr()
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
            tName, tTaskType ,tState, tTaskId, tRatio, tPostfix, tStateStr = self.getCheckStateFromFile(mIndex)
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
            tName, tTaskType ,tState, tTaskId, tRatio, tPostfix, tStateStr = self.getCheckStateFromFile(mIndex)
            #修复原本是light，显示all，因默认都是all，这里将all转化成light，好看一点
            if tTaskType == JTAG_TASKTYPE_ALL:
                tStateStr = tStateStr.replace(JTAG_TASKTYPE_ALL, JTAG_TASKTYPE_LIGHT)
            if isShowAll:
                resultStr += tStateStr
                resultStr += ","
            else:
                #这里是获取 light 的 check信息
                if mTaskType == JTAG_TASKTYPE_LIGHT and tTaskId == mTaskId and tTaskType == mTaskType:
                    resultStr += tStateStr
                    resultStr += ","
                #这里是获取 modelpreview 的 check信息
                if mTaskType == JTAG_TASKTYPE_MODELPREVIEW and tName == mName:
                    resultStr += tStateStr
                    resultStr += ","
            mIndex += 1
        
        #遍历 datafactory 群
        for ipStr in jConfigDatafactory:
            tName, tTaskType ,tState, tTaskId, tRatio, tPostfix, tStateStr = self.getCheckStateFromFile(mIndex)
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
        
        #self.log.info("getCheckState() -- tmp result str["+ resultStr +"]")
        #去掉最后一个逗号
        totalLen = len(resultStr)
        if not isShowAll and totalLen <= 1:
            self.log.info("getCheckState() -- can not find["+ mName +"]["+ mTaskType +"]" + " state!!!")
        else:
            if totalLen > 1:
                resultStr = resultStr[0:(totalLen-1)]
        #完成整个返回数据的封装	
        resultStr += "]"

        self.log.info("getCheckState() -- " + resultStr)
        return resultStr, result

    ##############################################################
    #/check end
    ##############################################################
    
    
    ##############################################################
    #/history start
    ##############################################################
    def handleRecv_history(self, path, contentData):
        response_body = self.readHistoryReqPro()
        return response_body

    #最多记录多少条历史记录
    HISTORY_LENGTH_MAX = 10

    #记录历史记录
    ARY_HISTORY_REQ_PRO = []

    #读取req pro的记录
    def readHistoryReqPro(self):
        result = "["
        lenHistory = len(self.ARY_HISTORY_REQ_PRO)
        index = lenHistory - 1
        while index >= 0:
            result += self.ARY_HISTORY_REQ_PRO[index]
            if index > 0:
                result += ","
            index -= 1
        result += "]"
        #log.info("readHistoryReqPro() --- " + result)
        return result

        #记录req pro的记录
    def writeHistoryReqPro(self, content):
        strTime = self.get_time_stamp()
        strHistory = "{"
        strHistory += "\"time\":\"" + strTime + "\","
        strHistory += "\"" + JTAG_PARAMS + "\":" + content
        strHistory += "}"
        #log.info("writeHistoryReqPro() --- " + strHistory)
        if len(self.ARY_HISTORY_REQ_PRO) >= self.HISTORY_LENGTH_MAX:
            self.ARY_HISTORY_REQ_PRO.pop(0)
        self.ARY_HISTORY_REQ_PRO.append(strHistory)
        #log.info("writeHistoryReqPro() --- " + str(len(ARY_HISTORY_REQ_PRO)) + " " + str(ARY_HISTORY_REQ_PRO))


    ##############################################################
    #/history end
    ##############################################################

    ##############################################################
    #/getLightInfo start
    ##############################################################
    def handleRecv_getLightInfo(self, path, contentData):
        #get data from http req header content
        isRightParams = 1
        resultStr = ""
        try:
            deploy = LightingDeploy()
            resultStr = deploy.deploy(contentData)
            self.log.info("getLightInfo() succ rtn:" + resultStr)
        except:
            self.log.info("handle_client() recv 'getLightInfo' --- run deploy error!!!!!!")
            isRightParams = 0

        if isRightParams == 1:
            response_body = "{\"" + JTAG_NAME + "\":\""+ path + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_DONE + "\",\"" + JTAG_MSG + "\":" + resultStr + "}"
        else:
            response_body = "{\"" + JTAG_NAME + "\":\""+ path + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_PARAMSERR + "\"}"
        return response_body

    ##############################################################
    #/getLightInfo end
    ##############################################################

    ##############################################################
    #/bye start
    ##############################################################
    def handleRecv_bye(self, path, contentData):
        isBusy = self.checkHasServerBusy()
        if isBusy or (self.gIsConfiging == 1):
            response_body = "{\"" + JTAG_NAME + "\":\""+ path + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_BUSY + "\"}"
        else:
            response_body = "{\"" + JTAG_NAME + "\":\""+ path + "\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_DONE + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_BYE + "\"}"
            self.endCheckStatePreSec()
        return response_body

    ##############################################################
    #/bye end
    ##############################################################

    ##############################################################
    #/fixmodel start
    ##############################################################

    def handleRecv_fixmodel(self, path, contentData):
        if self.gIsConfiging == 1:
            response_body = "{\"" + JTAG_NAME + "\":\""+ path + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_BUSY + "\"}"
            return response_body
        
        mName, mTaskId, result = self.getFixModelInfosFromJContent(contentData)
        if result < 0:
            response_body = "{\"" + JTAG_NAME + "\":\""+ str(mName) + "\", \"" + JTAG_TASKID + "\":\"" + mTaskId + "\", \"" + JTAG_TASKTYPE + "\":\"" + JTAG_TASKTYPE_FIXMODEL + "\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\", \"" + JTAG_MSG + "\":\"" + JTAG_MSG_PARAMSERR + "\"}"
        else:
            response_body = self.handle_SendReqToServers_datafactory_fixmodel(mName, mTaskId, contentData)
        return response_body

    
    #get FixModel infos from request content json string
    def getFixModelInfosFromJContent(self, jContent):
        mName = ""
        mTaskId = ""
        result = 0
        while(1):
            try:
                jobj = json.loads(jContent)
                #check name
                if(JTAG_NAME in jobj.keys()):
                    mName  = jobj[JTAG_NAME]
                    mName, result = self.checkName(mName)
                    if result < 0:
                        break
                else:
                    self.log.info("content json data name not find error!!!")
                    result = -1
                    break
                #check taskId
                if(JTAG_TASKID in jobj.keys()):
                    mTaskId  = jobj[JTAG_TASKID]
                    mTaskId, result = self.checkTaskId(mTaskId)
                    if result < 0:
                        break
                else:
                    self.log.info("content json data taskid not find error!!!")
                    result = -1
                    break
                #check end break while
                break
            except :
                result = -1
                self.log.info("getFixModelInfosFromJContent error!!!")
                self.log.info(traceback.format_exc())
                break
        self.log.info("getFixModelInfosFromJContent -- name:" + str(mName) + " taskId:" + str(mTaskId) + " result:" + str(result))
        return mName, mTaskId, result


    def handle_SendReqToServers_datafactory_fixmodel(self, mName, mTaskId, mContent):
        rtnMsg = "{\"" + JTAG_NAME + "\":\"" + mName + "\", \"" + JTAG_TASKID + "\":\"" + mTaskId + "\", \""  + JTAG_TASKTYPE + "\":\"" + JTAG_TASKTYPE_FIXMODEL + "\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_SERVERERR + "\"}"
        try:
            jConfigStr = self.getSerConfigsStr()
            jConfig = json.loads(jConfigStr)
            jConfigDatafactory = jConfig[JTAG_TASKTYPE_DATAFACTORY]
            jConfigDatafactoryLen = len(jConfigDatafactory)
            if jConfigDatafactoryLen <= 0:
                self.log.info("handle_SendReqToServers_datafactory_fixmodel() error!!! no config datafactory server")
            else:
                #取第一个来做model
                ipStr = jConfigDatafactory[0]
                dataStrBytes = mContent.encode('utf-8')
                url = ipStr + URL_PATH_FIXMODEL
                f = urllib.request.urlopen(url, dataStrBytes, timeout=90)
                rtnMsg = f.read().decode('utf-8')
                self.log.info("handle_SendReqToServers_datafactory_fixmodel() rtn:" + rtnMsg)
                f.close()
        except :
            self.log.info("handle_SendReqToServers_datafactory_fixmodel() request error!!!!")
            self.log.info(traceback.format_exc())
        return rtnMsg

    ##############################################################
    #/fixmodel end
    ##############################################################


    ##############################################################
    #/syncmodel start
    ##############################################################

    def handleRecv_syncmodel(self, path, contentData):
        if self.gIsConfiging == 1:
            response_body = "{\"" + JTAG_NAME + "\":\""+ path + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_BUSY + "\"}"
            return response_body
        mVersion, result = self.getSyncDownloadModelInfosFromJContent(contentData)
        if result < 0:
            response_body = "{\"" + JTAG_NAME + "\":\""+ str(path) + "\", \"" + JTAG_VERSION + "\":\"" + mVersion + "\", \"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\", \"" + JTAG_MSG + "\":\"" + JTAG_MSG_PARAMSERR + "\"}"
        else:
            response_body = self.handle_SendReqToServers_SyncDownloadModel(path, mVersion, contentData)
        return response_body

    def checkVersion(self, version):
        result = -1
        if not isinstance(version, str):
            self.log.info("version is not string error!!!")
            result = -1
        elif version == "":
            self.log.info("version is empty error!!!")
            result = -1
        else:
            result = 0
        return version, result
    
    #get sync download model infos from request content json string
    def getSyncDownloadModelInfosFromJContent(self, jContent):
        mVersion = ""
        result = 0
        while(1):
            # try:
            jobj = json.loads(jContent)
            #check name
            if(JTAG_VERSION in jobj.keys()):
                mVersion  = jobj[JTAG_VERSION]
                mVersion, result = self.checkVersion(mVersion)
                if result < 0:
                    break
            else:
                self.log.info("content json data name not find error!!!")
                result = -1
                break
            break
            # except json.decoder.JSONDecodeError:
            # 	result = -1
            # 	log.info("conntent json data error!!!")
            # 	break
        self.log.info("getSyncDownloadModelInfosFromJContent -- version:" + str(mVersion))
        return mVersion, result

    def newthread_SendReqToServers_SyncDownloadModel(self, path, aryResults, index, ip, dataStrBytes):
        self.log.info("newthread_SendReqToServers_syncmodel() path:" + str(path) + " index:" + str(index) + " ip:" + str(ip) + " dataStrBytes:" + str(dataStrBytes))
        url = ip + path
        f = urllib.request.urlopen(url, dataStrBytes, timeout=310)
        rtnMsg = f.read().decode('utf-8')
        f.close()
        self.log.info("newthread_SendReqToServers_SyncDownloadModel() path:" + str(path) + " index:" + str(index) + " rtn:" + rtnMsg)
        if rtnMsg.find(JTAG_STATE_ERROR) >= 0:
            aryResults[index] = "error"
        else:
            aryResults[index] = "done"
        
    def handle_SendReqToServers_SyncDownloadModel(self, path, version, mContent):
        self.log.info("handle_SendReqToServers_SyncDownloadModel() version:" + str(version) + " content:" + str(mContent) )
        rtnMsg = "{\"" + JTAG_NAME + "\":\"" + path + "\", \"" + JTAG_VERSION + "\":\"" + version + "\", \""  + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + "" + "\"}"
        try:
            aryIPs = []

            if path == URL_PATH_SYNCMODEL:
                jConfigStr = self.getSerConfigsStr()
                jConfig = json.loads(jConfigStr)
                jConfigDatafactory = jConfig[JTAG_TASKTYPE_DATAFACTORY]
                jConfigDatafactoryLen = len(jConfigDatafactory)
                #添加light 机群的所有IP
                for tmpIP in jConfigDatafactory:
                    aryIPs.append(tmpIP)

            elif path == URL_PATH_DOWNLOADMODEL:
                jConfigStr = self.getSerConfigsStr()
                jConfig = json.loads(jConfigStr)
                jConfigAll = jConfig[JTAG_TASKTYPE_ALL]
                jConfigAllLen = len(jConfigAll)

                jConfigLight = jConfig[JTAG_TASKTYPE_LIGHT]
                jConfigLightLen = len(jConfigLight)
                #添加all 机群的所有IP
                for tmpObj in jConfigAll:
                    arySerIPs = tmpObj["SER_IPS"]
                    for tmpIP in arySerIPs:
                        aryIPs.append(tmpIP)
                #添加light 机群的所有IP
                for tmpIP in jConfigLight:
                    aryIPs.append(tmpIP)

            self.log.info("handle_SendReqToServers_SyncDownloadModel() " + str(path) + " IPs:" + str(aryIPs))

            lenIPs = len(aryIPs)

            if lenIPs <= 0:
                self.log.info("handle_SendReqToServers_SyncDownloadModel() " + str(path) + " no server error!!!")
                return rtnMsg

            aryResults = []
            #全部状态清空
            for tmpIP in aryIPs:
                aryResults.append("")

            mIndex = 0
            dataStrBytes = mContent.encode('utf-8')
            for tmpIP in aryIPs:
                t = threading.Thread(target=self.newthread_SendReqToServers_SyncDownloadModel, args=(path, aryResults, mIndex, tmpIP, dataStrBytes))
                t.start()
                mIndex += 1
                time.sleep(0.1)
            
            cntError = 0
            isRtnEnd = 0
            while isRtnEnd == 0:
                self.log.info("handle_SendReqToServers_SyncDownloadModel() " + str(path) + " check:" + str(aryResults))
                cntError = 0
                mIndex = 0
                for tmpResult in aryResults:
                    if tmpResult == "":
                        break
                    if tmpResult == "error":
                        cntError += 1
                        self.log.info("handle_SendReqToServers_SyncDownloadModel() " + str(path) + " index:" + str(mIndex) + " find error!!!")
                    mIndex += 1
                    if mIndex >= lenIPs:
                        isRtnEnd = 1
                time.sleep(1)
            if cntError <= 0:
                rtnMsg = "{\"" + JTAG_NAME + "\":\"" + path + "\", \"" + JTAG_VERSION + "\":\"" + version + "\", \""  + JTAG_STATE + "\":\"" + JTAG_STATE_DONE + "\",\"" + JTAG_MSG + "\":\"" + "\"}"
            
        except :
            self.log.info("handle_SendReqToServers_syncmodel() request error!!!!")
            self.log.info(traceback.format_exc())
        return rtnMsg

    ##############################################################
    #/syncmodel end
    ##############################################################

    ##############################################################
    #handle http recv start
    ##############################################################
    def handleRecv(self, path, contentData):
        if path == URL_PATH_CHECK:
            return self.handleRecv_check(path, contentData)
        elif path == URL_PATH_CFG:
            return self.handleRecv_config(path, contentData)
        elif path == URL_PATH_GETCFG:
            return self.handleRecv_getConfig(path, contentData)
        elif path == URL_PATH_HISTORY:
            return self.handleRecv_history(path, contentData)
        elif path == URL_PATH_GETLIGHTINFO:
            return self.handleRecv_getLightInfo(path, contentData)
        elif path == URL_PATH_BYE:
            return self.handleRecv_bye(path, contentData)
        elif path == URL_PATH_PRO:
            return self.handleRecv_pro(path, contentData)
        elif path == URL_PATH_FIXMODEL:
            return self.handleRecv_fixmodel(path, contentData)
        elif path == URL_PATH_SYNCMODEL:
            return self.handleRecv_syncmodel(path, contentData)
        else:
            response_body = "{\"" + JTAG_NAME + "\":\""+ path + "\",\"" + JTAG_STATE + "\":\"" + JTAG_STATE_ERROR + "\",\"" + JTAG_MSG + "\":\"" + JTAG_MSG_UNKNOWN + "\"}"
            return response_body

    ##############################################################
    #handle http recv end
    ##############################################################

    ##############################################################
    #handle send error email start 
    ##############################################################

    MAIL_ERR_MSG_CHECKERR = "Server check ERROR!!!"

    def genSendMailMsg(self, ip, taskType, msg):
        return (str(ip) + " '" + str(taskType) + "' " + str(msg))

    #同样的邮件内容，间隔时间，要大于下面这个值才会发第二次，不然邮箱都爆了
    SEND_MAIL_SEP = 10 * 60

    #K-V K：发的内容content， V：发的时候的秒数（time.time()）
    #用于，如果发送时间间隔大于SEND_MAIL_SEP，才重复发邮件
    gCheckErrMailHistory = {}

    def sendCheckErrMail(self, ip, content):
        needSend = 0
        if content in self.gCheckErrMailHistory.keys():
            oldTime = self.gCheckErrMailHistory[content]
            nowTime = time.time()
            self.log.info("rptest --- nowTime:" + str(nowTime) + " oldTime:" + str(oldTime) + " sep:" + str(nowTime - oldTime))
            if (nowTime - oldTime) > self.SEND_MAIL_SEP:
                needSend = 1
            else:
                needSend = 0
        else:
            needSend = 1

        if needSend == 1:
            self.gCheckErrMailHistory[content] = time.time()
            t = threading.Thread(target=self.newthread_sendCheckErrMail, args=(ip, content,))
            t.start()
    
    def newthread_sendCheckErrMail(self, ip, content):
        self.log.info("send chek error mail>>" + str(ip) + ">>" + str(content))
        try:
            # 第三方 SMTP 服务
            #设置服务器
            mail_host="smtp.163.com"
            #用户名  
            mail_user="18813863320@163.com"
            #口令  
            mail_pass="sunchip123"
            sender = '18813863320@163.com'
            # receivers = ['356852346@qq.com', '1522631439@qq.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
            receivers = ['356852346@qq.com', 'wartheking@163.com']  # 接收邮件，可设置为你的QQ邮箱或者其他邮箱
            
            message = MIMEText(content, 'plain', 'utf-8')
            message['from'] = "18813863320@163.com"
            #发给多人，在这里加邮箱
            # message['to'] =  "356852346@qq.com,1522631439@qq.com"
            message['to'] =  "356852346@qq.com,wartheking@163.com"
            subject = "UE4 Server warning!!!" + " - " + str(ip)
            message['Subject'] = Header(subject, 'utf-8')

            smtpObj = smtplib.SMTP() 
            smtpObj.connect(mail_host, 25)    # 25 为 SMTP 端口号
            code, resp = smtpObj.login(mail_user, mail_pass)
            self.log.info("code:" + str(code) + " resp:" + str(resp))
            smtpObj.sendmail(sender, receivers, message.as_string())
            self.log.info("发送邮件成功-content:" + str(content))
        except smtplib.SMTPException:
            self.log.info("Error: 无法发送邮件-content:" + str(content))
            self.log.info(traceback.format_exc())

    ##############################################################
    #handle send error email end
    ##############################################################
 
    def __init__(self, log=None):
        #init log
        self.log = log
        self.log.info("init()")

        #check 文件夹都创建没有
        self.checkAndCreateDir(DIR_PATH)

        #init status array
        self.initAryStatus()

        #check servs state
        t = threading.Thread(target=self.checkStatePreSec, args=())
        t.start()



