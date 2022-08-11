import numpy as np
import urllib.request

url_ip = '172.16.32.252'
url_str = 'http://172.16.32.252/'

#print('val: ' + str(val))

def conn_init(ip, url_str):
    url_str = 'http://'+url_ip+'/'

def conn_test():
    response = urllib.request.urlopen(url_str)
    print('status: %d' %(response.getcode()))

def set_vs1(val):
    befehl = url_str + 'set/' + '2=' + str(val)
    #print(befehl)
    urllib.request.urlopen(befehl)

def get_vs1():
    befehl = url_str + 'get/1'
    #print(befehl)
    response = urllib.request.urlopen(befehl)
    return response.read().decode()

class PIConnet():

    def __init__(self, ip):
        self.default_url = 'http://'+ip+'/'

    def conn_test(self):
        url_response = urllib.request.urlopen(self.default_url)
        code = url_response.getcode()
        if code == 200:
            print("connection successful ")
        else:
            print("connection failed")


