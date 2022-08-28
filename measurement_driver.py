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
                        "vs8": {"get": "/18", "set": "/19"},
                        "cs1": {"get": "/21", "set": "/22"},
                        "cs2": {"get": "/23", "set": "/24"},
                        "cs3": {"get": "/25", "set": "/26"},
                        "cs4": {"get": "/27", "set": "/28"},
                        "cs5": {"get": "/29", "set": "/30"},
                        "cs6": {"get": "/31", "set": "/32"},
                        "cs7": {"get": "/33", "set": "/34"},
                        "cs8": {"get": "/35", "set": "/36"},
                        "ld1": {"get": "/5", "set": "/37"}}

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

    def multi_channel_sweep(self, channels, value_v):

        channel_list = list(channels)
        result_list = []

        for (ii, val) in enumerate(value_v):
            command_send = self.default_url + "set"
            command_recv = self.default_url + "get"
            for c in channel_list:
                command_send = command_send + self.channel[c]["set"] + "=" + str(val)
                command_recv = command_recv + self.channel[c]["get"]
            urllib.request.urlopen(command_send)
            response = urllib.request.urlopen(command_recv)
            result_str = response.read().decode
            result_int_list = list(np.fromstring(result_str))
            result_list.append(result_int_list)











class PIConnect2():
    def __init__(self, ip):
        self.default_url = 'http://' + ip + '/'
        self.channel = {"vs1": {"get": "/1", "set": "/2"},
                        "vs2": {"get": "/3", "set": "/4"},
                        "vs3": {"get": "/6", "set": "/7"},
                        "vs4": {"get": "/8", "set": "/9"},
                        "vs5": {"get": "/11", "set": "/12"},
                        "vs6": {"get": "/13", "set": "/14"},
                        "vs7": {"get": "/16", "set": "/17"},
                        "vs8": {"get": "/18", "set": "/19"}}

        self.channel_cmd = {"vs1": ["get_command_list_vs1", "set_command_list_vs1"]}

        self.get_command_list_vs1 = []
        self.set_command_list_vs1 = []

    def set_channel_cmd(self, channel, array):
        self.get_command_list_vs1.clear()
        self.set_command_list_vs1.clear()

        get_cmd_list = []
        set_cmd_list = []

        for i in array:
            set_cmd = self.default_url + "set" + self.channel[channel]["set"] + "=" + str(i)
            set_cmd_list.append(set_cmd)
            get_cmd = self.default_url + "get" + self.channel[channel]["get"]
            get_cmd_list.append(get_cmd)

        setattr(self, "get_command_list_vs1", get_cmd_list)
        setattr(self, "set_command_list_vs1", set_cmd_list)

    def set_value(self, channel, value):
        command = self.default_url + "set" + self.channel[channel]["set"] + "=" + str(value)
        urllib.request.urlopen(command)

    def get_value(self, channel):
        command = self.default_url + "get" + self.channel[channel]["get"]
        response = urllib.request.urlopen(command)
        return int(response.read().decode())

    def channel_sweep(self, channel):
        set_cmd_list = getattr(self, self.channel_cmd[channel][0])
        get_cmd_list = getattr(self, self.channel_cmd[channel][1])
        result_v = np.zeros((len(set_cmd_list),))
        #print(set_cmd_list)
        #print(get_cmd_list)
        for i in range(len(set_cmd_list)):
            urllib.request.urlopen(set_cmd_list[i])
            response = urllib.request.urlopen(get_cmd_list[i])
            result_v[i] = response.read().decode()

        return result_v



a_array = np.arange(0, 10, 1)
#print(a_array)
objtest = PIConnect2(url_ip)

objtest.set_channel_cmd("vs1", a_array)
#print(objtest.get_command_list_vs1)
#objtest.channel_sweep("vs1")

b = np.arange(0, 5, 1)
a = np.zeros((5, ))
print(a)