# -*- coding: utf-8 -*-
'''
@author: longxin
@version: 1.0
@date:
@changeVersion:
@changeAuthor:
@description:
'''
from model.record import  *
from utils import *
from code_algor import get_offloading_result


def Offloading(workloadlist, datasizelist, formertasklist, nexttaskList, taskidList,
               applicationid, requestdeviceid, algor_type, buget_type):

    # 'vgg 16 test policy'
    offloadingpolicy = [2 for tmp in formertasklist]
    offloadingpolicy = get_offloading_result(len(taskidList), formertasklist, workloadlist, datasizelist, algor_type, buget_type)


    offloadingpolicyid = getRandomId()

    policy = []
    for i in range(0, len(taskidList)):
        tmpdict = {}
        tmpdict['taskid'] = taskidList[i]
        tmpdict['excuteddeviceid'] = offloadingpolicy[i]

        policy.append(tmpdict)

    # 将迁移策略写入文件固化层
    writeoffloadingpolicy(requestdeviceid=requestdeviceid, applicationid=applicationid,
                          offloadingpolicyid=offloadingpolicyid, offloadingpolicy=policy)

    return policy, offloadingpolicyid
def offloading(workloadlist, datasizelist, formertasklist, nexttaskList, taskidList,
               applicationid, requestdeviceid):
    '''
    该调度策略将前面几个任务放在了IoT端进行 其他的任务放在了其他设备进行
    :param workloadlist:
    :param datasizelist:
    :param formertasklist:
    :param nexttaskList:
    :param taskidList:
    :param offloadingdeviceList:
    :param applicationid:
    :param requestdeviceid:
    :return:
    '''
    '根据各项参数进行任务的迁移'
    # 将任务调度结果写入离线文本
    offloadingpolicy = [3 for tmp in formertasklist]



    offloadingpolicyid = getRandomId()


    policy = []
    for i in range(0, len(taskidList)):
        tmpdict = {}
        tmpdict['taskid'] = taskidList[i]
        tmpdict['excuteddeviceid'] = offloadingpolicy[i]

        policy.append(tmpdict)

    # 将迁移策略写入文件固化层
    writeoffloadingpolicy(requestdeviceid=requestdeviceid,applicationid=applicationid, offloadingpolicyid=offloadingpolicyid, offloadingpolicy=policy)

    return policy, offloadingpolicyid

def offloading_all_tocloud(workloadlist, datasizelist, formertasklist, nexttaskList, taskidList,
               applicationid, requestdeviceid, algor_type, budget_type):

    offloadingpolicy = [1 for tmp in formertasklist]

    offloadingpolicyid = getRandomId()

    policy = []
    for i in range(0, len(taskidList)):
        tmpdict = {}
        tmpdict['taskid'] = taskidList[i]
        tmpdict['excuteddeviceid'] = offloadingpolicy[i]

        policy.append(tmpdict)

    # 将迁移策略写入文件固化层
    writeoffloadingpolicy(requestdeviceid=requestdeviceid, applicationid=applicationid,
                          offloadingpolicyid=offloadingpolicyid, offloadingpolicy=policy)

    return policy, offloadingpolicyid
