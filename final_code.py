import qrcode
import uuid

import tkinter
from PIL import Image, ImageTk
from tkinter import StringVar
import time
import sys
import datetime

import firebase_admin
from firebase_admin import credentials, db

cred = credentials.Certificate("firebase_auth.json")

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://attendance-system-2f77d-default-rtdb.firebaseio.com/'
    })

COURSE = "CNS"
YR = "LY"
BRANCH = "CSE"

ref = db.reference("/Courses").child(BRANCH).child(YR).child(COURSE).child("Lectures")
# ref.set({'Lec 1':{'qrId': '', 'Status':'Started', 'Time':datetime.datetime.now().strftime("%I:%M %p"), 'Present Students': {'0': 'true'}}})
insert_ref = ref.push({'qrId': '', 'LecID': '', 'Status':'Started', 'Date':datetime.date.today().strftime('%d-%m-%Y'), 'Time':datetime.datetime.now().strftime("%I:%M %p"), 'Timestamp': datetime.datetime.now().timestamp()*-1, 'Present Students': {'0': 'true'}})
insert_key = insert_ref.key

ref.child(insert_key).update({'LecID': insert_key})

print("Connected to Firebase & created lecture !")

# Set timer (in sec.)
ct = 60

# Generate QR
def gen_QR():
    data = {'qrID': str(uuid.uuid1()), 'lecID': insert_key, 'branch': BRANCH, 'year': YR, 'course': COURSE}

    lec_ref = ref.child(insert_key)
    lec_ref.update({'qrId': f'{data["qrID"]}'})

    qr = qrcode.QRCode(
        version=6,
        box_size=10,
        border=5
    )

    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill="black", back_color="white")
    qr_img.save("QR.png")

def disp_QR(pilImage):
    global ct
    root = tkinter.Tk()
    w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.overrideredirect(1)
    root.geometry("%dx%d+0+0" % (w, h))
    root.focus_set()    
    root.bind("<Escape>", lambda e: (e.widget.withdraw(), e.widget.quit(), ref.child(insert_key).update({'Status':'Ended'}), sys.exit()))
    txt = StringVar()
    txt.set(ct)
    lb = tkinter.Label(root, textvariable=txt, font=('Arial', 25))
    lb.pack(ipadx=10, ipady=10)
    canvas = tkinter.Canvas(root,width=w,height=h)
    canvas.pack()
    canvas.configure(background='black')
    imgWidth, imgHeight = pilImage.size
    if imgWidth > w or imgHeight > h:
        ratio = min(w/imgWidth, h/imgHeight)
        imgWidth = int(imgWidth*ratio)
        imgHeight = int(imgHeight*ratio)
        pilImage = pilImage.resize((imgWidth,imgHeight), Image.ANTIALIAS)
    image = ImageTk.PhotoImage(pilImage, master=root)
    imagesprite = canvas.create_image(w/2,h/2,image=image)


    while ct:
        ct = ct - 1
        mins, secs = divmod(ct, 60)

        timer = '{:02d}:{:02d}'.format(mins, secs)
        txt.set(timer)

        if mins == 0 and secs == 0:
            ref.child(insert_key).update({'Status':'Ended'})
            sys.exit()

        # Generate QR after every 10 sec 
        if secs%10 == 0:
            gen_QR()
            image = ImageTk.PhotoImage(Image.open("QR.png"), master=root)
            canvas.create_image(w/2,h/2,image=image)
            
        root.update()
        time.sleep(1)

    root.mainloop()

# Main Code
gen_QR()
disp_QR(Image.open("QR.png"))