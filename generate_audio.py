#!/usr/bin/env python3
"""
Generate cinematic ocean audio for WIZARD animation.
Creates: rising ocean ambience + wave impact + settling water + finale.
"""

import numpy as np
import struct
import math

SAMPLE_RATE = 48000
DURATION = 9  # seconds
OUTPUT_FILE = 'wizard-audio.wav'

def write_wav(filename, samples, sample_rate=SAMPLE_RATE):
    """Write audio samples to WAV file"""
    # Ensure samples are in [-1, 1] range
    samples = np.clip(samples, -1, 1)

    # Convert to 16-bit PCM
    samples_16bit = np.int16(samples * 32767)

    # WAV header
    num_samples = len(samples_16bit)
    num_channels = 1
    bytes_per_sample = 2
    byte_rate = sample_rate * num_channels * bytes_per_sample
    block_align = num_channels * bytes_per_sample

    with open(filename, 'wb') as f:
        # RIFF header
        f.write(b'RIFF')
        f.write(struct.pack('<I', 36 + num_samples * bytes_per_sample))
        f.write(b'WAVE')

        # fmt subchunk
        f.write(b'fmt ')
        f.write(struct.pack('<I', 16))
        f.write(struct.pack('<H', 1))  # PCM
        f.write(struct.pack('<H', num_channels))
        f.write(struct.pack('<I', sample_rate))
        f.write(struct.pack('<I', byte_rate))
        f.write(struct.pack('<H', block_align))
        f.write(struct.pack('<H', 16))  # bits per sample

        # data subchunk
        f.write(b'data')
        f.write(struct.pack('<I', num_samples * bytes_per_sample))
        f.write(samples_16bit.tobytes())

def generate_ocean_ambience(duration, start_time=0, intensity=0.3):
    """Generate base ocean ambience (wind, water)"""
    t = np.linspace(start_time, start_time + duration, int(SAMPLE_RATE * duration))

    # Multiple low-frequency sine waves (ocean rumble)
    bass = (0.2 * np.sin(2 * np.pi * 40 * t) +  # 40 Hz
            0.15 * np.sin(2 * np.pi * 65 * t) +  # 65 Hz
            0.1 * np.sin(2 * np.pi * 100 * t))   # 100 Hz

    # Higher frequency noise (wind, wave hiss)
    noise = np.random.randn(len(t)) * 0.1

    # Combine
    audio = (bass + noise) * intensity

    return audio, t

def generate_wave_impact(duration=0.5, delay=2.5, intensity=1.0):
    """Generate wave breaking impact sound"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))

    # Deep impact (rising frequency sweep)
    freq_start = 120
    freq_end = 80
    freq = freq_start - (freq_start - freq_end) * (t / duration)

    # Sine wave with envelope
    envelope = np.exp(-t * 3) * (1 - t / duration)
    impact = np.sin(2 * np.pi * freq * t) * envelope * intensity * 0.5

    # Add transient click (water splash)
    click = np.exp(-t * 50) * np.sin(2 * np.pi * 200 * t) * 0.3

    return impact + click, t

def generate_spray_sounds(duration=1.5, delay=3.0):
    """Generate water spray/droplet sounds"""
    t = np.linspace(0, duration, int(SAMPLE_RATE * duration))

    # Multiple high-frequency tones (spray)
    spray = (0.08 * np.sin(2 * np.pi * 400 * t) +
             0.06 * np.sin(2 * np.pi * 530 * t) +
             0.05 * np.sin(2 * np.pi * 720 * t))

    # Decay envelope
    envelope = np.exp(-t * 1.5)

    return spray * envelope * 0.3, t

def generate_settling_water(duration=2.0, start_time=4.5):
    """Generate settling water sound (post-splash)"""
    t = np.linspace(start_time, start_time + duration, int(SAMPLE_RATE * duration))

    # Gentle low frequency (water settling)
    settling = (0.12 * np.sin(2 * np.pi * 50 * t) +
                0.08 * np.sin(2 * np.pi * 75 * t))

    # Add subtle noise
    noise = np.random.randn(len(t)) * 0.05

    # Fade in then out
    envelope = np.minimum(t / 0.5, 1.0) * np.maximum((start_time + duration - t) / 0.8, 0)

    return (settling + noise) * envelope * 0.2, t

def generate_ocean_finale(duration=2.0, start_time=7.0):
    """Generate final ocean ambience (calm, settling)"""
    t = np.linspace(start_time, start_time + duration, int(SAMPLE_RATE * duration))

    # Soft ocean breeze
    breeze = (0.1 * np.sin(2 * np.pi * 35 * t) +
              0.08 * np.sin(2 * np.pi * 52 * t + 1) +
              0.06 * np.sin(2 * np.pi * 78 * t + 2))

    # Soft noise (water lapping)
    noise = np.random.randn(len(t)) * 0.08

    # Fade out over time
    envelope = np.maximum((start_time + duration - t) / duration, 0)

    return (breeze + noise) * envelope * 0.15, t

def main():
    print("[Generating Ocean Soundtrack for WIZARD]")
    print(f"Duration: {DURATION}s")
    print(f"Sample rate: {SAMPLE_RATE} Hz")
    print()

    total_samples = int(SAMPLE_RATE * DURATION)
    audio = np.zeros(total_samples)

    # Timeline breakdown:
    # 0-2.5s: Rising ocean ambience (wave building)
    print("Generating: rising ocean ambience...")
    ambience1, _ = generate_ocean_ambience(2.5, intensity=0.25)
    audio[:len(ambience1)] += ambience1

    # 2.5-3.0s: Wave building (intensify)
    print("Generating: wave intensification...")
    ambience2, _ = generate_ocean_ambience(0.5, start_time=2.5, intensity=0.35)
    audio[int(2.5*SAMPLE_RATE):int(3*SAMPLE_RATE)] += ambience2

    # 3.0-3.5s: WAVE IMPACT
    print("Generating: wave breaking impact...")
    impact, _ = generate_wave_impact(duration=0.5, intensity=1.0)
    audio[int(3*SAMPLE_RATE):int(3*SAMPLE_RATE)+len(impact)] += impact

    # 3.5-5.0s: Water spray and settling
    print("Generating: water spray...")
    spray, _ = generate_spray_sounds(duration=1.5, delay=3.0)
    audio[int(3.5*SAMPLE_RATE):int(3.5*SAMPLE_RATE)+len(spray)] += spray

    # 4.5-6.5s: Settling water
    print("Generating: settling water...")
    settling, _ = generate_settling_water(duration=2.0, start_time=4.5)
    audio[int(4.5*SAMPLE_RATE):int(4.5*SAMPLE_RATE)+len(settling)] += settling

    # 6.5-9.0s: Final ocean ambience (calm, logo appearing)
    print("Generating: final ocean ambience...")
    finale, _ = generate_ocean_finale(duration=2.5, start_time=6.5)
    audio[int(6.5*SAMPLE_RATE):int(6.5*SAMPLE_RATE)+len(finale)] += finale

    # Normalize to prevent clipping
    max_val = np.max(np.abs(audio))
    if max_val > 1.0:
        audio /= max_val

    # Smooth fade in/out
    fade_samples = int(0.1 * SAMPLE_RATE)
    audio[:fade_samples] *= np.linspace(0, 1, fade_samples)
    audio[-fade_samples:] *= np.linspace(1, 0, fade_samples)

    # Write to file
    print(f"\nWriting audio file: {OUTPUT_FILE}")
    write_wav(OUTPUT_FILE, audio)

    print(f"✓ Audio generated: {OUTPUT_FILE}")
    print(f"  Duration: {DURATION}s")
    print(f"  Peak amplitude: {max_val:.2f}")

if __name__ == '__main__':
    main()
