import time

def run():
    start = time.time()
    for i in range(1000):
        j = i * 2
        for k in range(j):
            t = k
            #print(t)
    end = time.time()
    print('run: ',end - start)

clock_start = time.process_time()
run()
clock_end = time.process_time()

print("current time: %f" %(time.time()))

print("current time：")

print("clock start: %f" %(clock_start))

print("clock start: %f" %(clock_end))