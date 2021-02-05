#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding:utf-8
import psutil
import pyautogui
import time, os, threading, platform, json, sys, traceback, logging
import urllib.request

##############
#Logger start
##############
class Logger:

    LOG_DIR_NAME = "logs"

    #最多保留多少个文件，一小时一个文件
    LOG_FILE_COUNT_MAX = 3 * 24

    def getPathSeperater(self):
        if platform.platform().find("Windows") >= 0:
            return "\\"
        else:
            return "/"

    def checkDirs(self):
        pathLogDir = self.getLogDirPath()
        isExists = os.path.exists(pathLogDir)
        if not isExists:
            os.makedirs(pathLogDir) 
            print(pathLogDir + ' 创建成功')

    def getLogDirPath(self):
        pathDirNow = os.path.abspath(os.path.join(sys.argv[0], ".."))
        #同其它的一样吧，统一放在根目录，log放同一个地方 加上个 /../../来返回上一级
        pathLogDir = pathDirNow + self.getPathSeperater() + ".." + self.getPathSeperater() + self.LOG_DIR_NAME
        return pathLogDir

    def closeCheckLog(self):
        self.checkLog = 0

    #检查log文件是否要更新，要更新的话就顺便触发删除多余log文件
    def checkLogFile(self):
        while self.checkLog:
            # print("checkLog~")
            # new_rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
            new_rq = time.strftime('%Y%m%d%H', time.localtime(time.time()))
            self.rq = new_rq
            logname = self.getLogDirPath() + self.getPathSeperater() + self.rq + "_" + str(self.pid) + "_" + str(self.fileName) + '.log'  # 指定输出的日志文件名
            isExists = os.path.exists(logname)
            # 判断结果
            if not isExists:
                print("create_logfile() -- create:" + logname)
                self.logger.removeHandler(self.fh)
                # 给logger添加handler
                self.fh = logging.FileHandler(logname, mode='a', encoding='utf-8')  # 不拆分日志文件，a指追加模式,w为覆盖模式
                self.fh.setLevel(logging.INFO)
                self.fh.setFormatter(self.formatter)
                self.logger.addHandler(self.fh)
                self.deleteLogfile()
            time.sleep(1)

    #只保存3天的log
    def deleteLogfile(self):
        print("deleteLogfile()-----")
        logFileList = os.listdir(self.getLogDirPath())
        logFileList.sort()
        nameContain = "_" + str(self.pid) + "_" + self.fileName + ".log"
        aryLogFile = []
        for i in logFileList:
            if nameContain in i:
                aryLogFile.append(i)
        cntLogFile = len(aryLogFile)
        print("deleteLogfile() --- count:" + str(cntLogFile) + " aryFile:" + str(aryLogFile))
        #判断要删除多少个log文件
        cntRemove = cntLogFile - Logger.LOG_FILE_COUNT_MAX
        if cntRemove < 0:
            cntRemove = 0
        index = 0
        for tmp in aryLogFile:
            if (index + 1) > cntRemove:
                break
            tmpPath = os.path.join(self.getLogDirPath(), tmp)
            try:
                os.remove(tmpPath)
                print("remove log file:" + str(tmp))
            except:
                print("remove log file error !!!")
            index += 1
        
        print("deleteLogfile()----- end end end ")

    def __init__(self, name=__name__, pid = 0):
        print("logger init start~~~")
        # 创建一个loggger
        self.__name = name
        self.fileName = sys.argv[0]
        print("fileName:" + str(self.fileName))
        self.pid = pid
        self.logger = logging.getLogger(self.__name)
        self.logger.setLevel(logging.DEBUG)
        # 定义handler的输出格式
        self.formatter = logging.Formatter('%(asctime)s-%(filename)s-[line:%(lineno)d]' '-%(levelname)s: %(message)s')
        #检查文件夹都在不在
        self.checkDirs()
        # self.rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
        self.rq = time.strftime('%Y%m%d%H', time.localtime(time.time()))
        logname = self.getLogDirPath() + self.getPathSeperater() + self.rq + "_" + str(self.pid) + "_" + str(self.fileName) + '.log'  #指定输出的日志文件名
        self.fh = logging.FileHandler(logname, mode='a', encoding='utf-8')  # 不拆分日志文件，a指追加模式,w为覆盖模式
        self.fh.setLevel(logging.INFO)
        self.fh.setFormatter(self.formatter)
        self.logger.addHandler(self.fh)
        # 创建一个handler，用于将日志输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(self.formatter)
        self.logger.addHandler(ch)
        self.checkLog = 1
        t = threading.Thread(target=self.checkLogFile)
        t.start()

##############
#Logger end
##############

##############
#默认方法 start
##############

def getPathSeperater():
        if platform.platform().find("Windows") >= 0:
            return "\\"
        else:
            return "/"

def GETMYPID():
    print("GETMYPID() - argv:" + str(sys.argv))
    pid = 0
    if len(sys.argv) > 1:
        command = list(sys.argv[1:])
        pid = command[0]
    else:
        print("no pid!!! just testing????")
    return pid

JTAG_PID_STATUS_RUNNING = "running"
JTAG_PID_STATUS_BACKGROUND = "background"
JTAG_PID_STATUS_FINISHED = "finished"
JTAG_PID_STATUS_ERROR = "error"

def RUNEND(status=JTAG_PID_STATUS_FINISHED):
    log.info("RUNEND() status:" + str(status))
    dataStr =  "{"
    dataStr += ("\"cmd\":" + str(PID) + ",")
    dataStr += ("\"status\":\"" + str(status) + "\"")
    dataStr += "}"
    dataStrBytes = dataStr.encode('utf-8')
    url = "http://127.0.0.1:9000/callback"
    f = urllib.request.urlopen(url, dataStrBytes)
    rtnMsg = f.read().decode('utf-8')
    log.info("RUNEND() rtn:" + rtnMsg)
    f.close()

PID = GETMYPID()
LOGGER = Logger(__name__, PID)
log = LOGGER.logger
##############
#默认方法 end
##############

#check 8000 的频率 5s一次
TM_CHECK_FEQ = 5

#90秒等待ue4完全打开，再继续while循环
TM_WAIT_OPENUE4 = 90

#用于检测软件是否正常的请求链接
URL_CHECK = "http://127.0.0.1:8000/check"

#通过URL请求启动UE4
URL_GUARD = "http://127.0.0.1:9000/execute"
URL_OPENUE4_DATA = "{\"name\":\"StartUE4.py\", \"params\":[]}"
URL_KILLUE4_DATA = "{\"name\":\"KillUE4.py\", \"params\":[]}"

class CheckUE4:

    def checkPreTM(self):
        log.info("checkPreTM()")
        while True:
            log.info("checkPreTM() checking~~~")
            #调用/check命令看有没有返回，没有的话就请求打开
            ret = self.checkReqCheck()
            if ret < 0:
                ret = self.handleOpenUE4()
                if ret >= 0:
                    log.info("checkPreTM() opening wait ue4 now wait unitl open 90s~~~")
                    time.sleep(TM_WAIT_OPENUE4)
                    continue
            time.sleep(TM_CHECK_FEQ)

    #通过直接check功能机，看有没有回复，就是挂了
    def checkReqCheck(self):
        ret = 0
        try:
            f = urllib.request.urlopen(URL_CHECK)
            log.info("checkReqCheck() ---------- " + str(f.read().decode("utf-8")))
            f.close()
        except:
            ret = -1
            log.info("checkReqCheck() error!!!")
            log.info(traceback.format_exc())
        log.info("checkReqCheck() ret:" + str(ret))
        return ret
    
    def handleOpenUE4(self):
        ret = 0
        try:
            dataStrBytes = URL_OPENUE4_DATA.encode("utf-8")
            f = urllib.request.urlopen(URL_GUARD, dataStrBytes, timeout=30)
            log.info("handleOpenUE4() ---------- " + str(f.read().decode("utf-8")))
            f.close()
        except:
            ret = -1
            log.info("handleOpenUE4() error!!!")
            log.info(traceback.format_exc())
        log.info("handleOpenUE4() ret:" + str(ret))
        return ret

    def handleKillUE4(self):
        ret = 0
        try:
            dataStrBytes = URL_KILLUE4_DATA.encode("utf-8")
            f = urllib.request.urlopen(URL_GUARD, dataStrBytes, timeout=30)
            log.info("handleKillUE4() ---------- " + str(f.read().decode("utf-8")))
            f.close()
        except:
            ret = -1
            log.info("handleKillUE4() error!!!")
            log.info(traceback.format_exc())
        log.info("handleKillUE4() ret:" + str(ret))
        return ret

    def __init__(self, name=__name__):
        log.info('init CheckUE4()')
        RUNEND(JTAG_PID_STATUS_BACKGROUND)
        log.info('kill ue4 first~~')
        self.handleKillUE4()
        log.info('check ue4 after 5sec~')
        time.sleep(5)
        self.checkPreTM()
        RUNEND(JTAG_PID_STATUS_ERROR)
try:
    tmp = CheckUE4()
except:
    log.info("contain exception")
    log.info(traceback.format_exc())
finally:
    log.info("finally END!!!")
    LOGGER.closeCheckLog()