import face_recognition
import cv2
import numpy as np
from picamera2 import Picamera2
import time
import sys
import os

class FaceRecognizer:
    def __init__(self, data, cv_scaler=8):
        self.known_face_encodings = data["encodings"]
        self.known_face_names = data["names"]
        self.cv_scaler = cv_scaler

        # Initialize the camera
        self.picam2 = Picamera2()
        self.picam2.configure(self.picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (1280, 720)}))
        self.picam2.start()

        # Initialize other variables
        self.face_locations = []
        self.face_encodings = []
        self.face_names = []
        self.frame_count = 0
        self.start_time = time.time()
        self.fps = 0

    def process_frame(self, frame, person_checking_name):
        # Resize the frame using cv_scaler to increase performance
        resized_frame = cv2.resize(frame, (0, 0), fx=(1/self.cv_scaler), fy=(1/self.cv_scaler))
        rgb_resized_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        
        # Find faces and encodings in the current frame
        self.face_locations = face_recognition.face_locations(rgb_resized_frame)
        self.face_encodings = face_recognition.face_encodings(rgb_resized_frame, self.face_locations, model='large')
        self.face_names = []
        
        for face_encoding in self.face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"
            
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]
            self.face_names.append(name)

        person_checking_found = person_checking_name in self.face_names
        return frame, person_checking_found

    def draw_results(self, frame):
        for (top, right, bottom, left), name in zip(self.face_locations, self.face_names):
            top *= self.cv_scaler
            right *= self.cv_scaler
            bottom *= self.cv_scaler
            left *= self.cv_scaler

            cv2.rectangle(frame, (left, top), (right, bottom), (244, 42, 3), 3)
            cv2.rectangle(frame, (left - 3, top - 35), (right + 3, top), (244, 42, 3), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, top - 6), font, 1.0, (255, 255, 255), 1)
        
        return frame

    def calculate_fps(self):
        self.frame_count += 1
        elapsed_time = time.time() - self.start_time
        if elapsed_time > 1:
            self.fps = self.frame_count / elapsed_time
            self.frame_count = 0
            self.start_time = time.time()
        return self.fps

    def main_loop(self, list_of_names):
        print('Facial recognition stage')
        if not list_of_names:
            return None
        
        start_time_loop = time.time()
        while time.time() - start_time_loop < 2:
            frame = self.picam2.capture_array()
            person_found = False
            processed_frame = None

            for name in list_of_names:
                processed_frame, person_checking_found = self.process_frame(frame, name)
                if person_checking_found:
                    person_found = True
                    print(name, "was found.")
                    return name

            if person_found:
                display_frame = self.draw_results(processed_frame)
                current_fps = self.calculate_fps()
                cv2.putText(display_frame, f"FPS: {current_fps:.1f}", 
                            (display_frame.shape[1] - 150, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow('Video', display_frame)

                if cv2.waitKey(1) == ord("q"):
                    break

        cv2.destroyAllWindows()
        return None