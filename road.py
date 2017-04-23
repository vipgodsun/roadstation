#!/usr/bin/python
# -*- coding: utf-8 -*-
#coding:utf-8
import sys
import cx_Oracle
import time  
import datetime
import logging
import os
import os.path
import shutil
import suds
import webbrowser
import json
import datetime
import re
import json
reload(sys)  
sys.setdefaultencoding('utf8')  
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

class StationInfo:
    StationNo = ''
    InsertTime = ''
    ReceiveTime = ''
    RoadStatus = ''
    WaterThick = ''
    SnowThick = ''
    IceTemp = ''
    SaltDesity = ''
    def __init__(self,t1,t2,t3,t4,t5,t6,t7,t8):
        self.StationNo = t1
        self.InsertTime = t2
        self.ReceiveTime = t3
        self.RoadStatus = t4
        self.WaterThick = t5
        self.SnowThick = t6
        self.IceTemp = t7
        self.SaltDesity =t8

def getLineInfo(staTime,line):
    print line
    staList = []
    instime = datetime.datetime.now()
    instime = instime.strftime("%Y-%m-%d %H:%M:%S")
    L = line.strip().decode('gbk').encode('utf-8')
    lineInfo = L.split(' ',2)
    stationNo = lineInfo[0]
    stationName = lineInfo[1]
    obstime = datetime.datetime.strptime(staTime,'%Y%m%d%H%M%S')
    obstime_init = obstime + datetime.timedelta(seconds=-600)
    #print obstime
    #print obstime_init
    stationStatusInfoList = lineInfo[2].split(' ')
    for i in range(len(stationStatusInfoList)):
        stationObstime = obstime_init + datetime.timedelta(seconds=+((i+1)*60))
        stationObstime = stationObstime.strftime("%Y-%m-%d %H:%M:%S")
        status = stationStatusInfoList[i]
        statusInfo = status.split(',')
        roadStatus = statusInfo[0]
        waterThick = statusInfo[1]
        snowThick = statusInfo[2]
        iceTemp = statusInfo[3]
        saltDesity = statusInfo[4]
        sta = StationInfo(stationNo,instime,stationObstime,roadStatus,waterThick,snowThick,iceTemp,saltDesity)
        staList.append(sta)
    return staList

def insertOracle(stalist):
    conn=cx_Oracle.connect()
    cursor=conn.cursor()
    parma = []
    sql = "insert into roaddata values(:StationNo,to_date(:InsertTime,'YYYY-MM-DD HH24:MI:SS'),to_date(:ReceiveTime,'YYYY-MM-DD HH24:MI:SS'),:RoadStatus,:WaterThick,:SnowThick,:IceTemp,:SaltDesity)"
    for a in stalist:
        myClassDict = a.__dict__
        parma.append(myClassDict)
    cursor.executemany(sql,parma)
    cursor.close();  
    conn.commit();  
    conn.close();  

if __name__ == '__main__':
    rootdir = "/src_rac/share_rac/road_aws/temp"
    regex = re.compile("DL_(\d+)_road.txt")
    regexLine = re.compile("^L(.*)")
    stationInfoList = []
    for parent,dirnames,filenames in os.walk(rootdir):
        for filename in filenames:
            if(regex.match(filename)):
                m = regex.match(filename)
                staTime = m.group(1)+"00"
                file_object = open(os.path.join(parent,filename))
                for line in file_object:
                    if(regexLine.match(line)):
                        sta = getLineInfo(staTime,line)
                        stationInfoList.extend(sta)
    insertOracle(stationInfoList)

