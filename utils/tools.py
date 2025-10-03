import numpy as np
from PIL import Image
import cv2


def resize_and_pad_to_square(img, target_size):
    # Get the width and height of the image
    width, height = img.size
    
    # Calculate the scaling ratio to ensure the longer edge is equal to target_size
    scale = target_size / max(width, height)
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    # Resize the image
    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
    
    # Create a new square canvas
    new_img = Image.new('RGB', (target_size, target_size), (0, 0, 0))
    
    # Calculate the offset to center the scaled image
    left = (target_size - new_width) // 2
    top = (target_size - new_height) // 2
    
    # Paste the scaled image onto the new canvas
    new_img.paste(resized_img, (left, top))
    
    return new_img


def center_crop_and_resize(image, size=256):
    # Get the height and width of the image
    height, width = image.shape[:2]

    # Calculate the shortest edge
    short_edge = min(height, width)

    # Calculate the start point of the cropped image
    start_x = (width - short_edge) // 2
    start_y = (height - short_edge) // 2

    # Crop the image, keeping only the center square
    cropped_image = image[start_y:start_y + short_edge, start_x:start_x + short_edge]

    # Change the size of the image
    resized_image = cv2.resize(cropped_image, (size, size))

    return resized_image
