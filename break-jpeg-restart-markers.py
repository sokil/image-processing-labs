#!/usr/bin/env python3
import sys
import shutil

# JPEG markers (known ones for clarity)
MARKERS = {
    0xD8: "SOI (Start of Image)",
    0xD9: "EOI (End of Image)",
    0xC0: "SOF0 (Baseline DCT)",
    0xC2: "SOF2 (Progressive DCT)",
    0xC4: "DHT (Define Huffman Table)",
    0xDB: "DQT (Define Quantization Table)",
    0xDA: "SOS (Start of Scan)",
    0xDD: "DRI (Define Restart Interval)",
    0xE0: "APP0 (JFIF)",
    0xE1: "APP1 (EXIF)",
    0xE2: "APP2",
    0xFE: "COM (Comment)",
    0xD0: "RST0",
    0xD1: "RST1",
    0xD2: "RST2",
    0xD3: "RST3",
    0xD4: "RST4",
    0xD5: "RST5",
    0xD6: "RST6",
    0xD7: "RST7",
}

def read_marker(f):
    # Skip non-FF bytes (padding or entropy data)
    b = f.read(1)
    while b and b != b'\xFF':
        b = f.read(1)
    if not b:
        return None

    # Read next non-FF byte (marker code)
    while True:
        c = f.read(1)
        if not c:
            return None
        if c != b'\xFF':
            break

    return c[0]


def dump_jpeg(filename):

    end_of_scans_pos = None
    restart_segments = []

    with open(filename, "rb") as f:
        pos = 0
        data = f.read()
        f.seek(0)

        print(f"--- JPEG structure of '{filename}' ---")
        while True:
            marker = read_marker(f)
            if marker is None:
                break

            offset = f.tell() - 2
            name = MARKERS.get(marker, f"Unknown (FF{marker:02X})")

            if marker == 0xD9:
                end_of_scans_pos = f.tell() - 3
                continue

            # SOI/EOI/RST markers have no length
            if marker in range(0xD0, 0xD8) or marker in (0xD8, 0xD9):
                print(f"{offset:08X}: FF {marker:02X}  -> {name}")
                continue

            # Read 2-byte segment length
            length_bytes = f.read(2)
            if len(length_bytes) < 2:
                break

            length = (length_bytes[0] << 8) + length_bytes[1]

            # Print marker info
            print(f"{offset:08X}: FF {marker:02X}  -> {name}, length={length}")

            # For Start of Scan, entropy data follows until next 0xFF marker
            if marker == 0xDA:
                start_scan = f.tell()
                last_rst_offset = start_scan
                while True:
                    b = f.read(1)
                    if not b:
                        break
                    if b == b'\xFF':
                        nxt = f.read(1)
                        if not nxt:
                            break
                        if nxt[0] == 0x00:
                            # literal 0xFF byte inside data
                            continue
                        elif 0xD0 <= nxt[0] <= 0xD7:
                            # restart marker
                            restart_segments.append(f.tell())
                            continue
                        else:
                            # next marker, scan ends
                            f.seek(-2, 1)  # rewind to let main loop read it
                            break
                end_scan = f.tell()
                total_entropy_length = end_scan - start_scan
                print(f"    Total entropy-coded segment: {total_entropy_length} bytes")
            else:
                # Skip rest of block
                f.seek(length - 2, 1)

        print("--- End of file ---")

    shutil.copy(filename, 'patched_' + filename)
    with open('patched_' + filename, "r+b") as w:
        for i, pos in enumerate(restart_segments):
            if i%3 == 0:
                continue

            w.seek(pos + 20, 0)

            if i == len(restart_segments) - 1:
                length = end_of_scans_pos - pos
            else:
                length = restart_segments[i+1] - pos

            print ("Replace %s bytes from %x" % (length, pos))
            w.write(b'\xaa' * 20)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: jpeg_dump.py <file.jpg>")
        sys.exit(1)

    dump_jpeg(sys.argv[1])
