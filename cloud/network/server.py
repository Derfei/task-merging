# -*- coding: utf-8 -*-
'''
@author: longxin
@version: 1.0
@date:
@changeVersion:
@changeAuthor:
@description: 服务器
'''
from flask import Flask
from flask import request
from process.processor import *
from model.record import  *
from Executer.executerDeepLearning import excuterDeepLearning
# from Executer.excuter import ExecuteAgent
# from flask.views import request
from Executer.excuteVgg16 import  excuteVgg16
from Executer.excuteResnet50 import excuteResnet50
from Executer.excuteVgg16boostVgg19 import excuteVgg16boostVgg19
from Executer.excuteDistributedDeepLearning import excuteDistributedDeepLearningAgent
app  = Flask(__name__)
localdeviceid = 3

# set the excute agent for global
print("Begin to load set the execute agent")
# excuteagent = excuterDeepLearning()
excuteagent = excuteDistributedDeepLearningAgent()
# excuteagent = excuteVgg16()
# excuteagent = excuteResnet50()
# excuteagent = excuteVgg16boostVgg19()
print("End to load set the execute agent")
def printOut(msg):
    app.logger.info(msg)
@app.route('/dojob', methods=['POST'])
def dojob():
    import json
    import datetime
    import time
    import numpy as np
    # 提取任务信息
    # app.logger.info("Do Job get data {0} \t the data content is {1}".format(request.get_data(), type(request.get_data())))
    # app.logger.info("After change the data to string, the string is {0}".format(str(request.get_data())))
    data = json.loads(request.get_data().decode(encoding='utf-8'))
    data = data['sendmsgcontent']

    requestdeviceid = data['requestdeviceid']
    applicationid = data['applicationid']
    offloadingpolicyid = data['offloadingpolicyid']
    taskid = data['taskid']
    operationid = data['operationid']
    inputdata = data['inputdata']
    formertasklist = data['formertasklist']
    nexttasklist = data['nexttasklist']
    timecloselist = data['timecostlist']

    # 应用信息中获取该任务的所有的前置任务
    actualformertasklist = gettaskFormertask(requestdeviceid, applicationid, taskid)
    # attention 任务结束时间这里需要进行重新设计 应该设计为任务结束的时间
    # 将任务写入前置任务中
    tmptaskdict = {}
    tmptaskdict['formertaskid'] = formertasklist[0]
    tmptaskdict['inputdata'] = inputdata
    tmptaskdict['timecost'] = timecloselist
    writeformertaskinfo(taskid=taskid, requestdeviceid=requestdeviceid, applicationid=applicationid, offloadingpolicyid=offloadingpolicyid,
                        taskdictlist=[tmptaskdict])
    # app.logger.info("Task {0} 写入前置任务 {1} 到离线文件成功".format(taskid, formertasklist))

    # 确认前置任务数据已经全部完成
    if len(actualformertasklist) != 1:
        formertaskdictlist = getformertaskinfo(taskid, requestdeviceid, applicationid, offloadingpolicyid)
        # app.logger.info("该任务需要等待前置任务{0}完成，现在只有{1}完成".format(actualformertasklist, [tmpFormerTask['formertaskid'] for tmpFormerTask
        #                                                                  in formertaskdictlist]))

        if len(formertaskdictlist) == len(actualformertasklist): # 任务已经全部完成 完成任务
            # 执行任务
            #excuteagent = ExecuteAgent()

            inputdatalist = []  # 整理输入数据按照任务id大小进行排序
            for i in range(len(formertaskdictlist)-1):
                for j in range(len(formertaskdictlist)-i-1):
                    if int(formertaskdictlist[j]['formertaskid']) > int(formertaskdictlist[j+1]['formertaskid']):
                        tmp = formertaskdictlist[j]
                        formertaskdictlist[j] = formertaskdictlist[j+1]
                        formertaskdictlist[j+1] = tmp

            for tmp in formertaskdictlist:
                # inputdatalist.append(tmp['inputdata'][0])
                inputdatalist.append(tmp['inputdata'])

            # 合并任务完成时间
            tmpTimeCost = [tmpTime for tmpTime in timecloselist]
            for taskindex in range(len(timecloselist)):
                for tmpformertask in formertaskdictlist:
                    if int(tmpformertask['timecost'][taskindex][0]) != 0:
                        tmpTimeCost[taskindex] = tmpformertask['timecost'][taskindex]
                        break
            timecloselist = tmpTimeCost
            timecloselist[int(taskid)][0] = time.time()
            print("operation id is: {0} and shape of input is {1}".format(operationid, np.shape(inputdatalist)))
            output = excuteagent.excute(operationid, inputdatalist)
            timecloselist[int(taskid)][1] = time.time()
            # app.logger.info("任务{0}已经完成 nexttasklist 为: {1} 输出为 {2}".format(taskid, nexttasklist, np.shape(output)))

            # 判断是不是最后一个任务
            if len(nexttasklist) == 1 and int(nexttasklist[0]) == -1:
                tmpnewtask = produce_newtask(taskid, timecloselist, taskid, output, requestdeviceid, applicationid,
                                             offloadingpolicyid)
                sendFinal(requestdeviceid, localdeviceid, tmpnewtask)

            else:
                # 生成新的任务
                for tmp in nexttasklist:
                    # app.logger.info("开始生成新的任务{0}".format(tmp))
                    tmpnewtask = produce_newtask(taskid, timecloselist, tmp, output, requestdeviceid, applicationid,
                                                 offloadingpolicyid)
                    # app.logger.info("生成新的任务为{0}".format(tmpnewtask.todict()))
                    SendTask(requestdeviceid, applicationid, offloadingpolicyid, tmp,
                             localdeviceid, tmpnewtask)  # 发送任务到另外的服务器

        else: # 任务还没有全部完成
            # app.logger.info("任务{0}进入等待中".format(taskid))
            pass
    else: # 任务已经全部完成
        formertaskdictlist = getformertaskinfo(taskid, requestdeviceid, applicationid, offloadingpolicyid)
        # 执行任务
        #excuteagent = ExecuteAgent()

        inputdatalist = []  # 整理输入数据按照任务id大小进行排序
        for i in range(len(formertaskdictlist) - 1):
            for j in range(len(formertaskdictlist) - i - 1):
                if int(formertaskdictlist[j]['formertaskid']) > int(formertaskdictlist[j + 1]['formertaskid']):
                    tmp = formertaskdictlist[j]
                    formertaskdictlist[j] = formertaskdictlist[j + 1]
                    formertaskdictlist[j + 1] = tmp

        for tmp in formertaskdictlist:
            # inputdatalist.append(tmp['inputdata'][0])
            inputdatalist.append(tmp['inputdata'])
        # 合并任务完成时间
        tmpTimeCost = [tmpTime for tmpTime in timecloselist]
        for taskindex in range(len(timecloselist)):
            for tmpformertask in formertaskdictlist:
                if int(tmpformertask['timecost'][taskindex][0]) != 0:
                    tmpTimeCost[taskindex] = tmpformertask['timecost'][taskindex]
                    break
        timecloselist = tmpTimeCost
        timecloselist[int(taskid)][0] = time.time()
        # app.logger.info("operation id is: {0}".format(operationid))
        if len(formertaskdictlist) == 1:
            inputdatalist = inputdatalist[0]
        print("operation id is: {0} and shape of input is {1}".format(operationid, np.shape(inputdatalist)))
        output = excuteagent.excute(operationid, inputdatalist)
        timecloselist[int(taskid)][1] = time.time()
        # app.logger.info("任务{0}已经完成 nexttasklist 为: {1} 输出为 {2}".format(taskid, nexttasklist, np.shape(output)))

        # 判断是不是最后一个任务
        if len(nexttasklist) == 1 and int(nexttasklist[0]) == -1:
            tmpnewtask = produce_newtask(taskid, timecloselist, taskid, output, requestdeviceid, applicationid,
                                         offloadingpolicyid)
            sendFinal(requestdeviceid, localdeviceid, tmpnewtask)
        else:
            # 生成新的任务
            for tmp in nexttasklist:
                tmpnewtask = produce_newtask(taskid, timecloselist, tmp, output, requestdeviceid, applicationid,
                                             offloadingpolicyid)
                # 根据id获取应该执行的设备
                # 根据id获取应该执行的设备
                reqUrl = SendTask(requestdeviceid, applicationid, offloadingpolicyid, tmp, localdeviceid,
                                  tmpnewtask)  # 发送任务到另外的服务器

                # app.logger.info("从 设备 {0} 发送任务 {1} 任务内容为 {2} 到设备{3} 执行完任务 {4}".format(localdeviceid, tmp,
                #                                                                       tmpnewtask.todict(), reqUrl,
                #                                                                       taskid))

    return 'OK'



@app.route('/getOffloadingPolicy', methods=['POST'])
def getoffloadingpolicy():
    import json
    # 从数据请求中获取 应用设备id 应用id 调度策略id
    tmpoffloadingpolicydict = json.loads(request.get_data().decode('utf-8'))
    tmpoffloadingpolicydict = tmpoffloadingpolicydict['sendmsgcontent']
    applicationdeviceid = tmpoffloadingpolicydict['requestdeviceid']
    applicationid = tmpoffloadingpolicydict['applicationid']
    offloadingpolicyid = tmpoffloadingpolicydict['offloadingpolicyid']

    # 从离线数据中获取迁移策略
    offloadingpolicylist = getoffloadingpolicyinfo(taskid=-1, requestdeviceid=applicationdeviceid, applicationid=applicationid,
                                               offloadingpolicyid=offloadingpolicyid)
    offloadingpolicylist = [tmp.todict() for tmp in offloadingpolicylist]

    # 返回offloading策略
    return json.dumps(offloadingpolicylist, cls=MyEncoder)


@app.route('/getInternetInfo', methods=['POST'])
def getinternetinfo():
    import json
    # 从离线数据读取网络信息
    networkinfolist = getnetworkinfo(-1)

    # 返回信息
    networkinfolist = [tmp.todict() for tmp in networkinfolist]

    return json.dumps(networkinfolist, cls=MyEncoder)

@app.route('/updateInternetInfo', methods=['POST'])
def updateinternetinfo():
    import json
    # 读取网络信息
    data  = json.loads(request.get_data())
    data = data['sendmsgcontent']

    # 将网络信息写入到离线文件当中
    writenetworkinfo(data)

    return "更新成功"


@app.route('/getApplicationInfo', methods=['POST'])
def getApplicationInfo():
    import json

    data = json.loads(request.get_data().decode(encoding='utf-8'))

    # 获取本设备的设备编号
    senddeviceid = data['senddeviceid']

    # 获取需要获取的应用id
    tmpapplication = data['sendmsgcontent']
    applicationid = tmpapplication['applicationid']

    # 处理器进行处理 读取离线数据 转成json格式 进行发送
    applicationdict = getapplicationdict(senddeviceid, applicationid)

    applicationobject = application.initfromdict(applicationdict)

    return applicationobject.tostring()


@app.route('/getFinalResult', methods=['POST'])
def getFinalResult():
    import json

    data = json.loads(request.get_data())
    data = data['sendmsgcontent']

    tmpapplicationid = data['applicationid']
    tmprequestdeviceid = data['requestdeviceid']
    tmpoffloadingpolicyid = data['offloadingpolicyid']
    tmpinputdata = data['inputdata']
    tmptimecostlist = data['timecostlist']

    # app.logger.info("应用编号{0}\t请求设备号{1}\t调度号{2}\t返回结果为{3}\t时间花费为{4} 完成任务".format(tmpapplicationid, tmprequestdeviceid,
    #                                                              tmpoffloadingpolicyid, tmpinputdata,tmptimecostlist))
if __name__ == "__main__":
    print("Begin the app run")
    app.run(host='0.0.0.0', port=8002, debug=True, threaded=True)