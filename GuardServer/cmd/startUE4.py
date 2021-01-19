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
        pathDirNow = os.path.abspath(os.path.join(sys.argv[0], ".."))
        pathLogDir = pathDirNow + self.getPathSeperater() + self.LOG_DIR_NAME
        print("pathLogDir --- " + str(pathLogDir))
        isExists = os.path.exists(pathLogDir)
        if not isExists:
            os.makedirs(pathLogDir) 
            print(pathLogDir + ' 创建成功')

    def getLogDirPath(self):
        return os.path.abspath(os.path.join(sys.argv[0], "..")) + self.getPathSeperater()  +  self.LOG_DIR_NAME

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

CFG_FILENAME = "ue4.config"
CFG_TAG_UE4EDITOR = "ue4editor"
CFG_TAG_PROJECT = "project"
CFG_TAG_MAPFILE = "mapfile"

class UE4Ctrl:

    #查找并且关闭UE4
    def findAndKillUE4(self):
        log.info("findAndKillUE4()")
        #获取当前所有的进程
        aryProcess = list(psutil.process_iter())

        if platform.platform().find("Windows") >= 0:
            isHas = False
            find_kill = "taskkill"
            #获取每个进程的名字 和 pid
            for tmpPro in aryProcess:
                # if "chrome" in tmpPro.name().lower():
                #     log.info("find chrome")
                #     isHas = True
                #     find_kill += (" /PID " + str(tmpPro.pid))
                if "UE4Editor" in tmpPro.name():
                    log.info("find chrUE4Editor")
                    isHas = True
                    find_kill += (" /PID " + str(tmpPro.pid))
                if "CrashReportClientEditor" in tmpPro.name():
                    log.info("find CrashReportClientEditor")
                    isHas = True
                    find_kill += (" /PID " + str(tmpPro.pid))
                if "EpicGamesLauncher" in tmpPro.name():
                    log.info("find EpicGamesLauncher")
                    isHas = True
                    find_kill += (" /PID " + str(tmpPro.pid))
                if "EpicWebHelper" in tmpPro.name():
                    log.info("find EpicWebHelper")
                    isHas = True
                    find_kill += (" /PID " + str(tmpPro.pid))
            if isHas:
                find_kill += " -f"
                log.info("win cmd:" + find_kill)
                result = os.popen(find_kill)
                log.info("win kill ret:" + str(result))
        else:
            isHas = False
            find_kill = "kill -9"
            #mac
            for tmpPro in aryProcess:
                if "chrome" in tmpPro.name().lower():
                    isHas = True
                    find_kill += (" " + str(tmpPro.pid))
            if isHas:
                log.info("mac cmd:" + find_kill)
                result = os.popen(find_kill)
                log.info("mac kill ret:" + str(result))
    
    def getUE4Config(self):
        #default
        ue4editor = "D:\\pro_files\\Epic Games\\UE_4.25\\Engine\\Binaries\\Win64\\UE4Editor.exe"
        projet = "D:\\GitHub\\0804\\HouseCreatorV3\\HouseCreatorV3.uproject"
        mapfile = "/Game/Maps/aha.map"
        configPath = os.path.abspath(os.path.join(sys.argv[0], "..")) + getPathSeperater() + CFG_FILENAME
        ret = 1
        try:
            while True:
                file = open(configPath, "r")
                jsonStr = file.read()
                jobj = json.loads(jsonStr)

                if CFG_TAG_UE4EDITOR in jobj.keys():
                    ue4editor = jobj[CFG_TAG_UE4EDITOR]
                    if not isinstance(ue4editor, str):
                        ret = -1
                        log.info("【错误】!!!ue4editor路径配置有问题, 请查看config文件")
                        break
                    else:
                        ret = os.path.exists(ue4editor)
                        if not ret:
                            log.info("【错误】!!!ue4editor路径不存在，请查看config文件:[" + str(ue4editor) + "]")
                            break
                else:
                    ret = -1
                    log.info("【错误】!!!配置文件没有ue4editor路径，请查看config文件!!!")
                    break
                
                if CFG_TAG_PROJECT in jobj.keys():
                    projet = jobj[CFG_TAG_PROJECT]
                    if not isinstance(projet, str):
                        ret = -1
                        log.info("【错误】!!!projet路径配置有问题，请查看config文件")
                        break
                    else:
                        ret = os.path.exists(projet)
                        if not ret:
                            log.info("【错误】!!!project路径不存在，请查看config文件:[" + str(projet) + "]")
                            break
                else:
                    ret = -1
                    log.info("【错误】!!!配置文件没有project路径，请查看config文件!!!")
                    break

                if CFG_TAG_MAPFILE in jobj.keys():
                    mapfile = jobj[CFG_TAG_MAPFILE]
                    if not isinstance(mapfile, str):
                        ret = -1
                        log.info("【错误】!!!mapfile路径配置有问题，请查看config文件")
                        break
                else:
                    ret = -1
                    log.info("【错误】!!!配置文件没有指定mapfile!!!，请查看config文件")
                    break

                break

        except FileNotFoundError:
            log.info("【错误】!!!配置文件没有ue4editor路径!!!，请查看config文件")
            log.info(traceback.format_exc())
            ret = -1
        except:
            log.info("【错误】!!!读取config数据出错，请注意路径是否要转义!!!，请查看config文件")
            log.info(traceback.format_exc())
            ret = -1
        return ret, ue4editor, projet, mapfile

    #windows命令行启动UE4
    def cmdOpenUE4Editor(self):
        if platform.platform().find("Windows") >= 0:
            try:
                ret, ue4editor, project, mapfile = self.getUE4Config()
                if ret < 0:
                    log.info("cmdOpenUE4Editor() config file error!!!")
                else:
                    RUNEND(JTAG_PID_STATUS_BACKGROUND)
                    os.system("\"" + ue4editor + "\" " + project + " " + mapfile)
            except:
                log.info("open software cmd run error!!!")
                log.info(traceback.format_exc())
                RUNEND(JTAG_PID_STATUS_ERROR)
        else:
            log.info("not windows platform open software error!!!")
            RUNEND(JTAG_PID_STATUS_ERROR)
    
    def __init__(self, name=__name__):
        log.info('init UE4Ctrl()')
        self.findAndKillUE4()
        self.cmdOpenUE4Editor()
        log.info('init UE4Ctrl()----------- end!!!')
        RUNEND(JTAG_PID_STATUS_FINISHED)
try:
    tmp = UE4Ctrl()
except:
    log.info("contain exception")
    log.info(traceback.format_exc())
finally:
    log.info("finally END!!!")
    LOGGER.closeCheckLog()