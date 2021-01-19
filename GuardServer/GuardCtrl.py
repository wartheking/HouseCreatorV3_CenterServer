#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding:utf-8

import psutil
import pyautogui
import time, os, threading, platform, json, traceback, socket
import urllib.request
from Logger import *
from Util import *
log = getLogger()

URL_PATH_EXECUTE = "/execute"
URL_PATH_CALLBACK = "/callback"
URL_PATH_GETALLTASKS = "/getAllTasks"
URL_PATH_GETHISTORYTASKS = "/getHistoryTasks"
URL_PATH_ABORT = "/abort"

JTAG_PATH = "path"
JTAG_STATE = "state"
JTAG_STATE_DONE = "done"
JTAG_STATE_ERROR = "error"
JTAG_MSG = "msg"
JTAG_DATA = "data"
JTAG_MSG_PARAMSERR = "params error"
JTAG_MSG_BUSY = "isBusy"
JTAG_MSG_UNKNOWN = "unknown"
JTAG_MSG_PIDNOTFOUND = "pid not found"
JTAG_MSG_NOTPERMIT = "not permit"
JTAG_NAME = "name"
JTAG_PARAMS = "params"

JTAG_PID_CMD =  "cmd"
JTAG_PID_PY = "py"
JTAG_PID_NAME = "name"
JTAG_PID_PARAMS = "params"
JTAG_PID_STATUS = "status"
JTAG_PID_TM_START = "tm_start"
JTAG_PID_TM_END = "tm_end"

JTAG_PID_STATUS_RUNNING = "running"
JTAG_PID_STATUS_BACKGROUND = "background"
JTAG_PID_STATUS_FINISHED = "finished"
JTAG_PID_STATUS_ERROR = "error"
JTAG_PID_STATUS_ABORT = "abort"

#就是如果 status是running，但是python的PID 不见了
#这个时候就是判断start time 和 now time 之间的差，如果大于10秒就认为是异常的了
#异常的和finished的就会自动关掉窗口（pid）
PID_TM_MAX = 10
TAG_GUARD = "Guard.py"

class GuardCtrl:

    gPathCmdDir = ""
    gAryPids = []
    gAryPidsHistory = []

    gIsRunningPyFile = 0
    gNowPyName = ""
    gNowPyParams = []

    def markdownIPAddr(self):
        pathWebJs = os.path.abspath(os.path.join(sys.argv[0], "..")) + "/web/IP.js"
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        log.info("markdownIPAddr() --- ip:" + str(ip))
        fd = open(pathWebJs, "w")
        fd.write("var DEV_IP = \"http://" + str(ip) + ":9000" + "\"")
        fd.close()

    def killCmds(self, aryPids=[]):
        if len(aryPids) <= 0:
            log.info("aryPids len <= 0!!!")
            return 0
        try:
            if platform.platform().find("Windows") >= 0:
                find_kill = "taskkill"
                #获取每个进程的名字 和 pid
                for pid in aryPids:
                    find_kill += (" /PID " + str(pid))
                find_kill += " -f"
                log.info("win cmd:" + find_kill)
                result = os.popen(find_kill)
                log.info("win kill ret:" + str(result))
            else:
                #mac
                log.info("other platform!!!")
                return 0
        except:
            log.info(traceback.format_exc())
            return 0
        return 1

    def checkPidCmd(self, cmdpid):
        ret = 0
        name = ""
        for tmpObj in self.gAryPids:
            if tmpObj[JTAG_PID_CMD] == cmdpid:
                ret = 1
                name = tmpObj[JTAG_PID_NAME]
                break
        return ret, name, cmdpid

    def checkPidPy(self, pypid):
        ret = 0
        name = ""
        for tmpObj in self.gAryPids:
            if tmpObj[JTAG_PID_PY] == pypid:
                ret = 1
                name = tmpObj["name"]
                break
        return ret, name, pypid

    def findNewCmd(self):
        #获取当前所有的进程
        aryProcess = list(psutil.process_iter())
        tmpPid = -1
        for tmpPro in aryProcess:
            if "cmd.exe" in tmpPro.name():
                tmpPid = tmpPro.pid
                ret, name, pid = self.checkPidCmd(tmpPid)
                if ret <= 0:
                    break
                else:
                    tmpPid = -1
        log.info("findNewCmd() - " + str(tmpPid))
        return tmpPid

    def findNewPy(self):
        #获取当前所有的进程
        aryProcess = list(psutil.process_iter())
        tmpPid = -1
        for tmpPro in aryProcess:
            if "python.exe" in tmpPro.name():
                tmpPid = tmpPro.pid
                ret, name, pid = self.checkPidPy(tmpPid)
                if ret <= 0:
                    break
                else:
                    tmpPid = -1
        log.info("findNewPy() - " + str(tmpPid))
        return tmpPid

    def setPathCmdDir(self, dirpath):
        log.info("setPathCmdDir() - dirpath:" + str(dirpath))
        self.gPathCmdDir = dirpath

    def getAllPidCmd(self):
        #获取当前所有的进程
        aryProcess = list(psutil.process_iter())
        mIndex = 0
        aryPidCmd = []
        for tmpPro in aryProcess:
            if "cmd.exe" in str(tmpPro.name()):
                aryPidCmd.append(tmpPro.pid)
                mIndex += 1
        log.info("getAllPidCmd():" + str(aryPidCmd))
        return aryPidCmd

    def getAllPidPy(self):
        #获取当前所有的进程
        aryProcess = list(psutil.process_iter())
        mIndex = 0
        aryPidPy = []
        for tmpPro in aryProcess:
            if "python.exe" in str(tmpPro.name()):
                aryPidPy.append(tmpPro.pid)
                mIndex += 1
        log.info("getAllPidPy():" + str(aryPidPy))
        return aryPidPy

    def keyboardInput(self, strEnter):
        log.info("输入" + str(strEnter) +"-start!")
        tmInterval = 0.01
        pyautogui.typewrite(message=strEnter,interval=tmInterval)
        tmWait = tmInterval * len(strEnter) + 0.1
        time.sleep(tmWait)
        log.info("输入" + str(strEnter) +"-end!")

    def keyboardEnter(self):
        #回车
        log.info("回车-start!")
        pyautogui.press('enter')
        log.info("回车-end!")

    def checkHasRunningPro(self):
        ret = 0
        if len(self.gAryPids) <= 1:
            #仅有一个Guard
            ret = 0
        else:
            for tmpObj in self.gAryPids:
                if tmpObj[JTAG_PID_NAME] == TAG_GUARD:
                    continue
                else:
                    if tmpObj[JTAG_PID_STATUS] == JTAG_PID_STATUS_RUNNING:
                        ret = 1
                        break
        return ret 

    #执行程序
    #ret=0  执行正常
    #ret=-1 isBusy（可能是正在调用execute或者python正在执行，还在running）
    #ret=-2 不支持的系统，正常要用也是wins，不会来个mac那么傻吧
    def execute(self, path, pyName="Template.py", params=[]):
        ret = 0
        if self.gIsRunningPyFile == 1:
            log.info("executePyFile() find gIsRunningPyFile == 1")
            ret = -1
        elif self.checkHasRunningPro() == 1:
            log.info("executePyFile() find checkHasRunningPro == 1")
            ret = -1
        else:
            self.gIsRunningPyFile = 1
            self.gNowPyName = pyName
            self.gNowPyParams = params
            log.info("openCmd() - pyName:" + str(pyName) + " params:" + str(params))
            if platform.platform().find("Windows") >= 0:
                # log.info("最小化-start!")
                # pyautogui.hotkey('winleft', 'd')
                # log.info("最小化-end!")
                log.info("打开运行-start!")
                pyautogui.hotkey('winleft', 'r')
                log.info("打开运行-end!")
                #输入cmd
                self.keyboardInput("cmd")
                self.keyboardEnter()
                
                #获取新的cmd窗口的pid
                nowPidCmd = -1
                nowPidCmd = self.findNewCmd()

                #特殊处理，为了兼容
                if pyName == "Center.py":
                    path += getPathSeperater() + ".." + getPathSeperater() + ".." + getPathSeperater()

                #输入 python执行命令
                cmdPython = "cd /d " + path + " && python " + pyName + " " + str(nowPidCmd)
                for tmp in params:
                    cmdPython += (" " + str(tmp))
                self.keyboardInput(cmdPython)
                self.keyboardEnter()

                nowPidPy = -1
                nowPidPy = self.findNewPy()

                objPro = {}
                objPro[JTAG_PID_CMD]  = nowPidCmd
                objPro[JTAG_PID_PY]   = nowPidPy
                objPro[JTAG_PID_NAME] = pyName
                objPro[JTAG_PID_PARAMS] = params
                objPro[JTAG_PID_STATUS] = JTAG_PID_STATUS_RUNNING
                objPro[JTAG_PID_TM_START] = int(time.time())
                objPro[JTAG_PID_TM_END] = -1
                if pyName == "Center.py":
                    objPro[JTAG_PID_STATUS] = JTAG_PID_STATUS_BACKGROUND
                self.gAryPids.append(objPro)
                log.info("opencmdend() --- ary:" + str(self.gAryPids))
                ret = 0
            else:
                log.info("not windows, not support!!!!")
                ret = -2
            self.gIsRunningPyFile = 0
        return ret

    #接收httpserver的请求
    def handleRecv(self, path, contentData):
        #log.info("handleRecv() path:" + str(path) + " contentData:" + str(contentData))
        if path == URL_PATH_EXECUTE:
            return self.handleExecute(path, contentData)
        elif path == URL_PATH_CALLBACK:
            return self.handleCallback(path, contentData)
        elif path == URL_PATH_GETALLTASKS:
            return self.handleGetAllTasks(path, contentData)
        elif path == URL_PATH_GETHISTORYTASKS:
            return self.handleGetHistoryTasks(path, contentData)
        elif path == URL_PATH_ABORT:
            return self.handleAbort(path, contentData)
        return self.genRtnMsg(path, JTAG_STATE_ERROR, JTAG_MSG_UNKNOWN)

    def genRtnMsg(self, path, state, msg="", data=""):
        result =  "{"
        result += ("\"" + JTAG_PATH  + "\":\"" + str(path) + "\",")
        result += ("\"" + JTAG_STATE + "\":\"" + str(state) + "\",")
        result += ("\"" + JTAG_MSG   + "\":\"" + str(msg) + "\"")
        if data != "":
            result += ","
            result += ("\"" + JTAG_DATA   + "\":" + str(data))
        result += "}"
        return result

    def checkName(self, name):
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

    def checkParams(self, params):
        result = -1
        if not isinstance(params, list):
            log.info("params is not list!!!")
            result = -1
        else:
            result = 0
        return params, result

    def handleExecute(self, path, contentData):
        #log.info("handleExecute() contentData:" + str(contentData))
        mName = ""
        mParams = []
        try:
            jObj = json.loads(contentData)
            if JTAG_NAME in jObj.keys():
                mName = jObj[JTAG_NAME]
                mName, ret = self.checkName(mName)
                if ret < 0:
                    return self.genRtnMsg(path, JTAG_STATE_ERROR, JTAG_MSG_PARAMSERR)
            else:
                log.info("handleExecute() no name error!!!")
                return self.genRtnMsg(path, JTAG_STATE_ERROR, JTAG_MSG_PARAMSERR)

            #params 非必要
            if JTAG_PARAMS in jObj.keys():
                mParams = jObj[JTAG_PARAMS]
                mParams, ret = self.checkParams(mParams)
                if ret < 0:
                    return self.genRtnMsg(path, JTAG_STATE_ERROR, JTAG_MSG_PARAMSERR)
        except:
            log.info("handleExecute() \n" + traceback.format_exc())
            return self.genRtnMsg(path, JTAG_STATE_ERROR, JTAG_MSG_PARAMSERR)
        log.info("handleExecute() name:" + str(mName) + " params:" + str(mParams))
        ret = self.execute(self.gPathCmdDir, mName, mParams)
        if ret == 0:
            return self.genRtnMsg(path, JTAG_STATE_DONE)
        else:
            return self.genRtnMsg(path, JTAG_STATE_ERROR, JTAG_MSG_BUSY)

    def checkStatus(self, status):
        result = -1
        if not isinstance(status, str):
            log.info("status is not string error!!!")
            result = -1
        elif status == "":
            log.info("status is empty error!!!")
            result = -1
        elif status != JTAG_PID_STATUS_ERROR and status != JTAG_PID_STATUS_BACKGROUND and status != JTAG_PID_STATUS_FINISHED:
            log.info("status not right error!!!")
            result = -1
        else:
            result = 0
        return status, result

    def checkCmd(self, cmd):
        result = -1
        if not isinstance(cmd, int):
            log.info("cmd is not string error!!!")
            result = -1
        elif cmd <= 0:
            log.info("cmd <= 0 error!!!")
            result = -1
        else:
            result = 0
        return cmd, result

    def handleCallback(self, path, contentData):
        mCmd = -1
        mStatus = JTAG_PID_STATUS_FINISHED
        try:
            jObj = json.loads(contentData)
            if JTAG_PID_STATUS in jObj.keys():
                mStatus = jObj[JTAG_PID_STATUS]
                mStatus, ret = self.checkStatus(mStatus)
                if ret < 0:
                    return self.genRtnMsg(path, JTAG_STATE_ERROR, JTAG_MSG_PARAMSERR)
            else:
                log.info("handleExecute() no status error!!!")
                return self.genRtnMsg(path, JTAG_STATE_ERROR, JTAG_MSG_PARAMSERR)

            if JTAG_PID_CMD in jObj.keys():
                mCmd = jObj[JTAG_PID_CMD]
                mCmd, ret = self.checkCmd(mCmd)
                if ret < 0:
                    return self.genRtnMsg(path, JTAG_STATE_ERROR, JTAG_MSG_PARAMSERR)
            else:
                log.info("handleExecute() no cmd error!!!")
                return self.genRtnMsg(path, JTAG_STATE_ERROR, JTAG_MSG_PARAMSERR)
        except:
            log.info("handleExecute() \n" + traceback.format_exc())
            return self.genRtnMsg(path, JTAG_STATE_ERROR, JTAG_MSG_PARAMSERR)
        log.info("handleCallback() cmd:" + str(mCmd) + " status:" + str(mStatus))
        
        if len(self.gAryPids) <= 1:
            return self.genRtnMsg(path, JTAG_STATE_ERROR, JTAG_MSG_PIDNOTFOUND)
        else:
            isHas = 0
            for tmpObj in self.gAryPids:
                tmpCmd = tmpObj[JTAG_PID_CMD]
                if tmpCmd == mCmd:
                    isHas = 1
                    tmpObj[JTAG_PID_STATUS] = mStatus
                    log.info("handleCallback() end --- gAryPids:" + str(self.gAryPids))
                    if mStatus == JTAG_PID_STATUS_ERROR or mStatus == JTAG_PID_STATUS_FINISHED:
                        tmpObj[JTAG_PID_TM_END] = int(time.time())
                    return self.genRtnMsg(path, JTAG_STATE_DONE)
            if isHas == 0:
                return self.genRtnMsg(path, JTAG_STATE_ERROR, JTAG_MSG_PIDNOTFOUND)

    def handleGetAllTasks(self, path, contentData):
        aryCmds = self.getAllPidCmd()
        aryPys = self.getAllPidPy()
        strTasks =  "["
        for tmpObj in self.gAryPids:
            tmpStr = str(tmpObj)
            tmpStr = tmpStr.replace("\'", "\"")
            strTasks += tmpStr
            strTasks += ","
        strTasks = strTasks[:(len(strTasks) - 1)]
        strTasks += "]"
        return self.genRtnMsg(path, JTAG_STATE_DONE, "", strTasks)

    def handleGetHistoryTasks(self, path, contentData):
        strTasks =  "["
        if len(self.gAryPidsHistory) > 0:
            for tmpObj in self.gAryPidsHistory:
                tmpStr = str(tmpObj)
                tmpStr = tmpStr.replace("\'", "\"")
                strTasks += tmpStr
                strTasks += ","
            strTasks = strTasks[:(len(strTasks) - 1)]
        strTasks += "]"
        return self.genRtnMsg(path, JTAG_STATE_DONE, "", strTasks)

    def handleAbort(self, path, contentData):
        mCmd = -1
        try:
            jObj = json.loads(contentData)
            if JTAG_PID_CMD in jObj.keys():
                mCmd = jObj[JTAG_PID_CMD]
                mCmd, ret = self.checkCmd(mCmd)
                if ret < 0:
                    return self.genRtnMsg(path, JTAG_STATE_ERROR, JTAG_MSG_PARAMSERR)
            else:
                log.info("handleAbort() no cmd error!!!")
                return self.genRtnMsg(path, JTAG_STATE_ERROR, JTAG_MSG_PARAMSERR)
        except:
            log.info("handleAbort() \n" + traceback.format_exc())
            return self.genRtnMsg(path, JTAG_STATE_ERROR, JTAG_MSG_PARAMSERR)
        log.info("handleAbort() cmd:" + str(mCmd))
        
        if len(self.gAryPids) <= 1:
            return self.genRtnMsg(path, JTAG_STATE_ERROR, JTAG_MSG_NOTPERMIT)
        else:
            isHas = 0
            for tmpObj in self.gAryPids:
                tmpCmd = tmpObj[JTAG_PID_CMD]
                tmpName = tmpObj[JTAG_PID_NAME]
                if tmpCmd == mCmd and tmpName == TAG_GUARD:
                    return self.genRtnMsg(path, JTAG_STATE_ERROR, JTAG_MSG_NOTPERMIT)
                if tmpCmd == mCmd:
                    isHas = 1
                    tmpObj[JTAG_PID_STATUS] = JTAG_PID_STATUS_ABORT
                    log.info("handleAbort() end --- gAryPids:" + str(self.gAryPids))
                    return self.genRtnMsg(path, JTAG_STATE_DONE)
            if isHas == 0:
                return self.genRtnMsg(path, JTAG_STATE_ERROR, JTAG_MSG_PIDNOTFOUND)

    def newthread_checkPreSec(self):
        while True:
            #log.info("newthread_checkPreSec()")
            time.sleep(1)
            self.updateAryPids()
    
    def getAllAryPids(self):
        aryPidsNow = []
        for tmpObj in self.gAryPids:
            mCmd = tmpObj[JTAG_PID_CMD]
            mPy = tmpObj[JTAG_PID_PY]
            aryPidsNow.append(mCmd)
            aryPidsNow.append(mPy)
        return aryPidsNow

    def updateAryPids(self):
        if not self.gIsRunningPyFile:
            aryCmds = self.getAllPidCmd()
            aryPys = self.getAllPidPy()
            aryPidsNow = self.getAllAryPids()
            aryDontKnowPid = []
            for pid in aryCmds:
                if not pid in aryPidsNow:
                    aryDontKnowPid.append(pid)
            for pid in aryPys:
                if not pid in aryPidsNow:
                    aryDontKnowPid.append(pid)
            if len(aryDontKnowPid) > 0:
                log.info("find dont know pid!!! - " + str(aryDontKnowPid))
                self.killCmds(aryDontKnowPid)

        if len(self.gAryPids) <= 1:
            #无事退朝
            pass
        else:
            isHasKill = 0
            for tmpObj in self.gAryPids:
                if TAG_GUARD == tmpObj[JTAG_PID_NAME]:
                    #过滤Guard
                    continue
                else:
                    mStatus = tmpObj[JTAG_PID_STATUS]
                    mCmd = tmpObj[JTAG_PID_CMD]
                    mPy = tmpObj[JTAG_PID_PY]
                    if mStatus == JTAG_PID_STATUS_FINISHED or mStatus == JTAG_PID_STATUS_ERROR:
                        #有返回的程序，不管是finished的还是error的都直接关闭
                        log.info("find " + mStatus + " pid closing~~~ " + str(tmpObj))
                        time.sleep(1)
                        self.killCmds([mPy, mCmd])
                        self.gAryPids.remove(tmpObj)
                        self.gAryPidsHistory.append(tmpObj)
                        isHasKill = 1
                        
                    elif mStatus == JTAG_PID_STATUS_RUNNING and not ((mPy in aryPys) and (mCmd in aryCmds) ):
                        #程序在跑，当时cmd.exe 和 python.exe 仅存在其中一个，肯定有问题，关吧
                        log.info("find " + mStatus + " pid but py or cmd not exist, closing~~~ " + str(tmpObj))
                        time.sleep(1)
                        self.killCmds([mPy, mCmd])
                        self.gAryPids.remove(tmpObj)
                        tmpObj[JTAG_PID_STATUS] = JTAG_PID_STATUS_ERROR
                        tmpObj[JTAG_PID_TM_END] = int(time.time())
                        self.gAryPidsHistory.append(tmpObj)
                        isHasKill = 1

                    elif mStatus == JTAG_PID_STATUS_ABORT:
                        #发现要强制关闭的程序
                        log.info("find " + mStatus + " pid, closing~~~ " + str(tmpObj))
                        time.sleep(1)
                        self.killCmds([mPy, mCmd])
                        self.gAryPids.remove(tmpObj)
                        tmpObj[JTAG_PID_TM_END] = int(time.time())
                        self.gAryPidsHistory.append(tmpObj)
                        isHasKill = 1

            if isHasKill == 1:
                log.info("updateAryPids() end~ update now:" + str(self.gAryPids))
                log.info("updateAryPids() end~ update history:" + str(self.gAryPidsHistory))

    def __init__(self, params=[]):
        log.info('init GuardCtrl() params:' + str(params))
        aryPidCmd = self.getAllPidCmd()
        if len(params) > 0:
            #需要先关掉这些传过来的cmd再正式启动
            ret = self.killCmds(params[1:])
            time.sleep(1)

        aryPidCmd = self.getAllPidCmd()
        aryPidPy = self.getAllPidPy()
        if len(aryPidCmd) > 1 or len(aryPidPy) > 1:
            #有多余的cmd窗口，要传参重新打开(关掉再运行)
            log.info("start GuardCtrl fail, find other cmd!!! ready restart")
            filePath = os.path.abspath(os.path.join(sys.argv[0], ".."))
            aryPid = []
            for pid in aryPidPy:
                aryPid.append(pid)
            for pid in aryPidCmd:
                aryPid.append(pid)
            self.execute(filePath, TAG_GUARD, aryPid)
        else:
            objCmd = {}
            objCmd[JTAG_PID_CMD]  = aryPidCmd[0]
            objCmd[JTAG_PID_PY] = aryPidPy[0]
            objCmd[JTAG_PID_NAME] = TAG_GUARD
            objCmd[JTAG_PID_PARAMS] = []
            objCmd[JTAG_PID_STATUS] = JTAG_PID_STATUS_BACKGROUND
            objCmd[JTAG_PID_TM_START] = int(time.time())
            objCmd[JTAG_PID_TM_END] = -1
            self.gAryPids.append(objCmd)
            self.markdownIPAddr()
            log.info("start GuardCtrl success~~~~")
            t = threading.Thread(target=self.newthread_checkPreSec)
            t.start()
