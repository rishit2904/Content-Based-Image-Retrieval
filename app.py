from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
import os
from cbir import load_images_from_folder, extract_features, build_index, retrieve_similar_images, resize_image

app = Flask(__name__)
CORS(app)

IMAGE_FOLDER_CAR = 'car'
IMAGE_FOLDER_FLOWER = 'Flower'
IMAGE_DIR = '.' 

flower_images = load_images_from_folder(IMAGE_FOLDER_FLOWER, max_images=100)
car_images = load_images_from_folder(IMAGE_FOLDER_CAR)

flower_features = extract_features(flower_images, method='ORB')
car_features = extract_features(car_images, method='ORB')

flower_index, filtered_flower_features, flower_image_indices = build_index(flower_features)
car_index, filtered_car_features, car_image_indices = build_index(car_features)

@app.route('/search', methods=['POST'])
def search_similar_images():
    file = request.files.get('image')
    if not file:
        return jsonify({"error": "No image provided"}), 400

    file_bytes = np.frombuffer(file.read(), np.uint8)
    query_image = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)
    if query_image is None:
        return jsonify({"error": "Could not decode image"}), 400

    query_image_resized = resize_image(query_image)

    flower_matches = retrieve_similar_images(query_image_resized, filtered_flower_features, flower_index, flower_image_indices, method='ORB', top_n=3)
    car_matches = retrieve_similar_images(query_image_resized, filtered_car_features, car_index, car_image_indices, method='ORB', top_n=3)

    flower_distance = sum([cv2.norm(resize_image(cv2.imread(match)), query_image_resized, cv2.NORM_L2) for match in flower_matches])
    car_distance = sum([cv2.norm(resize_image(cv2.imread(match)), query_image_resized, cv2.NORM_L2) for match in car_matches])

    chosen_category = 'Flower' if flower_distance <= car_distance else 'car'
    similar_images = flower_matches if flower_distance <= car_distance else car_matches
    similar_images_paths = [{"path": f"/image/{chosen_category}/{os.path.basename(img_path)}"} for img_path in similar_images]

    if not similar_images_paths:
        return jsonify({"error": "No similar images found."}), 404

    return jsonify(similar_images_paths)

# @app.route('/image/<category>/<filename>')
# def get_image(category, filename):
#     folder = IMAGE_FOLDER_FLOWER if category == './Flower' else IMAGE_FOLDER_CAR
#     return send_from_directory(folder, filename)

@app.route('/image/<category>/<filename>')
def get_image(category, filename):
    # Ensure the correct directory structure
    path = os.path.join(IMAGE_DIR, category, filename)
    
    # Debug the path for each request
    print(f"Requested image path: {path}")
    
    if not os.path.exists(path):
        print(f"File Not Found: {path}")
        return "File Not Found", 404
    
    return send_from_directory(IMAGE_DIR, f"{category}/{filename}")



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
