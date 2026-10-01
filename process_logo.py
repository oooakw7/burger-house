#!/usr/bin/env python3
"""
Process WIZARD logo: remove background, create PNG with transparency
and prepare for 3D composition.
"""

from PIL import Image
import numpy as np

# Load logo
img = Image.open('wizard-logo.png')
img_rgb = img.convert('RGB')
img_array = np.array(img_rgb)

# Convert to HSV for better color separation
from PIL import ImageOps
img_hsv = img.convert('HSV') if img.mode == 'RGB' else img

# Create mask based on gray background (threshold approach)
# Background is light gray (~220, 220, 220)
# Logo is dark brown (~80-100, 60-80, 40-60)

# Use color distance to identify background
gray_bg = np.array([220, 220, 220])
distance = np.linalg.norm(img_array - gray_bg, axis=2)

# Background pixels are close to gray (distance < 30)
mask = distance > 25  # Keep logo, remove background

# Create RGBA image
img_rgba = img.convert('RGBA')
alpha = Image.new('L', img_rgba.size, 0)
alpha_array = np.array(alpha)
alpha_array[mask] = 255  # Logo gets alpha 255
alpha = Image.fromarray(alpha_array, 'L')
img_rgba.putalpha(alpha)

# Save transparent version
img_rgba.save('wizard-logo-transparent.png')
print("✓ Created: wizard-logo-transparent.png (RGBA with transparency)")

# Also create a version with slight padding for 3D render
# Add 10% padding around the logo
pad = 20
new_size = (img_rgba.width + pad*2, img_rgba.height + pad*2)
img_padded = Image.new('RGBA', new_size, (0, 0, 0, 0))
img_padded.paste(img_rgba, (pad, pad), img_rgba)
img_padded.save('wizard-logo-padded.png')
print("✓ Created: wizard-logo-padded.png (padded version for 3D)")

# Print info
print(f"\nLogo dimensions: {img.width} × {img.height}px")
print(f"Background color: light gray (~220, 220, 220)")
print(f"Logo color: dark brown (~80-100, 60-80, 40-60)")
print(f"\nReady for 3D composition and video generation.")
