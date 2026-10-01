#!/usr/bin/env python3
"""Extract key frames from final video for verification"""
import cv2

video = cv2.VideoCapture('wizard-final.mp4')
fps = video.get(cv2.CAP_PROP_FPS)
frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))

print(f"Video info: {frame_count} frames @ {fps} fps")

# Extract key frames: 0-1s, 3s (wave building), 5s (wave impact), 7s (logo reveal)
frame_numbers = [30, 90, 150, 210]
labels = ["0-1s: Wave building", "3s: Wave rising", "5s: Wave impact", "7s: Logo reveal"]

for i, (frame_num, label) in enumerate(zip(frame_numbers, labels)):
    video.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
    ret, frame = video.read()

    if ret:
        filename = f'verification_frame_{i+1:02d}_{label.replace(" ", "_").replace(":", "")}.jpg'
        cv2.imwrite(filename, frame)
        print(f"✓ {filename} ({label})")

video.release()
print("\nFrames ready for verification")
