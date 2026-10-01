#!/usr/bin/env python3
"""
Generate WIZARD brand cinematic animation.
Creates ocean wave sequence with 3D logo reveal.
Output: MP4 vertical (9:16) suitable for Reels/Stories.
"""

import cv2
import numpy as np
from PIL import Image
import math
import os

# Configuration
OUTPUT_WIDTH = 1080
OUTPUT_HEIGHT = 1920
FPS = 30
TOTAL_SECONDS = 9
TOTAL_FRAMES = FPS * TOTAL_SECONDS

# Color palette
DARK_BROWN = (40, 60, 100)  # BGR format (inverted for OpenCV)
OCEAN_BLUE = (150, 100, 50)  # Teal-blue ocean
OCEAN_DEEP = (200, 120, 60)  # Deep ocean tone
FOAM_WHITE = (255, 255, 240)
GOLDEN_LIGHT = (180, 200, 255)  # Warm sunset light

class WaveSimulation:
    """Simple sine-wave based ocean animation"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.time = 0

    def generate_wave_surface(self, t, num_waves=3):
        """Generate water surface with wave interference pattern"""
        surface = np.zeros((self.height, self.width), dtype=np.float32)

        for x in range(self.width):
            y_wave = 0
            # Multiple sine waves for organic motion
            y_wave += 100 * math.sin((x / 150 + t * 0.05) * 2 * math.pi)
            y_wave += 60 * math.sin((x / 200 + t * 0.03) * 2 * math.pi + 1)
            y_wave += 40 * math.sin((x / 100 + t * 0.07) * 2 * math.pi + 2)

            # Increasing amplitude toward breaking point (frames 80-150)
            wave_intensity = min(t / 120, 1.0) if t < 120 else max((180 - t) / 80, 0)
            y_wave *= (1 + wave_intensity * 2)

            surface[:, x] = y_wave

        return surface

    def generate_frame(self, frame_idx):
        """Create one frame of wave animation"""
        t = frame_idx

        # Create base ocean gradient
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)

        # Sky to water gradient (top half is sky, bottom is water)
        for y in range(self.height):
            if y < self.height * 0.3:
                # Sky: light blue to golden
                ratio = y / (self.height * 0.3)
                b = int(200 * (1 - ratio) + 150 * ratio)
                g = int(180 * (1 - ratio) + 140 * ratio)
                r = int(160 * (1 - ratio) + 180 * ratio)
            else:
                # Ocean gradient: warm teal to deep blue
                ratio = (y - self.height * 0.3) / (self.height * 0.7)
                b = int(150 - ratio * 50)
                g = int(100 + ratio * 30)
                r = int(50 + ratio * 100)

            frame[y, :] = [b, g, r]

        # Wave surface
        wave_surface = self.generate_wave_surface(t)

        # Draw wave as a dynamic curve
        horizon_y = int(self.height * 0.5)

        for x in range(0, self.width, 5):
            x_idx = min(x, self.width - 1)
            wave_height = wave_surface[0, x_idx]
            wave_y = int(horizon_y - wave_height)

            # Wave line with thickness
            cv2.line(frame, (x, max(0, wave_y - 5)), (x + 5, max(0, wave_y - 5)),
                    FOAM_WHITE, 2)

        # Add foam and spray (frames 60-150)
        if 60 <= t <= 150:
            spray_intensity = min((t - 60) / 30, 1.0, (150 - t) / 50)
            num_spray = int(spray_intensity * 200)

            # Random water droplets
            np.random.seed(frame_idx)
            for _ in range(num_spray):
                x = np.random.randint(0, self.width)
                y = np.random.randint(horizon_y - 200, horizon_y + 100)
                size = np.random.randint(1, 4)
                alpha = np.random.randint(100, 255)
                cv2.circle(frame, (x, y), size, FOAM_WHITE, -1)

        # Add light rays (sunset effect)
        if 60 <= t <= 200:
            for i in range(5):
                start_x = int(self.width * (0.3 + i * 0.15) + np.sin(t * 0.01 + i) * 50)
                cv2.line(frame, (start_x, 0),
                        (start_x + int(100 * np.cos(t * 0.005)), self.height // 2),
                        GOLDEN_LIGHT, 1)

        return frame

class LogoCompositor:
    """Handle 3D logo positioning and animation"""
    def __init__(self, logo_path, width, height):
        self.width = width
        self.height = height
        self.logo = Image.open(logo_path).convert('RGBA')
        self.logo_array = np.array(self.logo)

    def get_logo_frame(self, frame_idx, total_frames):
        """Generate logo frame with animation (rotation + scale + position)"""
        # Logo appears around frame 150, fully visible at frame 180
        if frame_idx < 150:
            return None  # Logo not visible yet

        # Animation parameters
        reveal_progress = min((frame_idx - 150) / 30, 1.0)  # 0->1 over 30 frames
        rotation = reveal_progress * 20  # 0-20 degree rotation
        scale = 0.5 + reveal_progress * 0.3  # Scale up from 0.5 to 0.8
        opacity = int(255 * reveal_progress)  # Fade in

        # Resize logo
        new_size = int(self.logo.width * scale)
        logo_resized = self.logo.resize((new_size, new_size), Image.Resampling.LANCZOS)

        # Rotate logo
        logo_rotated = logo_resized.rotate(-rotation, expand=True, resample=Image.Resampling.BICUBIC)

        # Adjust opacity
        alpha = logo_rotated.split()[3]
        alpha = alpha.point(lambda p: int(p * opacity / 255))
        logo_rotated.putalpha(alpha)

        # Center position with slight bob motion (floating effect)
        bob = math.sin(frame_idx * 0.02) * 10
        x_pos = (self.width - logo_rotated.width) // 2
        y_pos = int((self.height - logo_rotated.height) // 2 + bob)

        return (logo_rotated, (x_pos, y_pos))

    def composite_logo(self, frame, frame_idx, total_frames):
        """Composite logo onto frame"""
        logo_data = self.get_logo_frame(frame_idx, total_frames)
        if logo_data is None:
            return frame

        logo_pil, (x, y) = logo_data

        # Ensure positions are within bounds
        x = max(0, x)
        y = max(0, y)

        # Crop if necessary
        x_end = min(x + logo_pil.width, self.width)
        y_end = min(y + logo_pil.height, self.height)

        if x_end <= x or y_end <= y:
            return frame

        # Convert frame to PIL for compositing
        frame_pil = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))

        # Crop logo if it exceeds bounds
        logo_crop = logo_pil.crop((0, 0, x_end - x, y_end - y))

        # Composite
        frame_pil.paste(logo_crop, (x, y), logo_crop)

        # Convert back to OpenCV format
        return cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGB2BGR)

def main():
    print("[WIZARD Cinematic Animation]")
    print(f"Resolution: {OUTPUT_WIDTH}×{OUTPUT_HEIGHT} (9:16 vertical)")
    print(f"Duration: {TOTAL_SECONDS}s @ {FPS}fps = {TOTAL_FRAMES} frames")
    print()

    # Initialize generators
    wave_sim = WaveSimulation(OUTPUT_WIDTH, OUTPUT_HEIGHT)
    logo_compositor = LogoCompositor('wizard-logo-transparent.png', OUTPUT_WIDTH, OUTPUT_HEIGHT)

    # Setup video writer
    output_path = 'wizard-animation.mp4'
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(output_path, fourcc, FPS, (OUTPUT_WIDTH, OUTPUT_HEIGHT))

    print(f"Rendering {TOTAL_FRAMES} frames...")

    # Render frames
    for frame_idx in range(TOTAL_FRAMES):
        # Generate wave frame
        frame = wave_sim.generate_frame(frame_idx)

        # Composite logo
        frame = logo_compositor.composite_logo(frame, frame_idx, TOTAL_FRAMES)

        # Add watermark info
        if frame_idx < 30:
            cv2.putText(frame, "WIZARD", (50, 100), cv2.FONT_HERSHEY_SIMPLEX,
                       1.5, (255, 255, 255), 2)

        # Write frame
        writer.write(frame)

        # Progress
        if (frame_idx + 1) % 30 == 0:
            print(f"  Frame {frame_idx + 1}/{TOTAL_FRAMES}")

    writer.release()
    print(f"\n✓ Video saved: {output_path}")
    print(f"  Size: {os.path.getsize(output_path) / (1024*1024):.1f} MB")

    return output_path

if __name__ == '__main__':
    main()
