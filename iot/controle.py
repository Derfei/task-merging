# -*- coding: utf-8 -*-
'''
@author: longxin
@version: 1.0
@date: 2018-11-18
@changeVersion:
@changeAuthor:
@description: 数据固化层
'''
from utils import *
from model.models import *
from model.record import *
from offloading import *
from network.client import *

local_deviceid = 1
def image_to_embedding(image_path):
    import  cv2
    import numpy as np


    #image = cv2.resize(image, (96, 96), interpolation=cv2.INTER_AREA)
    image = cv2.imread(image_path)
    image = cv2.resize(image, (96, 96))
    img = image[...,::-1]
    img = np.around(np.transpose(img, (0,1,2))/255.0, decimals=12)
    x_train = np.array([img])
    return x_train
def controle_deep_learning(algor_type=1, budget_type=1, double_type=1):
    import numpy as np
    import time

    requestdeviceid = local_deviceid
    applicationid = getRandomId()
    taskidlist = [i for i in range(33)]
    formertasklist = [[-1], [0], [0], [0], [0], [1, 2, 3, 4], [5], [5], [5], [5],
                      [6, 7, 8, 9], [10], [10], [10], [11, 12, 13], [14], [14],
                      [14], [14], [15, 16, 17, 18], [19], [19], [19], [20, 21, 22],
                      [23], [23], [23], [24, 25, 26], [27], [27], [27], [28, 29, 30],
                      [31]]
    nexttasklist = [[1, 2, 3, 4], [5], [5], [5], [5],[6, 7, 8, 9], [10], [10],
                    [10], [10], [11, 12, 13], [14], [14], [14], [15, 16, 17, 18],
                    [19], [19], [19], [19], [20, 21, 22], [23], [23], [23],
                    [24, 25, 26],[27], [27], [27], [28, 29, 30], [31], [31], [31],
                    [32], [-1]]
    nexttasklist[-1][0] = -1
    operationidlist = [i for i in range(33)]

    output_time = [1547473814.4659445, 1547473814.546958, 1547473814.6286523, 1547473814.7011578, 1547473814.7689452,
                  1547473814.7926652, 1547473814.8418512, 1547473814.9159176, 1547473814.986788, 1547473815.0573804,
                  1547473815.094309, 1547473815.1545618, 1547473815.2249172, 1547473815.288134, 1547473815.3123832,
                  1547473815.3638773, 1547473815.4306982, 1547473815.4762897, 1547473815.522738, 1547473815.5532544,
                  1547473815.5950744, 1547473815.6398182, 1547473815.6777437, 1547473815.6886353, 1547473815.7064416,
                  1547473815.7321815, 1547473815.7560656, 1547473815.7691329, 1547473815.7826364, 1547473815.8065357,
                  1547473815.8272645, 1547473815.8348973, 1547473815.8464653, 1547473807.4078662]

    workload = []
    for i in range(33):
        if i == 0:
            workload.append(output_time[0]-output_time[-1])
        else:
            workload.append(output_time[i] - max([output_time[tmp] for tmp in formertasklist[i]]))

    datasize = [96 * 96 * 3, 12 * 12 * 192, 12 * 12 * 192, 12 * 12 * 192, 12 * 12 * 192,
                (12 * 12 * 128 + 12 * 12 * 32 + 12 * 12 * 32 + 12 * 12 * 64), 12 * 12 * 256, 12 * 12 * 256,
                            12*12*256, 12*12*256, (12*12*128+12*12*64+12*12*64+12*12*64), 12*12*320, 12*12*320, 12*12*320, (6*6*256+6*6*64+6*6*320),
                            6*6*640, 6*6*640, 6*6*640, 6*6*640, (6*6*192+6*6*64+6*6*128+6*6*256), 6*6*640, 6*6*640, 6*6*640, (3*3*256+3*3*128+3*3*640),
                            3*3*1024, 3*3*1024, 3*3*1024, (3*3*384+3*3*96+3*3*256), 3*3*736, 3*3*736, 3*3*736, (3*3*384+3*3*96+3*3*256), 3*3*736]

    tmpapplication = application(requestdeviceid, applicationid, taskidlist, formertasklist,
                                 nexttasklist, operationidlist)
    writeapplication(tmpapplication)  # 将应用写入离线文档中
    workload = [tmp*double_type for tmp in workload]
    datasize = [tmp*double_type for tmp in datasize]

    # 使用调度算法进行调度 调度算法会将调度结果写入离线文件当中
    offloadingPolicy, offloadingpolicyid = offloading_all_tocloud(workload, datasize, formertasklist, nexttasklist, taskidlist,
                                                      applicationid,
                                                      requestdeviceid, algor_type, budget_type)

    # 生成任务
    input = image_to_embedding(r'longxin.jpg')
    input = np.array([input[0] for i in range(double_type)])
    print("the shape of input is: ", np.array(input).shape)
    time_cost_list = [[0, 0] for i in range(len(taskidlist) + 1)]
    time_cost_list[-1][0] = time.time()
    time_cost_list[-1][1] = time_cost_list[-1][0]
    tmptask = task(requestdeviceid, applicationid, offloadingpolicyid, 0, 0, np.array(input), [-1], [1, 2, 3, 4],
                   time_cost_list)

    # 发送任务
    # sendTask(objectdeviceid=firstdevice, localdeviceid=local_deviceid, newtask=tmptask)
    sendTask(local_deviceid, applicationid, offloadingpolicyid, 0, local_deviceid, tmptask)

    print("发送第一个任务成功 应用编号{0} 请求设备编号{1} 调度策略编号{2}".format(
        applicationid, requestdeviceid, offloadingpolicyid
    ))

def controle():
    '主控器器'
    # 新建应用写入文件当中
    requestdeviceid = local_deviceid
    applicationid = getRandomId()
    taskidlist = [0, 1, 2, 3, 4, 5, 6]
    formertasklist = [[-1], [0], [0], [1,2], [3], [2,3], [4,5]]
    nexttasklist = [[1,2], [3], [3,5], [4,5], [6], [6], [-1]]
    operationidlist = [i for i in range(0, 7)]

    tmpapplication = application(requestdeviceid, applicationid, taskidlist, formertasklist,
                                 nexttasklist, operationidlist)

    writeapplication(tmpapplication) # 将应用写入离线文档中
    # 使用调度算法进行调度 调度算法会将调度结果写入离线文件当中
    offloadingPolicy, offloadingpolicyid = offloading(taskidlist, taskidlist, formertasklist, nexttasklist, taskidlist,  applicationid,
               requestdeviceid)

    # 生成任务
    tmptask = task(requestdeviceid, applicationid, offloadingpolicyid, 0, 0, [1], [-1], [1,2],
                   [0 for i in range(0, len(taskidlist))])
    # 发送任务
    # sendTask(objectdeviceid=firstdevice, localdeviceid=local_deviceid, newtask=tmptask)
    sendTask(local_deviceid, applicationid, offloadingpolicyid, 0, local_deviceid, tmptask)

    print("发送第一个任务成功 应用编号{0} 请求设备编号{1} 调度策略编号{2}".format(
        applicationid, requestdeviceid, offloadingpolicyid
    ))


def control_vgg16(algor_type=1, budget_type=1):
    import numpy as np
    import time
    from keras.preprocessing import  image
    from keras.applications.imagenet_utils import preprocess_input

    requestdeviceid = local_deviceid
    applicationid = getRandomId()
    taskidlist = [i for i in range(6)]
    formertasklist = [[i-1] for i in range(6)]
    nexttasklist = [[i+1] for i in range(6)]
    nexttasklist[-1][0] = -1
    operationidlist = [i for i in range(6)]

    'set the workload size and data size'
    output_time = [1547468409.1495132, 1547468410.7728095, 1547468411.5976126, 1547468412.0235333, 1547468412.171921, 1547468412.2387455, 1547468407.1385837]
    workload = []
    for i in range(len(taskidlist)):
        if i == 0:
            workload.append(output_time[0]-output_time[-1])
        else:
            workload.append(output_time[i]-output_time[i-1])

    datasize = [224*224*3, 224*224*3, 112*112*64, 56*56*128, 28*28*256, 14*14*512,
          7*7*512]



    tmpapplication = application(requestdeviceid, applicationid, taskidlist, formertasklist,
                                 nexttasklist, operationidlist)
    writeapplication(tmpapplication)  # 将应用写入离线文档中

    # 使用调度算法进行调度 调度算法会将调度结果写入离线文件当中
    offloadingPolicy, offloadingpolicyid = Offloading(workload, datasize, formertasklist, nexttasklist, taskidlist,
                                                      applicationid,
                                                      requestdeviceid, algor_type, budget_type)

    # 生成任务
    img_path = 'elephant.jpg'
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    # x = np.array([x, x])
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    print("the shape of input is: ", np.array(x).shape)
    time_cost_list = [[0, 0] for i in range(len(taskidlist) + 1)]
    time_cost_list[-1][0] = time.time()
    time_cost_list[-1][1] = time_cost_list[-1][0]
    tmptask = task(requestdeviceid, applicationid, offloadingpolicyid, 0, 0, np.array(x), [-1], [1],
                   time_cost_list)

    # 发送任务
    # sendTask(objectdeviceid=firstdevice, localdeviceid=local_deviceid, newtask=tmptask)
    sendTask(local_deviceid, applicationid, offloadingpolicyid, 0, local_deviceid, tmptask)

    print("发送第一个任务成功 应用编号{0} 请求设备编号{1} 调度策略编号{2}".format(
        applicationid, requestdeviceid, offloadingpolicyid
    ))

def control_resnet50(algor_type=1, budget_type=1):
    import numpy as np
    import time
    from keras.preprocessing import image
    from keras.applications.imagenet_utils import preprocess_input

    requestdeviceid = local_deviceid
    applicationid = getRandomId()
    taskidlist = [i for i in range(38)]
    formertasklist = [[-1], [0], [0], [1, 2], [3], [3, 4], [5], [5, 6], [7], [7], [8, 9], [10], [10, 11],
                      [12], [12, 13], [14], [14, 15], [16], [16], [17, 18], [19], [19, 20], [21], [21, 22],
                      [23], [23, 24], [25], [25, 26], [27], [27, 28], [29], [29], [30, 31], [32], [32, 33],
                      [34], [34, 35], [36]]
    nexttasklist = [[1, 2], [3], [3], [4, 5], [5], [6,7], [7], [8,9], [10], [10], [11, 12], [12], [13, 14], [14],
                    [15, 16], [16], [17, 18], [19], [19], [20, 21], [21], [22, 23], [23], [24, 25], [25], [26, 27],
                    [27], [28, 29], [29], [30, 31], [32], [32], [33, 34], [34], [35, 36], [36], [37], [-1]]
    operationidlist = [i for i in range(38)]

    tmpapplication = application(requestdeviceid, applicationid, taskidlist, formertasklist,
                                 nexttasklist, operationidlist)
    writeapplication(tmpapplication)  # 将应用写入离线文档中

    output_time = [1547476899.3399606, 1547476899.7438064, 1547476901.792391, 1547476904.261936, 1547476905.6301556,
                   1547476909.052161, 1547476910.4211972, 1547476913.9923651, 1547476915.3374557, 1547476917.6072588,
                   1547476918.7249434, 1547476919.4683926, 1547476923.599801, 1547476930.3080227, 1547476936.5050642,
                   1547476937.7935014, 1547476941.8549275, 1547476945.8670638, 1547476949.7265143, 1547476950.324865,
                   1547476951.2173529, 1547476956.6322582, 1547476957.110144, 1547476958.6434438, 1547476959.0647304,
                   1547476960.6138852, 1547476961.2274103, 1547476962.9769964, 1547476963.4895194, 1547476964.7773721,
                   1547476965.6521354, 1547476966.621212, 1547476967.1023922, 1547476967.5535617, 1547476968.1555667,
                   1547476968.455434, 1547476969.264589, 1547476969.6297235, 1547476897.498089]

    workload = []
    for i in range(38):
        if i == 0:
            workload.append(output_time[0]-output_time[-1])
        else:
            workload.append(output_time[i] - max([output_time[tmp] for tmp in formertasklist[i]]))

    datasize = [224 * 224 * 3, 55 * 55 * 64, 55 * 55 * 64, 55 * 55 * 256 * 2, 55 * 55 * 256, 55 * 55 * 256 * 2,
                55 * 55 * 256, 55 * 55 * 256 * 2,
                55 * 55 * 256, 55 * 55 * 256, 28 * 28 * 512 * 2, 28 * 28 * 512, 28 * 28 * 512 * 2, 28 * 28 * 512,
                28 * 28 * 512 * 2, 28 * 28 * 512, 28 * 28 * 512 * 2,
                28 * 28 * 512, 28 * 28 * 512, 14 * 14 * 1024 * 2, 14 * 14 * 1024, 14 * 14 * 1024 * 2, 14 * 14 * 1024,
                14 * 14 * 1024 * 2, 14 * 14 * 1024, 14 * 14 * 1024 * 2,
                14 * 14 * 1024, 14 * 14 * 1024 * 2, 14 * 14 * 1024, 14 * 14 * 1024,7 * 7 * 2048 * 2,
                7 * 7 * 2048, 7 * 7 * 2048 * 2, 7 * 7 * 2048, 7 * 7 * 2048*2, 7 * 7 * 2048, 7 * 7 * 2048*2, 7 * 7 * 2048]

    # 使用调度算法进行调度 调度算法会将调度结果写入离线文件当中
    offloadingPolicy, offloadingpolicyid = Offloading(workload, datasize, formertasklist, nexttasklist, taskidlist,
                                                      applicationid,
                                                      requestdeviceid, algor_type, budget_type)

    # 生成任务
    img_path = 'elephant.jpg'
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    # x = np.expand_dims(x, axis=0)
    # x = np.array([x, x])
    x = np.expand_dims(x, axis=0)
    x = preprocess_input(x)
    print("the shape of input is: ", np.array(x).shape)
    time_cost_list = [[0, 0] for i in range(len(taskidlist) + 1)]
    time_cost_list[-1][0] = time.time()
    time_cost_list[-1][1] = time_cost_list[-1][0]
    tmptask = task(requestdeviceid, applicationid, offloadingpolicyid, 0, 0, np.array(x), [-1], [1, 2],
                   time_cost_list)

    # 发送任务
    # sendTask(objectdeviceid=firstdevice, localdeviceid=local_deviceid, newtask=tmptask)
    sendTask(local_deviceid, applicationid, offloadingpolicyid, 0, local_deviceid, tmptask)

    print("发送第一个任务成功 应用编号{0} 请求设备编号{1} 调度策略编号{2}".format(
        applicationid, requestdeviceid, offloadingpolicyid
    ))

def control_vgg16boostvgg19(algor_type=1, buget_type=1, input_double=1):
    import numpy as np
    import time
    from keras.preprocessing import image
    from keras.applications.imagenet_utils import preprocess_input

    requestdeviceid = local_deviceid
    applicationid = getRandomId()
    taskidlist = [i for i in range(14)]
    formertasklist = [[-1], [0], [0], [1], [2], [3], [4], [5], [6], [7], [8], [9], [10], [11, 12]]
    nexttasklist = [[1,2], [3], [4], [5], [6], [7], [8], [9], [10], [11], [12], [13], [13], [-1]]
    nexttasklist[-1][0] = -1
    operationidlist = [i for i in range(14)]

    tmpapplication = application(requestdeviceid, applicationid, taskidlist, formertasklist,
                                 nexttasklist, operationidlist)
    writeapplication(tmpapplication)  # 将应用写入离线文档中

    datasize = [224*224*3, 224*224*3, 224*224*3, 112*112*64, 112*112*64, 56*56*128, 56*56*128,28*28*256, 28*28*256,
                14*14*512, 14*14*512, 7*7*512, 7*7*512, 2000]
    output_time = [1547478369.6544778, 1547478370.1986272, 1547478373.8009465, 1547478371.4987335, 1547478375.4653232,
                   1547478372.4462256, 1547478376.3034225, 1547478373.0028286, 1547478376.7409902, 1547478373.2289195,
                   1547478376.8916638, 1547478373.3098044, 1547478376.9549108, 1547478376.9635487, 1547478367.86583]
    workload = []
    for i in range(14):
        if i == 0:
            workload.append(output_time[0]-output_time[-1])
        else:
            workload.append(output_time[i] - max([output_time[tmp] for tmp in formertasklist[i]]))

    # 使用调度算法进行调度 调度算法会将调度结果写入离线文件当中
    workload = [tmp*input_double for tmp in workload]
    datasize = [tmp*input_double for tmp in datasize]
    offloadingPolicy, offloadingpolicyid = Offloading(workload, datasize, formertasklist, nexttasklist, taskidlist,
                                                      applicationid,
                                                      requestdeviceid,algor_type, buget_type)

    # 生成任务
    img_path = 'elephant.jpg'
    img = image.load_img(img_path, target_size=(224, 224))
    x = image.img_to_array(img)
    # x = np.expand_dims(x, axis=0)
    x = np.array([x for i in range(input_double)])
    x = preprocess_input(x)
    print("the shape of input is: ", np.array(x).shape)
    time_cost_list = [[0, 0] for i in range(len(taskidlist) + 1)]
    time_cost_list[-1][0] = time.time()
    time_cost_list[-1][1] = time_cost_list[-1][0]
    tmptask = task(requestdeviceid, applicationid, offloadingpolicyid, 0, 0, np.array(x), [-1], [1, 2],
                   time_cost_list)

    # 发送任务
    # sendTask(objectdeviceid=firstdevice, localdeviceid=local_deviceid, newtask=tmptask)
    sendTask(local_deviceid, applicationid, offloadingpolicyid, 0, local_deviceid, tmptask)

    print("发送第一个任务成功 应用编号{0} 请求设备编号{1} 调度策略编号{2}".format(
        applicationid, requestdeviceid, offloadingpolicyid
    ))

if __name__ == "__main__":
    # controle()
    # for i in range(6):
    #     controle_deep_learning(3, 1, i+1)  # more true
    #     controle_deep_learning(3, 2, i+1)
    #     controle_deep_learning(3, 3, i+1)
    controle_deep_learning(3, 1, 5)
    # controle_deep_learning(3, 2)
    # controle_deep_learning(3, 3)
    # controle_deep_learning(3)
    # control_vgg16(1) # more True signle True
    # control_vgg16(algor_type=1, budget_type=1)
    # control_vgg16(algor_type=1, budget_type=2)
    # control_vgg16(algor_type=1, budget_type=3)
    # control_vgg16(algor_type=3, budget_type=1)
    # control_vgg16(algor_type=3, budget_type=2)
    # control_vgg16(algor_type=3, budget_type=3)

    # control_vgg16(3)

    # control_resnet50(1, 1) # more True
    # control_resnet50(1, 2)
    # control_resnet50(1, 3)
    #
    # control_resnet50(3, 1)
    # control_resnet50(3, 2)
    # control_resnet50(3, 3)
    # control_vgg16boostvgg19(1, 1)
    # control_vgg16boostvgg19(1, 2)
    # control_vgg16boostvgg19(1, 3)
    # # control_vgg16boostvgg19(2)
    # control_vgg16boostvgg19(3, 1)
    # control_vgg16boostvgg19(3, 2)
    # control_vgg16boostvgg19(3, 3)

    # '分析每个任务花费的时间'
    # output_time = [1547468409.1495132, 1547468410.7728095, 1547468411.5976126, 1547468412.0235333, 1547468412.171921, 1547468412.2387455, 1547468407.1385837]
    # workload = [output_time[i]-output_time[-1] for i in range(len(output_time)-1)]
    # print(workload)
