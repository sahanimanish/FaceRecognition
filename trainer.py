import math
from sklearn import neighbors
import os
import os.path
import pickle
from PIL import Image, ImageDraw
import face_recognition
# from face_recognition.face_recognition_cli import image_files_in_folder

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}


def train(model_save_path=None, n_neighbors=None, knn_algo='ball_tree', verbose=False):
    
    
    X = []
    Y = []
    path='./Dataset/'
    for class_dir in os.listdir(path):
        if not os.path.isdir(os.path.join(path, class_dir)):    
             continue
        for img_path in os.listdir(os.path.join(path, class_dir)):
            
            image = face_recognition.load_image_file(os.path.join(path, class_dir,img_path))
            face_bounding_boxes = face_recognition.face_locations(image)

            if len(face_bounding_boxes) != 1:
                print("Image {} not suitable for training: {}".format(img_path, "Didn't find a face" if len(face_bounding_boxes) < 1 else "Found more than one face"))

            else:
                  X.append(face_recognition.face_encodings(image, known_face_locations=face_bounding_boxes)[0])
                  Y.append(class_dir)
        print(class_dir)
    # x=np.array(X)
    # y=np.array(Y)
    # np.save('./classes/class_data.npy',x)
    # np.save('./labels/labels_data.npy',y)
    # return x,y

    # Determine how many neighbors to use for weighting in the KNN classifier
    if n_neighbors is None:
        n_neighbors = int(round(math.sqrt(len(X))))
        if verbose:
            print("Chose n_neighbors automatically:", n_neighbors)

    # Create and train the KNN classifier
    knn_clf = neighbors.KNeighborsClassifier(n_neighbors=n_neighbors, algorithm=knn_algo, weights='distance')
    knn_clf.fit(X, Y)

    # Save the trained KNN classifier
    if model_save_path is not None:
        with open(model_save_path, 'wb') as f:
            pickle.dump(knn_clf, f)

    return knn_clf

