from PIL import Image
import numpy as np
import wave
import struct, sys, math

def avg(l):
    s = 0
    for i in l:
        s+=i
    return s/len(l)

def center(l):
    avgc = avg(l)
    res = []
    for i in l:
        res.append(i-avgc)
    return res

def toRange(l, r):
    m = max([max(l), abs(min(l))])
    res = []
    for i in range(len(l)):
        res.append(r*l[i]/m)
    return res

def genCSV(l, csvName):
    out = open(csvName+".csv", "w")
    for c in l:
        out.write(c.__str__()+"\n")
    out.close()

def writeWav(l, outWName, duration):
    outW = wave.open(outWName, "w")
    outW.setnchannels(1)
    outW.setsampwidth(2)
    outW.setframerate(len(l)/duration)
    for e in l :
        data = struct.pack('<h', int(e))
        outW.writeframesraw( data )
    outW.close()


def avgFilter(l, filtre):
    res = []
    for i in range(len(l)):
        if filtre+i<len(l):
            res.append(avg(l[i:i+filtre]))
        else:
            res.append(avg(l[i:]))
    return res

def sinLink(l, duration):
    f = 44100
    ns = f*duration
    r = int(ns/len(l))
    res = []
    for i in range(len(l)-1):
        pA = l[i]
        pB = l[i+1]
        offset = (pA+pB)/2
        coef = (pA-pB)/2
        for sI in range(r+1):
            theta = sI*math.pi/r
            c = coef*math.cos(theta)+offset
            res.append(c)
    return res, r

def imgReader(inImg):
    img = Image.open(inImg)
    imgArr = np.array(img)
    img.close()
    height = len(imgArr)
    c = imgArr[0]
    length = len(c)
    l=[]
    for icol in range(length):
        top = 0
        bttm = -1
        col = imgArr[:,icol]
        for ipix in range(height):
            pix = col[(ipix+1)-height]
            if(pix>0):
                if(bttm<0):
                    bttm=ipix
                else:
                    top=ipix
        l.append(top)
        l.append(bttm)
    print(len(l))
    return l


inImg = "in.bmp"
outWName = "out"
filtre = 4
csvE = False
csvName = "out"
duration = 1

if len(sys.argv)>1:
    arg = sys.argv[1:]
    i=0
    while i<len(arg):
        if arg[i] == "-i":
            inImg = arg[i+1]
        elif arg[i] == "-o":
            outWName = arg[i+1]
        elif arg[i] == "-f":
            filtre = int(arg[i+1])
        elif arg[i] == "-csv":
            csvE = True
            csvName = arg[i+1]
        elif arg[i] == "-l":
            duration = float(arg[i+1])
        else:
            print("unknown argument:"+arg[i]+" = "+arg[i+1])
        i+=2

l = imgReader(inImg)
if(filtre>0):
	l = avgFilter(l,filtre)
l, nSample = sinLink(l, duration)
if(filtre>0):
    l = avgFilter(l,filtre*nSample)
l = center(l)
l = toRange(l, 32767)
if(csvE):
    genCSV(l, csvName)
writeWav(l, outWName, duration)
