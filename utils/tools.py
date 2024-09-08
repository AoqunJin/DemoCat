import numpy as np
from PIL import Image
import cv2

def resize_and_pad_to_square(img, target_size):
    # 获取图像的宽度和高度
    width, height = img.size
    
    # 计算放缩比例，确保较长边等于 target_size
    scale = target_size / max(width, height)
    new_width = int(width * scale)
    new_height = int(height * scale)
    
    # 放缩图像
    resized_img = img.resize((new_width, new_height), Image.LANCZOS)
    
    # 创建新的正方形画布
    new_img = Image.new('RGB', (target_size, target_size), (0, 0, 0))
    
    # 计算将放缩后的图像居中放置所需的偏移量
    left = (target_size - new_width) // 2
    top = (target_size - new_height) // 2
    
    # 将放缩后的图像粘贴到新画布上
    new_img.paste(resized_img, (left, top))
    
    return new_img

def center_crop_and_resize(image, size=224):
    # 获取图像的高度和宽度
    height, width = image.shape[:2]

    # 确定短边的长度
    short_edge = min(height, width)

    # 计算裁剪的起始点（中心裁剪）
    start_x = (width - short_edge) // 2
    start_y = (height - short_edge) // 2

    # 裁剪图像，生成正方形
    cropped_image = image[start_y:start_y + short_edge, start_x:start_x + short_edge]

    # 调整大小到指定大小
    resized_image = cv2.resize(cropped_image, (size, size))

    return resized_image

def trans(np_array):
    # 交换红色和蓝色通道
    # 红色通道：swapped_array[:, :, 0]
    # 蓝色通道：swapped_array[:, :, 2]    
    swapped_array = np.copy(np_array)
    swapped_array[:, :, [0, 2]] = swapped_array[:, :, [2, 0]]
    return swapped_array
