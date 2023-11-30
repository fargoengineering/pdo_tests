import struct

pack_format = '>BlB'
slot_all_pdo = [5, 1, 3]
packed_output = struct.pack(pack_format, *slot_all_pdo)

unpacked_output = struct.unpack(pack_format,packed_output)

print(repr(packed_output))
