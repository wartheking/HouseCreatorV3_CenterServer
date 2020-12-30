import logging
import os, time, sys, platform

class Logger:

    LOG_DIR_NAME = "logs"

    #是否写入log文件
    IS_OPEN_LOG_FILE = True
    #是否在串口打印
    IS_OPEN_LOG_TERMINAL = True
    #最多保留多少天文件
    LOG_FILE_COUNT_MAX = 30

    def getPathSeperater(self):
        if platform.platform().find("Windows") >= 0:
            return "\\"
        else:
            return "/"

    def checkDirs(self):
        #log文件夹父级目录看在不在
        pathDirNow = os.path.abspath(os.path.join(sys.argv[0], ".."))
        #创建log文件夹
        pathLogDir = pathDirNow + self.getPathSeperater() + self.LOG_DIR_NAME
        isExists = os.path.exists(pathLogDir)
        if not isExists:
            os.makedirs(pathLogDir) 
            print(pathLogDir + ' 创建成功')

    def getLogDirPath(self):
        return os.path.abspath(os.path.join(sys.argv[0], "..")) + self.getPathSeperater()  +  self.LOG_DIR_NAME

    def __init__(self, name=__name__):
        print("logger init start~~~")
        # 创建一个loggger
        self.__name = name
        self.logger = logging.getLogger(self.__name)
        self.logger.setLevel(logging.DEBUG)

        # 定义handler的输出格式
        self.formatter = logging.Formatter('%(asctime)s-%(filename)s-[line:%(lineno)d]' '-%(levelname)s: %(message)s')

        if Logger.IS_OPEN_LOG_FILE:
            # 创建一个handler，用于写入日志文件
            
            #检查文件夹都在不在
            self.checkDirs()

            self.rq = time.strftime('%Y%m%d', time.localtime(time.time()))
            logname = self.getLogDirPath() + self.getPathSeperater() + self.rq + '.log'  # 指定输出的日志文件名
            # fh = logging.handlers.TimedRotatingFileHandler(logname, when='M', interval=1, backupCount=5,encoding='utf-8')  # 指定utf-8格式编码，避免输出的日志文本乱码
            self.fh = logging.FileHandler(logname, mode='a', encoding='utf-8')  # 不拆分日志文件，a指追加模式,w为覆盖模式
            self.fh.setLevel(logging.INFO)
            self.fh.setFormatter(self.formatter)
            # 给logger添加handler
            self.logger.addHandler(self.fh)
            self.deleteLogfile()

        if Logger.IS_OPEN_LOG_TERMINAL:
            # 创建一个handler，用于将日志输出到控制台
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            ch.setFormatter(self.formatter)
            self.logger.addHandler(ch)

    #检查log文件是否要更新，要更新的话就顺便触发删除多余log文件
    def checkLogFile(self):
        #print("checkLogFile()")
        if Logger.IS_OPEN_LOG_FILE:

            new_rq = time.strftime('%Y%m%d', time.localtime(time.time()))
            #print("--------" + new_rq + "--------" + self.rq)
            #@MARK 每次都check文件存在不存在吧，这样log文件给别人删除了，可以自己重新创建起来
            #if new_rq > self.rq:
            self.rq = new_rq

            logname = self.getLogDirPath() + getPathSeperater() + self.rq + '.log'  # 指定输出的日志文件名
            
            #check文件是否存在，如果不存在就创建，并且调用删除log文件方法，因为可能是隔天了，清一下log

            isExists = os.path.exists(logname)
            # 判断结果
            if not isExists:
                print("create_logfile() -- create:" + logname)
                #检查文件夹都在不在
                self.checkDirs()
                # fh = logging.handlers.TimedRotatingFileHandler(logname, when='M', interval=1, backupCount=5,encoding='utf-8')  # 指定utf-8格式编码，避免输出的日志文本乱码
                #删除旧的handler
                self.logger.removeHandler(self.fh)
                # 给logger添加handler
                self.fh = logging.FileHandler(logname, mode='a', encoding='utf-8')  # 不拆分日志文件，a指追加模式,w为覆盖模式
                self.fh.setLevel(logging.INFO)
                self.fh.setFormatter(self.formatter)
                self.logger.addHandler(self.fh)
                self.deleteLogfile()

    #只保存3天的log
    def deleteLogfile(self):
        print("deleteLogfile()-----")
        index = 0
        curLogFileName = self.rq + ".log"
        #清除一遍文件名比现在的文件名大的文件
        for i in os.listdir(self.getLogDirPath()):
            #print("[" + str(index) + "]:" + str(i) )
            tmpPath = os.path.join(self.getLogDirPath(), i)
            if str(i) > curLogFileName:
                try:
                    os.remove(tmpPath)
                    print("find FILENAME BIGGER FILE remove it!!!")
                except:
                    print("find FILENAME BIGGER FILE remove it!!! error !!!")
            if os.path.isdir(tmpPath):
                try:
                    os.removedirs(tmpPath)
                    print("find DIR remove it!!!")
                except:
                    print("find DIR remove it!!! error!!!")
            index += 1
       
        #再清除一遍多余的文件
        index = 0
        logFileList = os.listdir(self.getLogDirPath())
        logFileList.sort()
        countFiles = len(logFileList)
        for i in logFileList:
            #print("[" + str(index) + "]:" + str(i))
            if index < (countFiles - Logger.LOG_FILE_COUNT_MAX):
                tmpPath = os.path.join(self.getLogDirPath(), i)
                try:
                    os.remove(tmpPath)
                    print("remove log file:" + str(i))
                except:
                    print("remove log file error !!!")
            index += 1
        print("deleteLogfile()----- end end end ")
        # except:
        #     print("deleteLogfile()----- find error!!!")

log = Logger(__name__)

def getLogger():
    return log.logger

def checkLogger():
    return log.checkLogFile()