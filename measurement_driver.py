import numpy as np
import urllib.request

url_ip = '172.16.32.252'
url_str = ''

print('val: ' + str(val))

def conn_init(ip):
    url_str = 'http://'+url_ip+'/'

def set_vs1(val):
    befehl = url_str + '2=' + str(val)
    urllib.request.urlopen(befehl)

def get_vs1():
    befehl = url_str + 'get/1'
    response = urllib.request.urlopen(befehl)