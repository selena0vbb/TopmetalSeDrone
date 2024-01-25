import os
import re
files = os.listdir("../dat/chip_002/i_scan/array_calib/high_i/")
pix_num=[]
for f in files:
    pix_num.append(int(re.findall(r'\d+', f)[0]))

pix_num.sort()
print("(", end=" ")
for p in pix_num:
    print(p,end=" ")

print(")", end=" ")
