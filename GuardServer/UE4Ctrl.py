import psutil
import pyautogui
import time, os, threading, platform
from ProcessHandler import *
from Logger import *
log = getLogger()

STATE_INIT     = "software init"
STATE_STARTING = "software starting"
STATE_RUNNING = "software running"

#用于检测软件是否正常的请求链接
URL_CHECK = "http://127.0.0.1:8000/check"

#每隔多久检测一次程序是否正常，单位秒
TM_CHECK_FEQ = 1

class UE4Ctrl:

    gState = STATE_INIT

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

    #windows命令行启动UE4
    def cmdOpenUE4Editor(self):
        if platform.platform().find("Windows") >= 0:
            try:
                os.system("\"D:\\pro_files\\Epic Games\\UE_4.25\\Engine\\Binaries\\Win64\\UE4Editor.exe\" D:\\GitHub\\0804\\HouseCreatorV3\\HouseCreatorV3.uproject /Game/Maps/aha.map")
            except:
                log.info("open software cmd run error!!!")
        else:
            log.info("not windows platform open software error!!!")
    
    #处理打开UE4
    def openUE4Editor(self):
        log.info("openUE4Editor()~~~")
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

    #起个线程处理打开UE4
    def handleOpenUE4Editor(self):
        log.info("handleOpenUE4Editor()")
        if self.gState == STATE_STARTING:
            log.info("OpenUE4 Process is starting plz wait...")
            # return json str - error please wait
        else:
            t = threading.Thread(target=self.openUE4Editor)
            t.start()
            # return json str - done, starting

    #通过直接check功能机，看有没有回复，就是挂了
    def checkReqCheck(self):
        ret = 0
        try:
            f = urllib.request.urlopen(URL_CHECK)
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

    def handleCtrl(self, path, params):
        log.info("handleCtrl() path:" + str(path) + " params:" + str(params))

    def __init__(self, name=__name__):
        log.info('init UE4Ctrl()')
        self.handleCheckPreTM()
