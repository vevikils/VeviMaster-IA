import re

output = """
[Parsed_ebur128_0 @ 0x56179bb9d680] Summary:

  Integrated loudness:
    I:          -9.7 LUFS
    Threshold: -20.0 LUFS

  Loudness range:
    LRA:         4.4 LU
    Threshold: -30.0 LUFS
    LRA low:   -13.0 LUFS
    LRA high:   -8.5 LUFS

  True peak:
    Peak:        1.0 dBFS
"""

lufs_match = re.search(r'I:\s+([-\d\.]+)\s+LUFS', output)
if lufs_match:
    print(f"MATCH FOUND: {lufs_match.group(1)}")
else:
    print("NO MATCH")
