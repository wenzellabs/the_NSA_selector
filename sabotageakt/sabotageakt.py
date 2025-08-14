#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# sabotageakt.py
# This script is part of the SabotageAkt project.
# It is designed to handle sabotage activities in a controlled environment.

# atleast what Copilot thinks it is.
# it's part of the NSA selector, a eurorack module that listens to raw ethernet.

import mido
import argparse
import sys

def list_ports(ports):
    print("Available MIDI input ports:")
    for idx, port in enumerate(ports):
        print(f"  [{idx}] {port}")

def main():
    parser = argparse.ArgumentParser(description="MIDI note printer")
    parser.add_argument('-p', '--port', type=int, help="Port number to open")
    args = parser.parse_args()

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
                if msg.type in ('note_on', 'note_off'):
                    print(msg)
        except KeyboardInterrupt:
            print("\nExiting...")

if __name__ == "__main__":
    main()