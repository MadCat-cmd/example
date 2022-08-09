import urllib.request

url = 'https://www.baidu.com'
url2= 'https://asdasds.com'

response = urllib.request.urlopen(url)

print(response.read().decode())
