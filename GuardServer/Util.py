#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding:utf-8
import os, platform
from Logger import *

def getPathSeperater(self):
        if platform.platform().find("Windows") >= 0:
            return "\\"
        else:
            return "/"

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

