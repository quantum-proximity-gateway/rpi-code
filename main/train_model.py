import os
import pickle
import cv2
from imutils import paths
import face_recognition
def model_training(usernames):
    encodingsFile = "encodings.pickle"

    # If file exists, load it, else initialize empty lists
    if os.path.exists(encodingsFile):
        with open(encodingsFile, "rb") as f:
            data = pickle.load(f)
        knownEncodings = data.get("encodings", [])
        knownNames = data.get("names", [])
        print("[INFO] Loaded existing encodings from file.")
    else:
        knownEncodings = []
        knownNames = []
        print("[INFO] No existing encodings file found. Starting from scratch.")
    for user in usernames:
        imagePaths = list(paths.list_images(f"dataset/{user}"))
        print(f"[INFO] Found {len(imagePaths)} images to process.")

        # Process each image
        for (i, imagePath) in enumerate(imagePaths):
            print(f"[INFO] Processing image {i + 1}/{len(imagePaths)}")
            # Extract the person's name assuming the folder structure: dataset/<name>/<image_file>
            name = imagePath.split(os.path.sep)[-2]
            
            # Load the image, convert from BGR to RGB
            image = cv2.imread(imagePath)
            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Detect face locations in the image using the 'hog' model
            boxes = face_recognition.face_locations(rgb, model="hog")
            
            # Compute the facial embedding for each detected face
            encodings = face_recognition.face_encodings(rgb, boxes)
            
            # Loop over the encodings and update our list
            for encoding in encodings:
                knownEncodings.append(encoding)
                knownNames.append(name)

        print("[INFO] Serializing encodings...")

        # Save updated encodings back to the pickle file
        data = {"encodings": knownEncodings, "names": knownNames}
        with open(encodingsFile, "wb") as f:
            f.write(pickle.dumps(data))

        print(f"[INFO] Training complete. Updated encodings saved to '{encodingsFile}'")
