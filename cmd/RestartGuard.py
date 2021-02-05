#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding:utf-8
import logging
import os, time, sys, platform, traceback, threading, urllib.request, psutil, pyautogui

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

##############
#实例测试 start
##############

#通过URL请求启动UE4
URL_ABORTALL = "http://127.0.0.1:9000/abortAll"

class Template:

    def getPathSeperater(self):
        if platform.platform().find("Windows") >= 0:
            return "\\"
        else:
            return "/"

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

    def handleAbortAll(self):
        ret = 0
        try:
            f = urllib.request.urlopen(URL_ABORTALL, timeout=30)
            log.info("handleAbortAll() ---------- " + str(f.read().decode("utf-8")))
            f.close()
        except:
            ret = -1
            log.info("handleAbortAll() error!!!")
            log.info(traceback.format_exc())
        log.info("handleAbortAll() ret:" + str(ret))
        return ret

    def mainfunc(self):
        try:
            if platform.platform().find("Windows") >= 0:

                #先AbortAll一下
                self.handleAbortAll()
                time.sleep(3)

                #最小化
                log.info("最小化-start!")
                pyautogui.hotkey('winleft', 'd')
                log.info("最小化-end!")

                log.info("打开运行-start!")
                pyautogui.hotkey('winleft', 'r')
                log.info("打开运行-end!")
                #输入cmd
                self.keyboardInput("cmd")
                self.keyboardEnter()
                rootPath = os.path.abspath(os.path.join(sys.argv[0], ".."))
                #特殊处理，为了兼容
                tmpPath = rootPath + self.getPathSeperater() + ".." + self.getPathSeperater()
                pyName = "Guard.py"

                #输入 python执行命令
                cmdPython = "cd /d " + tmpPath + " && python " + pyName
                self.keyboardInput(cmdPython)
                self.keyboardEnter()
        except:
            log.info(traceback.format_exc())

    def __init__(self, name=__name__):
        log.info("python start--->" + str(__file__) + " pid:" + str(PID))
        self.mainfunc()
        #给时间重启Guard，如果重启不了 10秒后也当作完成，接着Guard会自动删掉其它多余的程序
        time.sleep(5)
        #能到这里就是说明没有重启成功，直接返回error
        RUNEND(JTAG_PID_STATUS_ERROR)
        log.info("python end--->" + str(__file__))
try:
    tmp = Template()
except:
    log.info("contain exception")
    log.info(traceback.format_exc())
finally:
    log.info("finally END!!!")
    LOGGER.closeCheckLog()
    