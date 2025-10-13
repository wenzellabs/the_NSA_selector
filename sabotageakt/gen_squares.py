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
    
    # Generate square wave: 0xFF for first half of cycle, 0x00 for second half
    wave_data = bytearray()
    
    for i in range(num_bytes):
        # Each byte represents 2 samples, so multiply by 2 to get sample position
        sample_position = i * 2
        cycle_position = sample_position % samples_per_cycle
        if cycle_position < half_cycle:
            wave_data.append(0xFF)  # High part of square wave (both nibbles high)
        else:
            wave_data.append(0x00)  # Low part of square wave (both nibbles low)
    
    return wave_data

def main():
    parser = argparse.ArgumentParser(description="Generate square wave binary files for NSA selector")
    parser.add_argument('-n', '--num-notes', type=int, default=36, 
                        help="Number of note files to generate (default: 36)")
    parser.add_argument('-d', '--duration', type=float, default=0.5, 
                        help="Duration of each file in seconds (default: 0.5)")
    args = parser.parse_args()
    
    sample_rate = 25_000_000  # 25M/s
    base_freq = 65.41  # C2 frequency in Hz
    
    print(f"Generating {args.num_notes} square wave files")
    print(f"Sample rate: {sample_rate:,} Hz")
    print(f"Duration: {args.duration} seconds")
    print(f"Base frequency (C2): {base_freq} Hz")
    print()
    
    for note_num in range(args.num_notes):
        filename = f"note_{note_num:03d}.raw"
        frequency = freq_from_note(note_num, base_freq)
        
        print(f"Generating {filename}: {frequency:.2f} Hz")
        
        # Generate square wave data
        wave_data = generate_square_wave(frequency, args.duration, sample_rate)
        
        # Write binary file
        with open(filename, 'wb') as f:
            f.write(wave_data)
        
        file_size = len(wave_data)
        print(f"  -> {file_size:,} bytes written")
    
    print(f"\nGenerated {args.num_notes} files successfully!")

if __name__ == "__main__":
    main()