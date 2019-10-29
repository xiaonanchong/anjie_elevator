import sys
import configparser

import schedule
import time
import datetime

import pymysql

import redis

import json

import keras
from keras.models import load_model
import numpy as np

config_path = sys.argv[1]
config = configparser.ConfigParser()
config.read_file(open(config_path))

re_host = config.get('login_redis', 'host')
re_port = config.get('login_redis', 'port')
re_db = config.get('login_redis', 'database')

sensors_id = json.loads(config.get('sensor', 'ID'))

db_host = config.get('login_mysql', 'host')
db_usr = config.get('login_mysql', 'username')
db_pw = config.get('login_mysql', 'password')
db_name = config.get('login_mysql', 'database')

# not used: ignore
def get_signal(sensor_id):
    conn = redis.Redis(host=re_host, port =re_port)
    signal = conn.get(str(sensors_id))

    signal = np.array([[1 for i in range(2003)] for k in range(14)])  ####
    collect_time = datetime.datetime.now()  #####

    conn.close()
    return signal, collect_time


def record(sql):
    db = pymysql.connect(db_host, db_usr, db_pw, db_name)
    #db = pymysql.connect('192.168.1.190', 'root', 'AAAjjj000', 'kylin')
    cursor = db.cursor()
    try:
        cursor.execute(sql)
        db.commit()
    except:
        db.rollback()

    fault_id = cursor.lastrowid
    db.close()
    return fault_id


def diagnose0(signal):
    # length of signal: [[2003]]
    model = load_model('model1.h5')
    x = np.expand_dims(signal, 2)
    d = np.argmax(model.predict(x))
    return d


def diagnose1(signal):
    fault_type = 0
    return fault_type


def diagnose2_0(fault_signal):
    return "slight"


def diagnose2_1(fault_signal):
    return "medium"


def diagnose2_2(fault_signal):
    return "urgent"


def diag_sensor0(sensor_id, flag_count, flag_fault_id):
    if flag_count > 0:
        print('ignore diagnose!')
        signal, collect_time = get_signal(sensor_id)
        collect_time = collect_time.strftime("%Y-%m-%d %H:%M:%S")
        sql = "insert into tb_fault_data_detail " \
              "(fault_id, collect_time, collect_data)" \
              " values ('%d', '%s', '%s')" % \
              (flag_fault_id, collect_time, signal)
        id = record(sql)
        print('write to tb_fault_data_detail - detail_id: ', id)
    else:
        result, fault_id = diag_sensor(sensor_id)
        if(result):
            flag_count = -1
            flag_fault_id = None
        else:
            flag_count = 20
            flag_fault_id = fault_id

    return flag_count, flag_fault_id



def diag_sensor(sensor_id):

    signal, collect_time = get_signal(sensor_id)

    if diagnose0(signal) == 1:
        result = False
        fault_type = diagnose1(signal)
        if fault_type == 0:
            fault_type = "inner"
            fault_level = diagnose2_0(signal)
            algorithm_id = "model20"

        elif fault_type == 1:
            fault_type = "ball"
            fault_level = diagnose2_1(signal)
            algorithm_id = "model21"

        else:
            fault_type = "outer"
            fault_level = diagnose2_2(signal)
            algorithm_id = "model22"

        # fault_feature
        sql = "insert into tb_fault_feature " \
              "(fault_level, method_type) values " \
              "('%s','predict')" % \
              (fault_level)
        fault_feature_id = record(sql)
        print('write to tb_fault_feature -fault_feature_id: ', fault_feature_id)

        # fault_data
        collect_time_ = collect_time.strftime("%Y-%m-%d %H:%M:%S")
        sql = "insert into tb_fault_data " \
              "(sensor_id, collect_time, collect_data, fault_dev, fault_type, fault_cause, fault_feature_id, " \
              "method_type) " \
              "values ('%d', '%s', '%s', '%d', '%s', 'abrasion', '%d', 'predict')" % \
              (sensor_id, collect_time_, signal, sensor_id, fault_type, fault_feature_id)
        fault_id = record(sql)
        print('write to tb_fault_data - fault_id: ', fault_id)

        # fault_data_detail
        sql = "insert into tb_fault_data_detail " \
              "(fault_id, collect_time, collect_data)" \
              " values ('%d', '%s', '%s')" % \
              (fault_id, collect_time, signal)
        id = record(sql)
        print('write to tb_fault_data_detail - detail_id: ', id)

        for t in range(20):
            collect_time -= datetime.timedelta(seconds=1)
            collect_time_ = collect_time.strftime("%Y-%m-%d %H:%M:%S")

            file_name = collect_time.strftime("%Y-%m-%d")+"_"+str(sensor_id)+".json"
            #file = open(file_name)
            #file.read(10)
            with open(file_name, 'r') as myfile:
                data = myfile.read()
            obj = json.loads(data)
            signal = obj[collect_time_]

            sql = "insert into tb_fault_data_detail " \
              "(fault_id, collect_time, collect_data)" \
              " values ('%d', '%s', '%s')" % \
              (fault_id, collect_time_, signal)
            id = record(sql)
            print('write to tb_fault_data_detail - detail_id: ', id)

    else:
        result = True
        fault_id = -1


    return result, fault_id


def job():
    print('working at ', time.localtime(time.time()).tm_min, ':', time.localtime(time.time()).tm_sec)
    for id in sensors_id:
        flag_count = flag_counts[id]
        flag_fault_id = flag_fault_ids[id]
        new_flag_count, new_flag_fault_id = diag_sensor0(id, flag_count, flag_fault_id)
        flag_counts[id] = new_flag_count
        flag_fault_ids[id] = new_flag_fault_id


########################
flag_counts = {}
flag_fault_ids = {}
for id in sensors_id:
    flag_counts[id] = 0
    flag_fault_ids[id] = None


schedule.every(1).seconds.do(job)
while True:
    schedule.run_pending()
