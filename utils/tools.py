from PIL import Image

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