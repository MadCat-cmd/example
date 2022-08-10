import urllib.request

url = 'http://172.16.32.252/'
url2= 'http://172.16.32.252/get/1'

response = urllib.request.urlopen(url2)

print(response.read().decode())
