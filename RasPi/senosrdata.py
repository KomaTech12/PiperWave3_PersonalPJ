#! /usr/bin/python3

import RPi.GPIO as GPIO
import time
import datetime
import requests
import json
import redis

# Define GPIO Pin
Trigger = 16
Echo = 18

# Connect RedisCloud on PWS
r = redis.Redis(host='XXX', port='XXX', password='XXX')

# Initialize List
r.rpush('point0', 'NoData', 'NoData')
r.rpush('point10', 'NoData', 'NoData')
r.rpush('point20', 'NoData', 'NoData')
r.rpush('point30', 'NoData', 'NoData')
r.rpush('point40', 'NoData', 'NoData')
r.rpush('point50', 'NoData', 'NoData')

# Calculate distance
def checkdist():
    GPIO.output(Trigger, GPIO.HIGH)
    time.sleep(0.000015)
    GPIO.output(Trigger, GPIO.LOW)
    while not GPIO.input(Echo):
        pass
    t1 = time.time()
    while GPIO.input(Echo):
        pass
    t2 = time.time()
    return (t2-t1)*340/2

# Get the current date and time
def get_date():
    now = datetime.datetime.now()
    return now.strftime("%Y-%m-%d %H:%M:%S")

# Shape the sensor data to store DB
def shape_data(distance):
    date = get_date()
    result = {"distance": distance,
              "date": date}
    return result

# Set GPIO Pin
GPIO.setmode(GPIO.BOARD)
GPIO.setup(Trigger,GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(Echo,GPIO.IN)

### Main code ###
try:
    while True:
        d = checkdist()
        df = "%0.2f" %d
        result = shape_data(df)
        print ('Distance: %s m' %result["distance"])
        print ('Date: %s' %result["date"])

        #r.set('date', result["date"])
        #r.set('distance', result["distance"])
        r.lset('point0', 0, r.lindex('point10', 0))
        r.lset('point0', 1, r.lindex('point10', 1))
        r.lset('point10', 0, r.lindex('point20', 0))
        r.lset('point10', 1, r.lindex('point20', 1))
        r.lset('point20', 0, r.lindex('point30', 0))
        r.lset('point20', 1, r.lindex('point30', 1))
        r.lset('point30', 0, r.lindex('point40', 0))
        r.lset('point30', 1, r.lindex('point40', 1))
        r.lset('point40', 0, r.lindex('point50', 0))
        r.lset('point40', 1, r.lindex('point50', 1))
        r.lset('point50', 0, result["date"])
        r.lset('point50', 1, result["distance"])
        print('point0-0: %s' %r.lindex('point0', 0))
        print('point0-1: %s' %r.lindex('point0', 1))
        print('point10-0: %s' %r.lindex('point10', 0))
        print('point10-1: %s' %r.lindex('point10', 1))
        print('point20-0: %s' %r.lindex('point20', 0))
        print('point20-1: %s' %r.lindex('point20', 1))
        print('point30-0: %s' %r.lindex('point30', 0))
        print('point30-1: %s' %r.lindex('point30', 1))
        print('point40-0: %s' %r.lindex('point40', 0))
        print('point40-1: %s' %r.lindex('point40', 1))
        print('point50-0: %s' %r.lindex('point50', 0))
        print('point50-1: %s' %r.lindex('point50', 1))
        
        if d < 0.10:
            webhook_url = "XXX"
            text = "The box is full, please check.   XXX"
            requests.post(webhook_url, data = json.dumps({
                "text": text
            }));
        time.sleep(10)

except KeyboardInterrupt:
    GPIO.cleanup()
    print ('GPIO cleeanup and end!')
