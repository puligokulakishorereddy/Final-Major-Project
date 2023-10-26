from flask import Flask, render_template, Response,request
import cv2
import pyaudio
import json
import audioop
import pymysql.cursors
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='@g209X1A05H6g@',
                             database = 'students'            
                             )
cursor = connection.cursor()


# sql='''create table `sd`(
# `name` varchar(20),
# `roll` varchar(20),
# `score` varchar(40)
# )'''
# cursor.execute(sql)

app = Flask(__name__)

# Initialize audio input stream
audio = pyaudio.PyAudio()
stream = audio.open(format=pyaudio.paInt16, channels=1, rate=44100, input=True, frames_per_buffer=1024)

def generate_frames():
    # Initialize video capture
    phone_cascade= cv2.CascadeClassifier('C:\\Users\\sai\\OneDrive\\Desktop\\FYP\\haarcascade_phone.xml')  # Replace with the correct path to your XML file

    cap = cv2.VideoCapture(0)
    
    # Variables for tracking eye movement, tab switching, and noise detection
    blink_counter = 0
    prev_eye_state = True  # True when eyes are open, False when eyes are closed
    max_blink_count = 2  # Maximum allowed blinks
    tab_switch_detected = False
    noise_detected = False
    noise_reset_counter = 0
    noise_reset_threshold = 50  # Adjust as needed

    while True:
        ret, frame = cap.read()

        if not ret:
            break

        # Measure sound levels
        audio_data = stream.read(1024)
        rms = audioop.rms(audio_data, 2)

        # Convert the frame to grayscale for face and eye detection
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces) == 0:
            cv2.putText(frame, "Face Not Detected!", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        for (x, y, w, h) in faces:
            # Draw a rectangle around the face
            #cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # Extract the region of interest (ROI) for eyes
            roi_gray = gray[y:y + h, x:x + w]

            # Use Haar Cascade to detect eyes
            eyes = cv2.Canny(roi_gray, 100, 200)

            # Check for eye state (open or closed)
            eye_state = True  # Default to open
            contours, _ = cv2.findContours(eyes, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            for contour in contours:
                area = cv2.contourArea(contour)
                if area < 1000:  # Threshold for closed eyes
                    eye_state = False  # Eyes are closed

            if eye_state != prev_eye_state:
                prev_eye_state = eye_state
                if not eye_state:
                    blink_counter += 1

            # Check for tab switching (use a more sophisticated method for actual implementation)
            key = cv2.waitKey(1)
            if key == 9:  # Tab key
                tab_switch_detected = True

            # Check for excessive noise
            if rms > 1000:  # Adjust the noise threshold as needed
                noise_detected = True
                noise_reset_counter = 0
            else:
                if noise_reset_counter < noise_reset_threshold:
                    noise_reset_counter += 1
                else:
                    noise_detected = False

            # Display warning if suspicious activity is detected
            if blink_counter > max_blink_count or noise_detected:
                cv2.putText(frame, "Suspicious Activity Detected!", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        

        ret, buffer = cv2.imencode('.jpg', frame)
        if not ret:
            continue

        frame = buffer.tobytes()
        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('quiz1.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/process_data', methods=['POST','GET'])
def process_data():
    mb = request.form.get('nam')
    count = request.form.get('scor')
    roll = request.form.get('rol')
    sql='''insert into `sd`(name,roll,score)values(%s,%s,%s)'''
    v=[mb,roll,count]
    cursor.execute(sql,v)
    connection.commit()
    return render_template("thank.html")

connection.commit()

@app.route('/res',methods=['POST','GET'])
def res():
    data=[]

    sql="select * from `sd`"
    cursor.execute(sql)

    for i in cursor:
        data.append(list(i))

    return render_template("res.html",data=data)



if __name__ == '__main__':
    app.run(debug=True)
