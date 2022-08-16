import numpy as np
import urllib.request
import numpy as np

url_ip = '172.16.32.252'
url_str = 'http://172.16.32.252/'


# print('val: ' + str(val))

def conn_init(ip, url_str):
    url_str = 'http://' + url_ip + '/'


def conn_test():
    response = urllib.request.urlopen(url_str)
    print('status: %d' % (response.getcode()))


def set_vs1(val):
    befehl = url_str + 'set/' + '2=' + str(val)
    # print(befehl)
    urllib.request.urlopen(befehl)


def get_vs1():
    befehl = url_str + 'get/1'
    # print(befehl)
    response = urllib.request.urlopen(befehl)
    return response.read().decode()


# PIConnet Class
class PIConnet():

    def __init__(self, ip):
        self.default_url = 'http://' + ip + '/'

        self.channel = {"vs1": {"get": "/1", "set": "/2"},
                        "vs2": {"get": "/3", "set": "/4"},
                        "vs3": {"get": "/6", "set": "/7"},
                        "vs4": {"get": "/8", "set": "/9"},
                        "vs5": {"get": "/11", "set": "/12"},
                        "vs6": {"get": "/13", "set": "/14"},
                        "vs7": {"get": "/16", "set": "/17"},
                        "vs8": {"get": "/18", "set": "19"}}

    def conn_test(self):
        url_response = urllib.request.urlopen(self.default_url)
        code = url_response.getcode()
        if code == 200:
            print("connection successful ")
        else:
            print("connection failed")

    def source_enable(self):
        command = self.default_url + "set/0=1"
        response = urllib.request.urlopen(command)

        if response.read().decode() == "ACK":
            print("source enabled...")
        else:
            print("cannot enable")

    def source_disable(self):
        command = self.default_url + "set/0=0"
        response = urllib.request.urlopen(command)

        if response.read().decode() == "ACK":
            print("source enabled...")
        else:
            print("cannot enable")

    def set_value(self, channel, value):
        command = self.default_url + "set" + self.channel[channel]["set"] + "=" + str(value)
        urllib.request.urlopen(command)

    def get_value(self, channel):
        command = self.default_url + "get" + self.channel[channel]["get"]
        response = urllib.request.urlopen(command)
        return int(response.read().decode())

    def set_get_value(self, channel, value):
        command_send = self.default_url + "set" + self.channel[channel]["set"] + "=" + str(value)
        command_recv = self.default_url + "get" + self.channel[channel]["get"]
        urllib.request.urlopen(command_send)
        response = urllib.request.urlopen(command_recv)
        return int(response.read().decode())

    def channel_sweep(self, channel, v_value):
        mess_value = np.zeros(len(v_value))
        command_send = self.default_url + "set" + self.channel[channel]["set"] + "="
        command_recv = self.default_url + "get" + self.channel[channel]["get"]

        for (ii, val) in enumerate(v_value):
            urllib.request.urlopen(command_send + str(val))
            response = urllib.request.urlopen(command_recv)
            mess_value[ii] = int(response.read().decode())

        return mess_value
