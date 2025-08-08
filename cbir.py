import cv2
import numpy as np
from sklearn.neighbors import NearestNeighbors
import os
import glob

def load_images_from_folder(folder_path, max_images=None):
    images = []
    print(f"Loading images from: {folder_path}")
    for i, filename in enumerate(glob.glob(os.path.join(folder_path, "*.jpg"))):
        if max_images and i >= max_images:
            break
        img = cv2.imread(filename)
        if img is not None:
            images.append((filename, img))
    print(f"Total images loaded from {folder_path}: {len(images)}")
    return images

def extract_features(images, method='ORB'):
    feature_list = []
    for filename, img in images:
        descriptor = cv2.ORB_create() if method == 'ORB' else cv2.SIFT_create()
        keypoints, features = descriptor.detectAndCompute(img, None)
        if features is not None:
            feature_list.append((filename, features))
        else:
            print(f"No features found for image: {filename}")
    return feature_list

def build_index(features):
    feature_vectors = []
    image_indices = []
    for idx, (filename, f) in enumerate(features):
        if f is not None and len(f) > 0:
            feature_vectors.extend(f)
            image_indices.extend([idx] * len(f))
    if not feature_vectors:
        raise ValueError("No valid features found to build the index.")
    
    feature_vectors = np.array(feature_vectors)
    index = NearestNeighbors(n_neighbors=5, algorithm='brute', metric='euclidean')
    index.fit(feature_vectors)
    return index, features, image_indices

def resize_image(img, target_size=(100, 100)):
    return cv2.resize(img, target_size)

def retrieve_similar_images(query_image, feature_list, index, image_indices, method='ORB', top_n=3):
    descriptor = cv2.ORB_create() if method == 'ORB' else cv2.SIFT_create()
    _, query_features = descriptor.detectAndCompute(query_image, None)
    if query_features is None:
        print("No features found in the query image.")
        return []

    distances, indices = index.kneighbors(query_features)
    match_filenames = [feature_list[image_indices[i]][0] for i in indices.flatten()]
    unique_matches = list(dict.fromkeys(match_filenames))[:top_n]
    return unique_matches
