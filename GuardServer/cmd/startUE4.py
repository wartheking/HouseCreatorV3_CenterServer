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

STATE_INIT     = "software init"
STATE_STARTING = "software starting"
STATE_RUNNING = "software running"

#用于检测软件是否正常的请求链接
URL_CHECK = "http://127.0.0.1:8000/check"

#每隔多久检测一次程序是否正常，单位秒
TM_CHECK_FEQ = 1

URL_PATH_CHECKSTATE = "/checkstate"
URL_PATH_RESTART = "/restart"

CFG_FILENAME = "ue4.config"
CFG_TAG_UE4EDITOR = "ue4editor"
CFG_TAG_PROJECT = "project"
CFG_TAG_MAPFILE = "mapfile"

class UE4Ctrl:

    #当前状态
    gState = STATE_INIT

    #控制restart 请求一次处理一个
    gIsRestarting = 0

    #查找并且关闭UE4
    def findAndKillUE4(self):
        log.info("findAndKillUE4()")
        #获取当前所有的进程
        aryProcess = list(psutil.process_iter())

        #for test
        # mIndex = 0
        # for tmpPro in aryProcess:
        #     log.info("index:" + str(mIndex) + "-" + str(tmpPro.name()) + " pid:" + str(tmpPro.pid))
        #     mIndex += 1
        # return

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
            ret = -1
        except:
            log.info("【错误】!!!读取config数据出错，请注意路径是否要转义!!!，请查看config文件")
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
                    os.system("\"" + ue4editor + "\" " + project + " " + mapfile)
            except:
                log.info("open software cmd run error!!!")
        else:
            log.info("not windows platform open software error!!!")
    
    #处理打开UE4
    def openUE4Editor(self):
        log.info("openUE4Editor()~~~")
        try:
            self.gState = STATE_STARTING

            #不管怎样，先关闭一次UE4所有东西
            log.info("killUE4-start!")
            self.findAndKillUE4()
            time.sleep(2)
            log.info("killUE4-end!")

            log.info("最小化-start!")
            pyautogui.hotkey('winleft', 'd')
            log.info("最小化-end!")

            #ue4editor - 菜单栏 - window的坐标 113,37
            log.info("打开UE4Editor-start!")
            t = threading.Thread(target=self.cmdOpenUE4Editor)
            t.start()
            log.info("打开UE4Editor-end!")
            time.sleep(60)

            #最大化浏览器
            # 最大化窗口：ALT＋空格＋X
            # 最小化窗口：ALT+空格＋N
            log.info("最大化窗口-start!")
            pyautogui.hotkey('altleft', 'space')
            pyautogui.press('x')
            log.info("最大化窗口-end!")
            time.sleep(1)

            log.info("点击一下菜单-start!")
            pyautogui.click(x=113, y=37, clicks=1, interval=0.0, button='left', duration=0.0, tween=pyautogui.linear)
            log.info("点击一下菜单-end!")
            time.sleep(1)

            #输入python
            log.info("输入python-start!")
            strEnter = "python"
            tmInterval = 0.1
            pyautogui.typewrite(message=strEnter,interval=tmInterval)
            tmWait = tmInterval * len(strEnter) + 1
            log.info("输入python-end!")
            time.sleep(tmWait)

            #按好几下键
            mIndex = 0
            timesDown = 50
            log.info("下键-start!")
            while mIndex < timesDown:
                pyautogui.press('down')
                time.sleep(0.1)
                mIndex += 1
            log.info("下键-end!")
            time.sleep(1)

            #回车,启动python editor
            log.info("回车-start!")
            pyautogui.press('enter')
            log.info("回车-end!")
            time.sleep(20)
            self.gState = STATE_RUNNING
        except:
            log.info("openUE4Editor find error!!!!  it'll restart after 10sec")
            time.sleep(10)
            self.openUE4Editor()


    #起个线程处理打开UE4
    def handleOpenUE4Editor(self):
        log.info("handleOpenUE4Editor()")
        if self.gState == STATE_STARTING:
            log.info("OpenUE4 Process is starting plz wait...")
        else:
            ret, ue4editor, project, mapfile = self.getUE4Config()
            if ret > 0:
                t = threading.Thread(target=self.openUE4Editor)
                t.start()

    #通过直接check功能机，看有没有回复，就是挂了
    def checkReqCheck(self):
        ret = 0
        try:
            f = urllib.request.urlopen(URL_CHECK)
            log.info("checkReqCheck() ---------- " + str(f.read().decode("utf-8")))
            f.close()
        except:
            ret = -1
        log.info("checkReqCheck() ret:" + str(ret))
        return ret
    
    #通过检查后台进程，如果有缺少哪个，就是挂了
    #异常关了, 好像还有后台进程，暂时不能用这个处理
    def checkSoftProcess(self):
        ret = 0
        log.info("checkSoftProcess() ret:" + str(ret))
        return ret

    def checkPreTM(self):
        log.info("checkPreTM()")
        while True:
            log.info("checkPreTM() checking~~~ state:" + str(self.gState))
            time.sleep(TM_CHECK_FEQ)
            if self.gState == STATE_INIT:
                self.handleOpenUE4Editor()
                continue
            if self.gState == STATE_STARTING:
                continue
            if self.gState == STATE_RUNNING:
                #即便是STARTING 也是 会走到RUNNING的状态,所以如果open不成功，也会来到这里check一下，不行就会重新启动
                ret = self.checkReqCheck()
                if ret < 0:
                    self.handleOpenUE4Editor()
                    continue
                ret = self.checkSoftProcess()
                if ret < 0:
                    self.handleOpenUE4Editor()
                    continue

    def handleCheckPreTM(self):
        t = threading.Thread(target=self.checkPreTM)
        t.start()
    
    def handleRestart(self):
        log.info("handleRestart()")
        result = ""
        if self.gState == STATE_STARTING or self.gState == STATE_INIT:
            result = self.genRtnStr(URL_PATH_RESTART, "error", self.gState)
        else:
            log.info("handleRestart() run here????")
            #重置状态让它重新起来
            self.gState = STATE_INIT
            time.sleep(2)
            result = self.genRtnStr(URL_PATH_RESTART, "done", self.gState)
        self.gIsRestarting = 0
        return result

    def genRtnStr(self, name, state, msg):
        return "{\"name\":\""+ name + "\", \"state\":\"" + state + "\", \"msg\":\"" + msg + "\"}"

    def handleCtrl(self, path, params):
        log.info("handleCtrl() path:" + str(path) + " params:" + str(params))
        if path == URL_PATH_CHECKSTATE:
            return self.genRtnStr(path, "done", self.gState)
        elif path == URL_PATH_RESTART:
            #确保restart命令 一次只能处理一个
            while self.gIsRestarting:
                time.sleep(1)
            self.gIsRestarting = 1
            return self.handleRestart()
        return self.genRtnStr(path, "error", "unknown")
    

    def __init__(self, name=__name__):
        log.info('init UE4Ctrl()')
        self.handleCheckPreTM()

try:
    tmp = UE4Ctrl()
    RUNEND(JTAG_PID_STATUS_BACKGROUND)
except:
    log.info("contain exception")
    log.info(traceback.format_exc())
finally:
    log.info("finally END!!!")
    LOGGER.closeCheckLog()