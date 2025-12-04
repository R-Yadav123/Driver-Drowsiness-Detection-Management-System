# This file is the image classification machine learning model.
# Looking down --> distracted/drowsy, looking up --> alert/attentive
# This was developed with the assistance of artificial intelligence
import cv2
import mediapipe as mp
import time
import numpy as np

# Mediapipe initialization
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5,
                                  min_tracking_confidence=0.5)

# Eye aspect ratio
def eye_aspect_ratio(eye_landmarks):
    p2_minus_p6 = np.linalg.norm(np.array([eye_landmarks[1].x, eye_landmarks[1].y]) -
                                 np.array([eye_landmarks[5].x, eye_landmarks[5].y]))
    p3_minus_p5 = np.linalg.norm(np.array([eye_landmarks[2].x, eye_landmarks[2].y]) -
                                 np.array([eye_landmarks[4].x, eye_landmarks[4].y]))
    p1_minus_p4 = np.linalg.norm(np.array([eye_landmarks[0].x, eye_landmarks[0].y]) -
                                 np.array([eye_landmarks[3].x, eye_landmarks[3].y]))
    return (p2_minus_p6 + p3_minus_p5) / (2.0 * p1_minus_p4)

# VERY ACCURATE head-down detector
def get_down_score(landmarks):
    nose = landmarks[1]

    # eyelid points
    eye_top_left = landmarks[159]
    eye_top_right = landmarks[386]
    eye_mid_y = (eye_top_left.y + eye_top_right.y) / 2

    forehead = landmarks[10]

    pitch1 = nose.y - eye_mid_y

    pitch2 = eye_mid_y

    pitch3 = forehead.y - eye_mid_y

    down_score = pitch1 + pitch2 + pitch3
    return down_score

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [263, 387, 385, 362, 380, 373]

EAR_THRESHOLD = 0.012
EYES_CLOSED_TIME = 10

# Auto-calibration
calibration_values = []
calibration_start = time.time()
neutral_down_score = None
CALIBRATION_TIME = 2.0

eye_closed_start = None
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(frame_rgb)

    status = "Attentive"
    color = (0, 255, 0)

    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark

        # compute down score
        down_score = get_down_score(landmarks)
        print("Down Score:", down_score)

        # calibration phase
        if neutral_down_score is None:
            calibration_values.append(down_score)

            if time.time() - calibration_start >= CALIBRATION_TIME:
                neutral_down_score = np.mean(calibration_values)
                print("Neutral calibrated score:", neutral_down_score)
            
            cv2.putText(frame, "Calibrating posture...", (30, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 0), 3)
            cv2.imshow("Attention Monitor", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            continue

        # eye blinking logic
        left_eye = [landmarks[i] for i in LEFT_EYE]
        right_eye = [landmarks[i] for i in RIGHT_EYE]
        avg_ear = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0

        if avg_ear < EAR_THRESHOLD:
            if eye_closed_start is None:
                eye_closed_start = time.time()
        else:
            eye_closed_start = None

        eyes_closed_long = (eye_closed_start is not None and 
                            time.time() - eye_closed_start > EYES_CLOSED_TIME)

        # THRESHOLD for down detection
        DOWN_THRESHOLD = 0.015  # sensitivity control

        if down_score > neutral_down_score + DOWN_THRESHOLD or eyes_closed_long:
            status = "Distracted"
            color = (0, 0, 255)

    cv2.putText(frame, status, (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, color, 3)
    cv2.imshow("Attention Monitor", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
