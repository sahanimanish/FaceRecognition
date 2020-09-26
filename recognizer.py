import math
from sklearn import neighbors
import os
import os.path
import pickle
from PIL import Image, ImageDraw
import cv2
import face_recognition

knn_clf=None

with open("trained_knn_model.clf", 'rb') as f:        
    knn_clf = pickle.load(f)

def updateModel():
    with open("trained_knn_model.clf", 'rb') as f:        
        knn_clf = pickle.load(f)

def predict(X_img,model_path=None, distance_threshold=0.6):
    # X_img = face_recognition.load_image_file(X_img_path)
    small_frame = cv2.resize(X_img, (0, 0), fx=0.25, fy=0.25)
    X_face_locations = face_recognition.face_locations(small_frame)

    # If no faces are found in the image, return an empty result.
    if len(X_face_locations) == 0:
        return []

    # Find encodings for faces in the test iamge
    faces_encodings = face_recognition.face_encodings(small_frame, known_face_locations=X_face_locations)

    # Use the KNN model to find the best matches for the test face
    closest_distances = knn_clf.kneighbors(faces_encodings, n_neighbors=1)
    are_matches = [closest_distances[0][i][0] <= distance_threshold for i in range(len(X_face_locations))]

    # Predict classes and remove classifications that aren't within the threshold
    return [(pred, loc) if rec else ("unknown", loc) for pred, loc, rec in zip(knn_clf.predict(faces_encodings), X_face_locations, are_matches)]



def recognize(img):
    predictions=predict(img,model_path="trained_knn_model.clf")
    print(predictions)
    if(len(predictions)==0):
        return img
    for name, (y1, x2, y2, x1) in predictions:
        y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
        cv2.rectangle(img,(x1,y1),(x2,y2),(0,255,0),2)
        cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
        cv2.putText(img,name.upper(),(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
    return img