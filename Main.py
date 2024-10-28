import cv2
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import Voronoi, voronoi_plot_2d

# Load the map image
image = cv2.imread('/mnt/data/image.png')
image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Step 1: Create masks for land and water based on color ranges
# Define color ranges for land (greens, browns) and water (blues, teals, white)
land_mask = cv2.inRange(image_rgb, (0, 50, 0), (150, 200, 150))  # Adjust for green and brown
water_mask = cv2.inRange(image_rgb, (0, 0, 100), (200, 255, 255))  # Adjust for blue and white tones

# Step 2: Segment land areas (using land_mask) and find contours for landmasses
contours, _ = cv2.findContours(land_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

# Step 3: Place seed points within each landmass for province centers
# Generate seeds by finding centroids of contour areas or by random sampling within each landmass
seed_points = []
for contour in contours:
    # Calculate the number of seeds for each landmass based on area size
    area = cv2.contourArea(contour)
    num_seeds = max(1, area // 50000)  # Adjust based on desired province density

    for _ in range(num_seeds):
        # Generate random points within the bounding box of each contour
        x, y, w, h = cv2.boundingRect(contour)
        seed_x = np.random.randint(x, x + w)
        seed_y = np.random.randint(y, y + h)

        # Check if the point is within the landmass contour
        if cv2.pointPolygonTest(contour, (seed_x, seed_y), False) >= 0:
            seed_points.append([seed_x, seed_y])

# Step 4: Create a blank image for province visualization
province_map = np.zeros_like(image_rgb)

# Step 5: Use Voronoi tessellation to divide the land based on seeds
# Convert seed points to numpy array
seed_points = np.array(seed_points)
vor = Voronoi(seed_points)

# Draw Voronoi regions for each seed
for region in vor.regions:
    if not -1 in region and region:
        # Generate polygon for each region using vertices
        poly_points = [vor.vertices[i] for i in region]
        poly_points = np.array([poly_points], dtype=np.int32)

        # Fill the polygon with a random color
        color = tuple(np.random.randint(0, 255, size=3).tolist())
        cv2.fillPoly(province_map, poly_points, color)

# Step 6: Overlay province centers and labels
for idx, (x, y) in enumerate(seed_points):
    # Label each province center
    cv2.circle(province_map, (x, y), 3, (255, 255, 255), -1)
    cv2.putText(province_map, f'Prov {idx+1}', (x + 5, y), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255), 1)

# Display the province map
plt.imshow(province_map)
plt.axis('off')
plt.show()
