#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# coding:utf-8

import sqlite3
from Logger import *

log = getLogger()

def test():
    conn = sqlite3.connect('./showdoc.db.php')
    cursor = conn.cursor()

    sql = "SELECT * from item"
    values = cursor.execute(sql)
    log.info("values:" + str(values))

    for i in values:
        log.info("0:" + str(i[0]) + " 1:" + str(i[1]) + " 2:" + str(i[2]))
    #关闭游标
    cursor.close()
    #提交事物
    conn.commit()
    #关闭连接
    conn.close()

test()