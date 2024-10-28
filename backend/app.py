from flask import Flask, request, send_file, jsonify
import cv2
import numpy as np
from scipy.spatial import Voronoi
import matplotlib.pyplot as plt
import os

app = Flask(__name__)

def generate_province_map(image_path):
    # Load the map image
    image = cv2.imread(image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Step 1: Create masks for land and water
    land_mask = cv2.inRange(image_rgb, (0, 50, 0), (150, 200, 150))
    water_mask = cv2.inRange(image_rgb, (0, 0, 100), (200, 255, 255))
    
    # Ignore legend areas (corners)
    h, w, _ = image.shape
    legend_mask = np.zeros((h, w), dtype=np.uint8)
    corner_size = int(0.1 * min(h, w))
    cv2.rectangle(legend_mask, (0, 0), (corner_size, corner_size), 255, -1)
    cv2.rectangle(legend_mask, (w - corner_size, 0), (w, corner_size), 255, -1)
    cv2.rectangle(legend_mask, (0, h - corner_size), (corner_size, h), 255, -1)
    cv2.rectangle(legend_mask, (w - corner_size, h - corner_size), (w, h), 255, -1)

    combined_land_mask = cv2.bitwise_and(land_mask, cv2.bitwise_not(legend_mask))

    # Step 2: Find contours for landmasses
    contours, _ = cv2.findContours(combined_land_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    seed_points = []
    for contour in contours:
        area = cv2.contourArea(contour)
        num_seeds = max(1, area // 50000)
        for _ in range(num_seeds):
            x, y, w, h = cv2.boundingRect(contour)
            seed_x = np.random.randint(x, x + w)
            seed_y = np.random.randint(y, y + h)
            if cv2.pointPolygonTest(contour, (seed_x, seed_y), False) >= 0:
                seed_points.append([seed_x, seed_y])

    # Create province map
    province_map = np.zeros_like(image_rgb)
    seed_points = np.array(seed_points)
    vor = Voronoi(seed_points)
    for region in vor.regions:
        if not -1 in region and region:
            poly_points = [vor.vertices[i] for i in region]
            poly_points = np.array([poly_points], dtype=np.int32)
            color = tuple(np.random.randint(0, 255, size=3).tolist())
            cv2.fillPoly(province_map, poly_points, color)
    
    # Save output image
    output_path = 'province_map.png'
    plt.imsave(output_path, province_map)
    return output_path

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        file_path = 'input_map.png'
        file.save(file_path)
        output_path = generate_province_map(file_path)
        return send_file(output_path, mimetype='image/png')

if __name__ == "__main__":
    app.run(debug=True)
