import urllib.request

url = 'http://172.16.32.252/'
urlset = 'http://172.16.32.252/set/2=2000'
url2= 'http://172.16.32.252/get/1'

urllib.request.urlopen(urlset)
response = urllib.request.urlopen(url2)
response.getcode()

print(response.read().decode())
1

print("status: %d"  %(response.getcode()))
