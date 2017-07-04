# qrxfr
Transfer files from camera enabled laptop to camera enabled laptop optically (no wires or RF)

Sometimes it's not convenient to transfer files using traditional methods such as USB sticks, memory cards, or even wifi/bluetooth methods. Hence this idea was born of transferring files using the screen as a transmitter and the camera as a receiver.

QR codes were chosen due to their robustness (error connection, alignment, etc.), ease of use, and python library support. Pyqtgraph was chosen to draw QR codes due it's speed in drawing and updating. Zbar and opencv were chosen to decode QR codes.

This program transmits small files less than 100kB.

Much more work could go into improving this work such as improving encoding of data, compression, and improving bandwith (like using color QR codes).

Read "qrxfrsetup.txt" for information about how to get it working.

I also have a YouTube video showing the program in action.
