#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# sabotageakt.py
#
# this is part of the NSA selector, a eurorack module that listens to raw ethernet.
# 
# sabotageakt lets you play images, videos, or any files on raw ethernet, using a MIDI keyboard.
# 
# this is a console MIDI client for the NSA selector, it downloads media files from a
# web server, preferably plaintext over http without encryption or compression.
#
# the mapping of MIDI notes to files is done in a JSON file, which is loaded at startup.
# the JSON file format is interoperable with Nick Starke's https://github.com/nstarke/nsa-midi
# so you may use his tools to download media and generate the mapping files.
#

import mido
import argparse
import sys
import json
import os
import subprocess

def list_ports(ports):
    print("Available MIDI input ports:")
    for idx, port in enumerate(ports):
        print(f"  [{idx}] {port}")

def load_mapping(mapping_file):
    """Load MIDI note to URL mapping from JSON file."""
    try:
        with open(mapping_file, 'r') as f:
            mapping = json.load(f)
        return mapping
    except FileNotFoundError:
        print(f"Error: Mapping file '{mapping_file}' not found.")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in mapping file '{mapping_file}': {e}")
        sys.exit(1)

def get_url_for_note(note, mapping):
    """Get URL for a MIDI note from the mapping."""
    if len(mapping) > 0:
        index = note % len(mapping)
        return mapping[index]
    return None

def get_media_file(url, monophonic=False):
    """Fork a wget process to download the media file, output to /dev/null."""
    print(f"fetching {url}")
    try:
        if monophonic:
            # Kill all existing wget processes and wait for them to finish
            try:
                subprocess.run(['killall', 'wget'], check=False)
            except FileNotFoundError:
                # killall not found, try pkill
                try:
                    subprocess.run(['pkill', 'wget'], check=False)
                except FileNotFoundError:
                    print("Warning: Neither killall nor pkill found, cannot kill existing wget processes")
        
        # Fork wget process with output to /dev/null (fire and forget)
        subprocess.Popen([
            'wget', 
            '-q',  # quiet mode
            '-O', '/dev/null',  # output to /dev/null
            url
        ])
    except FileNotFoundError:
        print("Error: wget not found. Please install wget.")
    except Exception as e:
        print(f"Error launching wget: {e}")

def main():
    parser = argparse.ArgumentParser(description="MIDI note to URL mapper for downloading media files via the NSA selector")
    parser.add_argument('-p', '--port', type=int, help="Port number to open")
    parser.add_argument('-m', '--mapping', default='default.json', 
                        help="MIDI note to URL JSON mapping file (default: default.json)")
    parser.add_argument('-1', '--monophonic', action='store_true',
                        help="monophonic mode: just one download at a time (WARNING: will kill all existing wget processes on this system!)")
    args = parser.parse_args()

    mapping = load_mapping(args.mapping)
    print(f"Loaded mapping from '{args.mapping}'")

    ports = mido.get_input_names()
    if not ports:
        print("No MIDI input ports found.")
        sys.exit(1)

    if args.port is None:
        list_ports(ports)
        try:
            idx = int(input(f"Select MIDI port [0-{len(ports)-1}]: "))
        except (ValueError, KeyboardInterrupt):
            print("\nAborted.")
            sys.exit(1)
    else:
        idx = args.port

    if idx < 0 or idx >= len(ports):
        print(f"Invalid port index: {idx}")
        sys.exit(1)

    port_name = ports[idx]
    print(f"Opening MIDI input port: {port_name}")
    with mido.open_input(port_name) as inport:
        print("Listening for MIDI notes. Press Ctrl+C to exit.")
        try:
            for msg in inport:
                if msg.type == 'note_on' and msg.velocity > 0:
                    url = get_url_for_note(msg.note, mapping)
                    if url:
                        get_media_file(url, args.monophonic)
                    else:
                        print(f"  -> No mapping found for note {msg.note}")
        except KeyboardInterrupt:
            print("\nExiting...")

if __name__ == "__main__":
    main()