#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# gen_squares.py
#
# Generate square wave binary files for NSA selector
# Sample rate: 25M/s, 4-bit resolution (nibble)
# Square waves contain only 0x00 or 0xFF values
#

import argparse
import math

def freq_from_note(note_number, base_freq=65.41):
    """Calculate frequency for a given note number starting from C2 (65.41 Hz)."""
    # Each semitone is 2^(1/12) times the previous frequency
    return base_freq * (2 ** (note_number / 12))

def generate_square_wave(frequency, duration, sample_rate=25_000_000):
    """Generate square wave binary data."""
    # Each byte contains 2 samples (4-bit resolution), so we need half as many bytes
    num_samples = int(duration * sample_rate)
    num_bytes = num_samples // 2
    samples_per_cycle = int(sample_rate / frequency)
    half_cycle = samples_per_cycle // 2
    
    # Pre-calculate one period of square wave bytes
    period_bytes = samples_per_cycle // 2  # Convert samples to bytes
    if samples_per_cycle % 2 == 1:
        period_bytes += 1  # Round up if odd number of samples
    
    period_data = bytearray()
    
    for i in range(period_bytes):
        # Each byte represents 2 samples, so multiply by 2 to get sample position
        sample_position = i * 2
        if sample_position < half_cycle:
            period_data.append(0xFF)  # High part of square wave (both nibbles high)
        else:
            period_data.append(0x00)  # Low part of square wave (both nibbles low)
    
    # Now repeat the period to fill the required duration
    wave_data = bytearray()
    bytes_written = 0
    
    while bytes_written < num_bytes:
        # Copy as much of the period as we can fit
        bytes_to_copy = min(len(period_data), num_bytes - bytes_written)
        wave_data.extend(period_data[:bytes_to_copy])
        bytes_written += bytes_to_copy
    
    return wave_data

def main():
    parser = argparse.ArgumentParser(description="Generate square wave binary files for NSA selector")
    parser.add_argument('-d', '--duration', type=float, default=0.5, 
                        help="Duration of each file in seconds (default: 0.5)")
    args = parser.parse_args()
    
    sample_rate = 25_000_000  # 25M/s
    base_freq = 8.18  # MIDI note 0 frequency in Hz
    num_notes = 128  # Generate all 128 MIDI notes (0-127)
    
    print(f"Generating {num_notes} square wave files")
    print(f"Sample rate: {sample_rate:,} Hz")
    print(f"Duration: {args.duration} seconds")
    print(f"Base frequency (MIDI note 0): {base_freq} Hz")
    print(f"Frequency range: {base_freq:.2f} Hz to {freq_from_note(127, base_freq):.2f} Hz")
    print()
    
    for note_num in range(num_notes):
        filename = f"square_{note_num:03d}.raw"
        frequency = freq_from_note(note_num, base_freq)
        
        print(f"Generating {filename}: {frequency:.2f} Hz")
        
        # Generate square wave data
        wave_data = generate_square_wave(frequency, args.duration, sample_rate)
        
        # Write binary file
        with open(filename, 'wb') as f:
            f.write(wave_data)
        
        file_size = len(wave_data)
        print(f"  -> {file_size:,} bytes written")
    
    print(f"\nGenerated {num_notes} files successfully!")

if __name__ == "__main__":
    main()