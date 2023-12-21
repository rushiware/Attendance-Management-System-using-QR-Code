import os
import re
from django.shortcuts import render, redirect
import datetime
import qrcode
import uuid
import firebase_admin
from firebase_admin import credentials, db, auth
from django.http import JsonResponse
from django.contrib import messages
import pyrebase
from django.contrib.auth import authenticate, login, logout
from .decorators import firebase_authenticated

firebaseConfig = {
    "type": "service_account",
    "project_id": "attendance-system-2f77d",
    "private_key_id": "b727b09b9c426864daca308d27984abb99c85032",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCaeNckxanH1Ymk\nRiBk/WIcb8r6llg1qmKJGze0/PjRGMrBYO9oHK7AevfXvQljqiulze9jsXJw8vpQ\nUtA0z1LfehpNayfbUrTM8kFbVwK/XssmEwb0gh/RzLzCaRcZSXdC6qACaVWwHUsE\nN17iKrUjaEKpPdOwK7CB9l8BBR43PRjfFU84vWIBwZjGZtJD8KT1TqO6jyKThrZm\nRqZJFqWz/Jk6vKC4lB63bs4SDPnXJmTmw6e0Xdt9r+p1t9aQ51XXxkV2EOCc6RU6\nWTN2QX9Fx5zb1Ds+ntxIXZEO2a2Njpt2t2+V6NtcM80RI6qXqL6TSU2mD/O1cS2n\nYRmZX7pnAgMBAAECggEADqlunk5mrZGOpXmEhKFqSRGxXfScPcfE34emU3b5dPtZ\n713wi1zBl4J0eNU4CW4zA2NXGArVNnRRnwMlQQX2s0CHM5b6qv4gLB3IZ0+Mcrag\nKKaAr/+T3pmExx0rdJp9B+x2MJRn7jXxk15gEq6ED+7K+P5l0+BpugQ1A0dFlW+A\n5OgabBRtpjGC1Fk0+UdQmGGbDyKphsmK8YZqUKZXis4HxTOYiozIEoiXNE+NQEFk\nTsVtWrq6btEOWFOH+GVy1oZ3tBweBLyaXA6qJIXC2vfeyvLltkpEzT+95FTy8eS4\nbQhMUKxVeGm3JNLOwx4Dm4BifxQYEOG0R5rwLgzPSQKBgQDLTgD0Jw2ngGIAOfGM\nYweZHvBNpvSzMeqp7DVJAy0fWBkAknBuufTufinyZrZUz6NYcDESABE3HdrHTiWY\nFyrZWCh8Dkuylx/yScFaNM0Khxbe8tT3+QklxsI1goRrd4Twn/9l7GFg8d+yFWvX\nvL6hnHFuJIeLXNKyGOYSvTMRXwKBgQDCgp0o1TIjDX8+GO/GoVXyERZcIwwtw06Q\n/Z+JzJ/KAq8pp6UJjfgoqK/5CXKbPhjePYCoLRVtTuCiHso44ay28Ei7aOOGl7Ft\ne/DBEeJyH0UnZVuA3zwoUU+BKP5EavPneBiXhag7Jq8TFH6ysjjfhTI07FMLkJ5v\nUi4954NL+QKBgQCXA90vfubkmjexpVjoiBL3yYSEmdTAWv7Ns7itAF//HWiNBTng\n9d6bXTn5ZhRgEVBrfALnNQeUomeFjmXcgLECezqvU8sk4J8JUYH/aKM6A7iYaVaK\n0ADcf7R5HPcSANjOCHslEZ4P7frVBJZzzS7pSxTy1M2eVpfnVRlpqAKMDwKBgB/j\n/FJqifrXRqpuujlN0GKMzKa0lFWYdPQusQ6NvxEG2aMxukxTu4EnDxr8oo6zYq5l\nVQe9xIqUaR4LgEpNLd0cjkAz1UIG8u8pZ/KvtPnTCKqJ4rPBZgKSOj/J8c5T3sNv\nnFCTeF6iXAf7zz4LHGoBU5b7vC3kOyWzSqOZppw5AoGARYh/UFByrBs7HRACq2+6\nnPSBqa/TJ8rLYny1I9NcZstrQnhXq9zKrqm4ihU/sfpdroT6O3FwuUnOp6uklIFM\nD90DXUB/HKmCTS4sBpnTjrupd9pyoav9uy35BTNkDxpMqAQW+luHXrsSMIJeZHlh\n5uzFnxg+zE65dKBdYIiA9Ak=\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-bamb7@attendance-system-2f77d.iam.gserviceaccount.com",
    "client_id": "114454284992133838418",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-bamb7%40attendance-system-2f77d.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

cred = credentials.Certificate(firebaseConfig)

firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://attendance-system-2f77d-default-rtdb.firebaseio.com/'
})

# Set timer (in sec.)
ct = 60

def gen_QR(ref, insert_key, branch, yr, course):
    data = {'qrID': str(uuid.uuid1()), 'lecID': insert_key, 'branch': branch, 'year': yr, 'course': course}

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

    save_dir = f"media/QR/{branch}/{yr}/{course}/{insert_key}"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)

    qr_img.save(f"{save_dir}/QR.png")

    saved_img_url = f'/{save_dir}/QR.png'

    return saved_img_url

# Pyrebase Firebase
config={
    "apiKey": "AIzaSyDMt7O82KqYYUrtcROWEWEXNpwOIWj8riI",
    "authDomain": "attendance-system-2f77d.firebaseapp.com",
    "databaseURL": "https://attendance-system-2f77d-default-rtdb.firebaseio.com",
    "projectId": "attendance-system-2f77d",
    "storageBucket": "attendance-system-2f77d.appspot.com",
    "messagingSenderId": "935686411905",
    "appId": "1:935686411905:web:d79a0ba90beee401185f80",
    "measurementId": "G-DZ3DQJYY31"
}

py_firebase=pyrebase.initialize_app(config)
py_auth = py_firebase.auth()

# Create your views here.
def home(request):
    return render(request, "home.html")

def signin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(username=email, password=password)
        if user is not None:
            # A backend authenticated the credentials
            login(request, user)
            return redirect("home")   

        else:
            try:
                user=py_auth.sign_in_with_email_and_password(email,password)
                session_id=user['idToken']
                user_id=user['localId']
                request.session['teacher_name'] = db.reference("/Faculties").child(user_id).child("Name").get()
                request.session['uid']=str(session_id)
                request.session['user_email']=email
                request.session['user_uid']=user_id
                return redirect("home")
            except:
                messages.error(request, "Invalid Credentials!")
                return render(request,"sign_in.html")

    return render(request, "sign_in.html")

def forgot_pass(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            py_auth.send_password_reset_email(email)
            messages.success(request, "An email to reset password is successfully sent to your email!")
            return render(request, "forgot_pass.html")
        except:
            messages.error(request, "Something went wrong!!\nPlease check the email you provided is registered or not!")
            return render(request, "forgot_pass.html")

    return render(request, "forgot_pass.html")

def lg_out(request):
    try:
        del request.session['uid']
        del request.session['user_email']
    except:
        pass
    return redirect("home")

def sout(request):
    logout(request)
    return redirect("home")

@firebase_authenticated
def courses(request, teacher_uid, *args, **kwargs):
    nm = db.reference("/Faculties").child(teacher_uid).child("Name").get()
    branch = db.reference("/Faculties").child(teacher_uid).child("Branch").get()
    courses_ref = db.reference(f"/Courses/{branch}/")

    courses = []

    for year_key, year_value in courses_ref.get().items():
        # Iterate through the course names
        for course_name_key, course_name_value in year_value.items():
            # Check if the teacher matches the given name
            if course_name_value.get('Teacher') == nm:
                # Append the course details to the list
                courses.append({
                    'Year': year_key,
                    'Course_Name': course_name_key,
                    'Course_Code': course_name_value.get('Code'),
                })
    
    return render(request, "courses.html", {'courses': courses, 'branch': branch})

def view_courses(request, branch, yr, c_code):
    courses_ref = db.reference(f"/Courses/{branch}/{yr}/")

    course = []

    for course_name_key, course_name_value in courses_ref.get().items():
        # Check if the code matches the given code
        if course_name_value.get('Code') == c_code:
            # Append the course details to the list
            course.append({
                'Course_Name': course_name_key,
                'Branch': branch,
                'Year': yr,
                'Course_Code': course_name_value.get('Code'),
                'Enrolled Students': course_name_value.get('Enrolled Students'),
            })

    stud = []
    stud_ref = db.reference("/Students")

    if len(course[0]['Enrolled Students']) == 1 and course[0]['Enrolled Students'][0] == True:
        pass
    else:
        for es in course[0]['Enrolled Students']:
            stud_details = stud_ref.order_by_child("PRN").equal_to(es).get()
            stud_data = {"PRN": es,"Name": list(stud_details.values())[0]['Name'], "Phone": list(stud_details.keys())[0], "Branch": list(stud_details.values())[0]['Branch']}
            stud.append(stud_data)

    return render(request, "view_course.html", {'course': course, 'students': stud})

@firebase_authenticated
def lec_create(request, branch, yr, c_code):
    course_ref = db.reference(f"/Courses/{branch}/{yr}/")
    c_data = course_ref.order_by_child('Code').equal_to(c_code).get()
    if c_data:
        subj = list(c_data.keys())[0]
    else:
        return JsonResponse({"Error": f"Invalid Course Code - {c_code}"})

    ref = db.reference("/Courses").child(branch).child(yr).child(subj).child("Lectures")

    dt = datetime.date.today().strftime('%d-%m-%Y')
    tm = datetime.datetime.now().strftime("%I:%M %p")

    insert_ref = ref.push({'qrId': '', 'LecID': '', 'Status':'Started', 'Date': dt, 'Time': tm, 'Timestamp': datetime.datetime.now().timestamp()*-1, 'Present Students': {'0': 'true'}})
    insert_key = insert_ref.key

    ref.child(insert_key).update({'LecID': insert_key})
    img_url = gen_QR(ref, insert_key, branch, yr, subj)

    return render(request, "create_lec.html", {'img_url': img_url, 'insert_key': insert_key, 'branch': branch, 'yr': yr, 'course': subj, 'c_code': c_code, 'c_dt': dt, 'c_tm': tm})

@firebase_authenticated
def genQR_url(request):
    branch = request.POST['branch']
    year = request.POST['year']
    subject = request.POST['subject']
    insert_key = request.POST['insert_key']

    ref = db.reference("/Courses").child(branch).child(year).child(subject).child("Lectures")
    gen_QR(ref, insert_key, branch, year, subject)

    return JsonResponse({'Status': 'Success'})

@firebase_authenticated
def view_lec(request, branch, yr, c_code):
    courses_ref = db.reference(f"/Courses/{branch}/{yr}/")
    lec = []
    course = []

    for course_name_key, course_name_value in courses_ref.get().items():
        # Check if the code matches the given code
        if course_name_value.get('Code') == c_code:
            # Append the lecture & course details to the list
            lec.append({
                'Lectures': course_name_value.get('Lectures'),
            })
            course.append({
                'Course_Name': course_name_key,
                'Course_Code': course_name_value.get('Code'),
            })

    lectures = []

    if lec[0]['Lectures'] == None:
        pass
    else:
        for l in lec:
            for lecture_id, lecture_data in lec[0]['Lectures'].items():
                if lecture_data['Present Students'] == ['true']:
                    student_ids = []
                else:
                    student_ids = [student_id for student_id in lecture_data['Present Students']]
                lec_data = {"LecID": lecture_id,"Date": lecture_data['Date'], "Time": lecture_data['Time'], "Timestamp": lecture_data['Timestamp'], "Present_Students": student_ids}
                lectures.append(lec_data)
    
    return render(request, "view_lec.html", {'lectures': lectures, 'course': course})

@firebase_authenticated
def stud_att(request, branch, yr, c_code):
    courses_ref = db.reference(f"/Courses/{branch}/{yr}/")

    enroll_stud = []
    course = []

    c_name = ""

    for course_name_key, course_name_value in courses_ref.get().items():
        # Check if the code matches the given code
        if course_name_value.get('Code') == c_code:
            # Append the lecture & course details to the list
            c_name = course_name_key
            enroll_stud.append({
                'Enrolled Students': course_name_value.get('Enrolled Students')
            })
            course.append({
                'Course_Name': course_name_key,
                'Course_Code': course_name_value.get('Code'),
            })
            
    stud = []
    stud_ref = db.reference("/Students")

    if len(enroll_stud[0]['Enrolled Students']) == 1 and enroll_stud[0]['Enrolled Students'][0] == True:
        pass
    else:
        for es in enroll_stud[0]['Enrolled Students']:
            lectures_ref = db.reference(f'Courses/{branch}/{yr}/{c_name}/Lectures')

            # Initialize a counter for attended lectures & total lectures
            total_lectures_count = 0
            attended_lectures_count = 0

            # Query the lectures
            lectures_snapshot = lectures_ref.get()
            if lectures_snapshot:
                total_lectures_count = len(lectures_snapshot)
                for lecture_id, lecture_data in lectures_snapshot.items():
                    present_students = lecture_data.get('Present Students', {})
                    if es in present_students:
                        attended_lectures_count += 1

            stud_details = stud_ref.order_by_child("PRN").equal_to(es).get()
            stud_data = {"PRN": es,"Name": list(stud_details.values())[0]['Name'], "Attendance": "{:.2f}".format((attended_lectures_count/total_lectures_count)*100) if total_lectures_count>0 else "0" }
            stud.append(stud_data)

    return render(request, "stud_attendance.html", {'course': course, 'students': stud})

def lec_ended(request, branch, yr, c_code):
    messages.warning(request, "Session Ended!")
    return redirect("view_courses", branch, yr, c_code)

def users_stud(request):
    ROLE = "student"
    ref = db.reference("/Students")

    try:
        user_list = []
        for user in auth.list_users().iterate_all():
            if user.phone_number is None:
                continue
            usr_ref = ref.child(re.sub(r'^\+91', '', user.phone_number))
            user_data = {
                "name": usr_ref.child("Name").get(),
                "phone_number": user.phone_number,
                "PRN": usr_ref.child("PRN").get(),
                "branch": usr_ref.child("Branch").get(),
                "year": usr_ref.child("Year").get(),
            }
            user_list.append(user_data)
        return render(request, "users.html", {"role": ROLE, "users_list": user_list})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

def users_faculty(request):
    ROLE = "faculty"
    ref = db.reference("/Faculties")

    try:
        fact_list = []
        for user in auth.list_users().iterate_all():
            if user.email is None:
                continue
            usr_ref = ref.child(user.uid)
            user_data = {
                "name": usr_ref.child("Name").get(),
                "email": user.email,
                "branch": usr_ref.child("Branch").get()
            }
            fact_list.append(user_data)
        return render(request, "users.html", {"role": ROLE, "fact_list": fact_list})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
