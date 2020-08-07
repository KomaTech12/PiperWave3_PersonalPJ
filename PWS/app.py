#! /usr/bin/python3

from flask import Flask, render_template, make_response
from io import BytesIO
import urllib
import os

import redis
import time
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.dates as md
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import numpy as np

app = Flask(__name__)
fig = plt.figure(figsize=(12, 4))
ax = fig.add_subplot()
tx = plt.subplot()

# Connect RedisCloud on PWS
r = redis.Redis(host='XXX', port='XXX', password='XXX')

# Initialize graph
plt.cla()

# Draw graph from cloud DB data
@app.route('/')
def set_data():
    # Time from RedisCloud as int
    time_p0 = r.lindex('point0', 0)
    time_p1 = r.lindex('point10', 0)
    time_p2 = r.lindex('point20', 0)
    time_p3 = r.lindex('point30', 0)
    time_p4 = r.lindex('point40', 0)
    time_p5 = r.lindex('point50', 0)

    # Distance from RedisCloud as int
    distance_p0 = 25 - (float(r.lindex('point0', 1)) * 100)
    distance_p1 = 25 - (float(r.lindex('point10', 1)) * 100)
    distance_p2 = 25 - (float(r.lindex('point20', 1)) * 100)
    distance_p3 = 25 - (float(r.lindex('point30', 1)) * 100)
    distance_p4 = 25 - (float(r.lindex('point40', 1)) * 100)
    distance_p5 = 25 - (float(r.lindex('point50', 1)) * 100)

    # Set data to draw graph
    x = [time_p0, time_p1, time_p2, time_p3, time_p4, time_p5]
    y = [distance_p0, distance_p1, distance_p2, distance_p3, distance_p4, distance_p5]
    
    # Draw graph
    xfmt = md.DateFormatter('%Y-%m-%d %H:%M:%S')
    tx.xaxis.set_major_formatter(xfmt)
    plt.cla()
    plt.title('Sensor Data')
    plt.legend()
    plt.grid()
    plt.xlabel('Time')
    plt.ylabel('Trash Capacity')
    plt.plot(x, y, label="Distance")
    plt.xlim([0,5])
    plt.ylim([0,25])

    canvas = FigureCanvasAgg(fig)
    png_output = BytesIO()
    canvas.print_png(png_output)
    data = png_output.getvalue()

    response = make_response(data)
    response.headers['Content-Type'] = 'image/png'

    return response

if __name__ == "__main__":
    app.run(debug=False, host='0.0.0.0', port=int(os.getenv('PORT', '5000')), threaded=True)
