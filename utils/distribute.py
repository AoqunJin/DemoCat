import os
import cv2
from collections import defaultdict

def count_total_frames(folder_path):
    total_frames = 0
    frame_counts = defaultdict(int)
    video_extensions = ['.mp4', '.avi', '.mov', '.mkv']  # 可以根据需要添加更多视频格式

    for root, dirs, files in os.walk(folder_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in video_extensions):
                video_path = os.path.join(root, file)
                cap = cv2.VideoCapture(video_path)
                frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                total_frames += frame_count
                frame_counts[frame_count] += 1
                cap.release()

    return total_frames, frame_counts

def main():
    folder_path = input("请输入视频文件夹路径: ")
    total_frames, frame_counts = count_total_frames(folder_path)
    
    print(f"\n文件夹中视频的总帧数: {total_frames}")
    print("\n各视频帧数分布:")
    for frame_count, count in sorted(frame_counts.items()):
        print(f"帧数 {frame_count}: {count} 个视频")

if __name__ == "__main__":
    main()