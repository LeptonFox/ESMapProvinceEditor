import cv2
import numpy as np
import matplotlib.pyplot as plt
import argparse
from scipy.spatial import Voronoi

def main(input_image_path, output_image_path):
    # Load the map image
    image = cv2.imread(input_image_path)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Step 1: Create masks for land and water based on color ranges
    # Define color ranges for land (greens, browns) and water (blues, teals, white)
    land_mask = cv2.inRange(image_rgb, (0, 50, 0), (150, 200, 150))  # Adjust for green and brown land colors
    water_mask = cv2.inRange(image_rgb, (0, 0, 100), (200, 255, 255))  # Adjust for blue and white water colors

    # Step 2: Remove areas that might be legends or external labels
    # Assuming legends are in the corners, we mask out the corners
    h, w, _ = image.shape
    legend_mask = np.zeros((h, w), dtype=np.uint8)
    corner_size = int(0.1 * min(h, w))  # Adjust the corner mask size as needed

    # Top-left, Top-right, Bottom-left, Bottom-right corners
    cv2.rectangle(legend_mask, (0, 0), (corner_size, corner_size), 255, -1)
    cv2.rectangle(legend_mask, (w - corner_size, 0), (w, corner_size), 255, -1)
    cv2.rectangle(legend_mask, (0, h - corner_size), (corner_size, h), 255, -1)
    cv2.rectangle(legend_mask, (w - corner_size, h - corner_size), (w, h), 255, -1)

    # Combine the land mask and remove legend areas
    combined_land_mask = cv2.bitwise_and(land_mask, cv2.bitwise_not(legend_mask))

    # Step 3: Segment land areas (using combined_land_mask) and find contours for landmasses
    contours, _ = cv2.findContours(combined_land_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    # Step 4: Place seed points within each landmass for province centers
    seed_points = []
    for contour in contours:
        area = cv2.contourArea(contour)
        num_seeds = max(1, area // 50000)  # Adjust based on desired province density

        for _ in range(num_seeds):
            x, y, w, h = cv2.boundingRect(contour)
            seed_x = np.random.randint(x, x + w)
            seed_y = np.random.randint(y, y + h)

            # Check if the point is within the landmass contour
            if cv2.pointPolygonTest(contour, (seed_x, seed_y), False) >= 0:
                seed_points.append([seed_x, seed_y])

    # Step 5: Create a blank image for province visualization
    province_map = np.zeros_like(image_rgb)

    # Step 6: Use Voronoi tessellation to divide the land based on seeds
    seed_points = np.array(seed_points)
    vor = Voronoi(seed_points)

    # Draw Voronoi regions for each seed
    for region in vor.regions:
        if not -1 in region and region:
            poly_points = [vor.vertices[i] for i in region]
            poly_points = np.array([poly_points], dtype=np.int32)

            color = tuple(np.random.randint(0, 255, size=3).tolist())
            cv2.fillPoly(province_map, poly_points, color)

    # Overlay province centers and labels
    for idx, (x, y) in enumerate(seed_points):
        cv2.circle(province_map, (x, y), 3, (255, 255, 255), -1)
        cv2.putText(province_map, f'Prov {idx+1}', (x + 5, y), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)

    # Save the output image
    plt.imsave(output_image_path, province_map)
    print(f"Province map saved to {output_image_path}")

if __name__ == "__main__":
    # Parse input and output file paths from command-line arguments
    parser = argparse.ArgumentParser(description="Generate provinces from a terraformed moon map.")
    parser.add_argument('input_image', type=str, help="Path to the input map image")
    parser.add_argument('output_image', type=str, help="Path to save the output province map")
    args = parser.parse_args()

    # Run main function with provided paths
    main(args.input_image, args.output_image)
