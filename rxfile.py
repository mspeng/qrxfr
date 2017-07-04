# QRXFR - Transfer files using screen and camera
#
# mspeng@gmail.com
#
# This is the sendfile part. 
# Notes:
#   1) Camera resolution of 640x480 or better.
#   2) Python 2.7, zbar and opencv installed.
#       For zbar, NaturalHistoryMuseum/ZBarWin64 wheel was used; might need to 
#           Visual C++ Redistributable for 2013 to make it work.
#       For opencv, opencv3.1 downloaded from opencv.org
#
 
# Todo: Process multiple images, resume
 
# Imports
import zbar
import cv2
import datetime as dt

stDT = dt.datetime.now()
print stDT-stDT,"Started..."

# Parameters
ramp_frames = 30                    # how many frames to throw away when starting
camera_port = 0                     # usually this is the default one on laptop
inttoTD = dt.timedelta(seconds=20)  # how long to wait between frames for timeout
tottoTD = dt.timedelta(seconds=300) # total time to wait before quitting
width,height = 640,480              # default camera settings

# Set up camera, accessed through opencv
camera = cv2.VideoCapture(camera_port)
for i in xrange(ramp_frames):
    retval, temp = camera.read()

# configure zbar reader
scanner = zbar.ImageScanner()
scanner.parse_config("enable")

# start trying to get data or wait until timeout, data structure lists data
# has flag in front of frame data to indicate if it has been gotten
notdoneFlg = True
FRMHDRLEN = 6
FNHDRLEN = 1
QRCODENUM = 64 
frmLi = [(False,0)] # setup where data will go with empty first one
gotfrmCt = [it[0] for it in frmLi].count(True)

lstfrmDT = dt.datetime.now()

while notdoneFlg and dt.datetime.now()-stDT < tottoTD and dt.datetime.now()-lstfrmDT < inttoTD:
    retval, camera_capture = camera.read()  # get image
    imgray = cv2.cvtColor(camera_capture, cv2.COLOR_BGR2GRAY) # convert to gray
    raw = str(imgray.data)
    print ".",
    image = zbar.Image(width,height,'Y800', raw)
    scanner.scan(image)    # process image for QRcodes
    for symbol in image:   # should only be frame in each image
        # only get QRcode data
        if symbol.type == QRCODENUM: # enum for "QRCODE":
            # Adjust the number of frames if not correct, should only happen once
            if len(frmLi) != int(symbol.data[FRMHDRLEN/2:FRMHDRLEN]):
                frmLi = [(False,None)]*int(symbol.data[FRMHDRLEN/2:FRMHDRLEN])
            # get filename
            fnhdrstr = symbol.data[FRMHDRLEN+FNHDRLEN:
                                   FRMHDRLEN+FNHDRLEN+(int(symbol.data[FRMHDRLEN])+3)*2]
            # get data without headers
            frmLi[int(symbol.data[:FRMHDRLEN/2])] = (True,
                                                     symbol.data[FRMHDRLEN+FNHDRLEN+(int(symbol.data[FRMHDRLEN])+3)*2:])
            gotfrmCt = [it[0] for it in frmLi].count(True)
            lstfrmDT = dt.datetime.now()
            print " "
            print dt.datetime.now()-stDT,"Frame",int(symbol.data[:FRMHDRLEN/2]),"received, Status",gotfrmCt,"/",len(frmLi)

    # check if all frames have been gotten, if so then get out
    if gotfrmCt == len(frmLi):
        notdoneFlg = False

# cleanup, important to release camera!
del camera
del image

if dt.datetime.now()-stDT > tottoTD:
    print dt.datetime.now()-stDT,"Timed out - total time"
elif dt.datetime.now()-lstfrmDT > inttoTD:
    print dt.datetime.now()-stDT,"Timed out - time between frames"
else:
    # reconstruct file
    fnhdrint = [ord('.')+int(fnhdrstr[i:i+2]) for i in range(0,len(fnhdrstr),2)]
    filename = "".join(map(chr,fnhdrint))
    byteCt = 0
    with open(filename,"wb") as myfile:
        for frm in frmLi:
            for i in range(len(frm[1])/5):
                tempnum = int(frm[1][i*5:i*5+5])
                #print tempnum
                writebytes = [tempnum/256, tempnum-tempnum/256*256]
                if writebytes[1] == 0 and i == len(frm)/5-1: # we've come to the end
                    byteCt += 1
                    myfile.write(bytearray([writebytes[0]]))
                else:
                    byteCt += 2
                    myfile.write(bytearray(writebytes))
    
    print dt.datetime.now()-stDT,"Done reconstructing file",filename,byteCt,"bytes"