# Import required libraries
import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from skimage.io import imread
from skimage.transform import resize
from skimage.color import rgb2gray
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix, classification_report, accuracy_score
import pickle
import sys
from tkinter import Tk, filedialog
from urllib import request
from PIL import Image

# Create a directory to store the downloaded images
os.makedirs('Classification_Images_SouthIndian')

# Install bing_image_downloader package
!pip install bing_image_downloader

# Import images using bing downloader
from bing_image_downloader import downloader

# Define the target categories (South Indian food items)
Categories = ["idli", "dosa", "vada", "sambhar", "rasam", "poori", "chapathi", "briyani"]

# Download images for each category
for category in Categories:
    downloader.download(category, limit=30, output_dir="Classification_Images_SouthIndian", adult_filter_off=True)

# Load and preprocess the image data
target = []
flat_data = []
images = []
DataDirectory = 'Classification_Images_SouthIndian'

for category in Categories:
    target_class = Categories.index(category)
    path = os.path.join(DataDirectory, category)
    
    for img in os.listdir(path):
        img_array = imread(os.path.join(path, img))
        img_resized = resize(img_array, (150, 150, 3))
        flat_data.append(img_resized.flatten())
        images.append(img_resized)
        target.append(target_class)

flat_data = np.array(flat_data)
images = np.array(images)
target = np.array(target)

# Create a DataFrame for the image data
df = pd.DataFrame(flat_data)
df['Target'] = target

# Split the data into training and testing sets
x = df.iloc[:, :-1].values
y = df.iloc[:, -1].values
x_train, x_test, y_train, y_test = train_test_split(x, y, shuffle=True, test_size=0.3, random_state=109, stratify=y)

# Define the hyperparameters for the RandomForestClassifier
tuned_parameters = {'max_depth': [3, 5, 10, None],
                    'n_estimators': [10, 100, 200],
                    'max_features': [1, 3, 5, 7]}

# Create the RandomForestClassifier and apply GridSearchCV to find the best parameters
r_clf = RandomForestClassifier()
cv = GridSearchCV(r_clf, tuned_parameters, refit=True, verbose=3)
cv.fit(x_train, y_train)

# Print the best parameters and the model after hyperparameter tuning
print("Best parameters to apply are:", cv.best_params_)
r = cv.best_estimator_
print("Model after tuning is:\n", r)

# Make predictions on the test data
y_prediction = r.predict(x_test)

# Display evaluation metrics
print("Confusion matrix results:\n", confusion_matrix(y_prediction, y_test))
print("\nClassification report of the model:\n", classification_report(y_prediction, y_test))
print("Accuracy score:", 100 * accuracy_score(y_prediction, y_test))

# Save the trained model
pickle.dump(r, open("Classification_Model_SouthIndian.p", "wb"))
#pickle.load(open("Classification_Model_SouthIndian.p", "rb"))

test_model = pickle.load(open("Classification_Model_SouthIndian.p", "rb"))

#Provide the image path as a command-line argument
image_path = sys.argv[1]

url = input("Enter the URL of the image to test: ")

#Download and preprocess the input image
from io import BytesIO

response = request.urlopen(url)
img_data = response.read()
img = Image.open(BytesIO(img_data))
img_resized = resize(np.array(img), (150, 150, 3))
flat_data = np.array([img_resized.flatten()])

#Make predictions on the input image
y_output = test_model.predict(flat_data)
y_output = Categories[y_output[0]]

# Display the predicted output and the input image
print("Predicted output is:", y_output)
plt.imshow(img)
plt.axis('off')
plt.title("Predicted Output: " + y_output)
plt.show()
