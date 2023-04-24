import os
import time


#time.sleep(430)
res = os.popen("ls /root/linux-git/kernel").readlines()
data = []
for r in res:
    r = r.split("\n")[0]
    if r.endswith(".patch"):
        data.append(r)
print(data)

os.chdir("/root/linux-git/kernel")
for d in data:
    os.popen("git send-email --to=wanghaosqsq@163.com {} --suppress-cc=all --force".format(d)).readlines()
    time.sleep(0.1)
