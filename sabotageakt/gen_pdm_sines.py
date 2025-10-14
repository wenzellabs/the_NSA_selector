#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# gen_pdm_sines.py
#
# Generate PDM sine wave binary files for NSA selector
# Sample rate: 25M/s, 4-bit resolution (nibble)
# PDM sine waves using pulse density modulation, LSB first, low nibble first
#

import argparse
import math
import random

def freq_from_note(note_number, base_freq=65.41):
    """Calculate frequency for a given note number starting from C2 (65.41 Hz)."""
    # Each semitone is 2^(1/12) times the previous frequency
    return base_freq * (2 ** (note_number / 12))

def generate_pdm_sine_wave(frequency, duration, sample_rate=25_000_000):
    """Generate PDM sine wave binary data."""
    # Each byte contains 2 samples (4-bit resolution), so we need half as many bytes
    num_samples = int(duration * sample_rate)
    num_bytes = num_samples // 2
    
    # Calculate samples per cycle and pre-compute one period
    samples_per_cycle = int(sample_rate / frequency)
    
    # Pre-calculate one period of PDM sine wave bytes
    period_bytes = samples_per_cycle // 2  # Convert samples to bytes
    if samples_per_cycle % 2 == 1:
        period_bytes += 1  # Round up if odd number of samples
    
    period_data = bytearray()
    
    for i in range(period_bytes):
        byte_value = 0
        
        for nibble in range(2):  # 2 nibbles per byte
            sample_index = i * 2 + nibble
            if sample_index >= samples_per_cycle:
                # Handle case where we have odd samples per cycle
                break
                
            # Calculate sine wave value at this sample point in the period
            phase = 2.0 * math.pi * sample_index / samples_per_cycle
            sine_value = math.sin(phase)  # -1 to +1
            
            # Convert sine to 0-1 range for PDM
            target_density = (sine_value + 1.0) / 2.0  # 0 to 1
            
            # Generate 4-bit PDM value (0-15)
            pdm_nibble = 0
            for bit in range(4):
                # PDM: compare target density with bit position threshold
                threshold = (bit + 0.5) / 4.0  # 0.125, 0.375, 0.625, 0.875
                if target_density > threshold:
                    pdm_nibble |= (1 << bit)  # LSB first
            
            # Pack nibbles: low nibble first
            if nibble == 0:
                byte_value = pdm_nibble  # Low nibble (bits 0-3)
            else:
                byte_value |= (pdm_nibble << 4)  # High nibble (bits 4-7)
        
        period_data.append(byte_value)
    
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
    parser = argparse.ArgumentParser(description="Generate PDM sine wave binary files for NSA selector")
    parser.add_argument('-d', '--duration', type=float, default=0.5, 
                        help="Duration of each file in seconds (default: 0.5)")
    args = parser.parse_args()
    
    sample_rate = 25_000_000  # 25M/s
    base_freq = 8.18  # MIDI note 0 frequency in Hz
    num_notes = 128  # Generate all 128 MIDI notes (0-127)
    
    print(f"Generating {num_notes} PDM sine wave files")
    print(f"Sample rate: {sample_rate:,} Hz")
    print(f"Duration: {args.duration} seconds")
    print(f"Base frequency (MIDI note 0): {base_freq} Hz")
    print(f"Frequency range: {base_freq:.2f} Hz to {freq_from_note(127, base_freq):.2f} Hz")
    print(f"Format: 4-bit PDM, LSB first, low nibble first")
    print()
    
    for note_num in range(num_notes):
        filename = f"sine_{note_num:03d}.raw"
        frequency = freq_from_note(note_num, base_freq)
        
        print(f"Generating {filename}: {frequency:.2f} Hz")
        
        # Generate PDM sine wave data
        wave_data = generate_pdm_sine_wave(frequency, args.duration, sample_rate)
        
        # Write binary file
        with open(filename, 'wb') as f:
            f.write(wave_data)
        
        file_size = len(wave_data)
        print(f"  -> {file_size:,} bytes written")
    
    print(f"\nGenerated {num_notes} files successfully!")

if __name__ == "__main__":
    main()