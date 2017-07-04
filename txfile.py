# QRXFR - Transfer files using screen and camera
#
# mspeng@gmail.com
#
# This is the sendfile part. 
# Notes:
#   1) Screen size should be greater than 800 x 700 (so QR code fits).
#   2) Python 2.7, pyqrcode, and pyqtgraph installed.
#   3) Best results when screen brightness turned all the way up.
#   4) File size is limited to about 200K since it takes a long time to display.
#   5) How fast the QR code is generated depends on computer; make sure it
#       is faster than the pause intervals
#   6) PyQtGraph is used to draw the QR code fast; good for realtime display
#

# Imports
import pyqrcode
import numpy as np
import datetime as dt
import pyqtgraph as pg

# Parameters
maxFrmCt = 100                          # maximum number of QRcode
intSecTD = dt.timedelta(seconds=1.1)    # time interval between QRcodes
filename = "txfile.py"                # less than 12 chars total

# Different QR code and window sizes and pyqtgraph mrkrsize
# Assume L error correction level and numeric mode
# Can tune and optimize, but make sure the QR code looks good
# qvcapsz = #(ver, max numeric cap, winht, winwi, mrksize)
#qvcapsz = (15,1250,796,780,9) 
#qvcapsz = (16,1408) 
#qvcapsz = (17,1548) 
#qvcapsz = (18,1725)
#qvcapsz = (19,1903) 
#qvcapsz = (20,2061,616,600,5) #(ver, max numeric cap, winht, winwi, mrksize)
qvcapsz = (20,2061,796,780,7) #(ver, max numeric cap, winht, winwi, mrksize)
#qvcapsz = (21,2232)
#qvcapsz = (22,2409)
#qvcapsz = (23,2620)
#qvcapsz = (24,2812)
#qvcapsz = (25,3057)
#qvcapsz = (26,3283)

# For keeping track of performance
stDT = dt.datetime.now()

# Read each byte of file into 2byte integer list. 2bytes = 65536 which uses
# most of the integer space in 5 digits. Could be optimized more.
wordLi = []

byteCt = 0
with open(filename,"rb") as myfile:
    while True:
        abyte = myfile.read(1)
        # check for end of file
        if not abyte:
            break
        byteCt += 1
        tempnum = int(abyte.encode('hex'),16)*256
        bbyte = myfile.read(1)
        if not bbyte:
            wordLi.append(str(tempnum).zfill(5))
            break
        byteCt += 1
        tempnum += int(bbyte.encode('hex'),16)
        wordLi.append(str(tempnum).zfill(5))
print dt.datetime.now()-stDT,"Finished reading",byteCt,"bytes in",filename

# Encode filename, period ascii code is zero so charaters lower than 
# that don't work. Filename will be in header.
fnhdrint = map(lambda x: ord(x)-ord('.'),filename)
# assume filename has at least 2 characters so can just use 1 digit
fnhdrstr = str(len(fnhdrint)-3)+"".join(map(lambda x:str(x).zfill(2),fnhdrint))

# Header is: frame id, total frame count, encoded filename
hdrLen = 3+3+len(fnhdrstr)  
#hdrLen = 3+3+1+len(hdrint)*2 

# A frame is a set of data in each QR code image (amount determined by QR
# code capacity). QR code will be using numeric data.
# Add extra 1 because of truncation.
totalFrameCt = len(wordLi)*5/qvcapsz[1] + 1

# May need more frames than based on filesize due to header
while totalFrameCt*hdrLen + len(wordLi)*5 > totalFrameCt*qvcapsz[1]:
    totalFrameCt += 1
print dt.datetime.now()-stDT,"Required frames:",totalFrameCt

if totalFrameCt > maxFrmCt:
    print "Sorry, file size exceeds max ~",maxFrmCt*qvcapsz[1]/5*2,"bytes, Exit!"
else:
    # Set up graph for displaying QR codes
    pg.setConfigOption('background','w')
    pw = pg.plot()
    pw.parentWidget().move(100,0)   # move to top of screen and to left
    pw.resize(qvcapsz[2]-20,qvcapsz[3]-20) 
    
    # Generate QR Codes frame by frame and display as soon as ready
    lpstDT = dt.datetime.now()
    for frmNum in range(totalFrameCt):
        encdatastr = str(frmNum).zfill(3) + str(totalFrameCt).zfill(3) + fnhdrstr
        for i in range((qvcapsz[1]-hdrLen)/5):
            if wordLi:
                encdatastr += wordLi.pop(0)
            else:
                break
        mycode = pyqrcode.create(encdatastr,
                                 error='L',
                                 version=qvcapsz[0],
                                 mode='numeric')
        mytxt = mycode.text()
        mytxt1 = mytxt.split('\n')[:-1] # ignore last element which is empty
        # put it in format for pyqtgraph to display easily using scatter plot
        mybxAr = np.array([[int(x) for x in mystring] for mystring in mytxt1])
        xs = []
        ys = []
        # pyqrcode adds 4 zeros before and after the data for padding so ignore
        for i in range(4,mybxAr.shape[0]-4):
            for j in range(4,mybxAr.shape[1]-4):
                if mybxAr[i,j] == 1:
                    xs.append(i)
                    ys.append(j)
        # wait until time interval to display
        print dt.datetime.now()-stDT,"QR data generated, Status",frmNum,"/",totalFrameCt
        while dt.datetime.now()-lpstDT < intSecTD:
            pg.QtGui.QApplication.processEvents()
        pw.plot(xs,ys,pen=None,symbol='s',symbolPen='k',symbolBrush='k',symbolSize=qvcapsz[4],clear=True)
        pw.addItem(pg.TextItem("%d of %d" % (frmNum,totalFrameCt),color=(255,0,0),anchor=(-1,1)))
        lpstDT = dt.datetime.now()
        print dt.datetime.now()-stDT,"QR data drawn",frmNum,"/",totalFrameCt
    
    while dt.datetime.now()-lpstDT < intSecTD:
        pg.QtGui.QApplication.processEvents()
    pw.parentWidget().close()
