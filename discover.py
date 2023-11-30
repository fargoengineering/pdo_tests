# import asyncio
# from bleak import BleakScanner

# slots = {}

# async def discover():
#     for d in await BleakScanner.discover():
#         if d.name is not None and "SLOT" in d.name:
#             split_and_append(str(d), slots)
#             print(f"found {d}")

# def split_and_append(input_string, existing_dict):
#     parts = input_string.split(":")
#     mac_address = ":".join(parts[:-1])  # Join all parts except the last one with ":"
#     slot_name = parts[-1].strip()  # Get the last part and remove leading/trailing spaces
#     existing_dict[mac_address] = slot_name

# asyncio.run(discover())

import asyncio
from bleak import BleakScanner


async def run():
    for device in await BleakScanner.discover():
        print(f'{device.name} - {device.address}')

if __name__ == '__main__':
    try:
        asyncio.run(run())
    except KeyboardInterrupt:
        pass
