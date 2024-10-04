import cv2
import numpy as np


def pixel_to_latlng(pixel_coords, img_size, map_center, scale_factor, scale_factor_y):
    img_width, img_height = img_size
    latlng_coords = []
    
    for x, y in pixel_coords:
        # Инвертируем Y, потому что система координат карты обратная
        inverted_y = img_height - y
        
        lat = map_center[0] + (inverted_y - img_height / 2) * scale_factor_y
        lng = map_center[1] + (x - img_width / 2) * scale_factor
        
        latlng_coords.append([lat, lng])
    
    return latlng_coords

def make_txt_mask_of_radius(p, coords_psr, radius, result, center):
    kernel = np.ones((5, 5), np.uint8)  
    # Применение эрозии перед дилатацией для уменьшения артефактов
    result = cv2.erode(result, kernel, iterations=2)
    result = cv2.dilate(result, kernel, iterations=3)
    result = cv2.Canny(result, 100, 200)
    mask1 = np.zeros((result.shape[0]+2, result.shape[1]+2), np.uint8)
    cv2.floodFill(result, mask1, center, 255)

    p = p.split('.')[0].split('/')[1]
    contours, _ = cv2.findContours(result, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    contour = contours[0]

    coords = contour[:, 0, :].tolist()

    img_size = (result.shape[1], result.shape[0])

    map_center = coords_psr
    radius = radius 

    scale_factor = 0.000894 * 805/img_size[0] * radius/10
    scale_factor_y = 0.00045 * 486/img_size[1] * radius/10

    latlng_coords = pixel_to_latlng(coords, img_size, map_center, scale_factor, scale_factor_y)

    with open(f'./temp/{p}.txt', "w") as file:
        file.write(str(latlng_coords))