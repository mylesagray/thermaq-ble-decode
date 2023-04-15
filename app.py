import asyncio
import platform

from bleak import BleakClient, BleakScanner
from bleak.uuids import uuid16_dict

ADDRESS = (
    "68:27:19:04:d0:54"
    if platform.system() != "Darwin"
    else "eda72dde-bcd3-be23-d129-03430fa7ba70"
)

uuid16_dict = {v: k for k, v in uuid16_dict.items()}

# BTLE UUIDs and services for ThermaQ Blue
#
# Check readme for protocol dump
#
# Standard Services
#
SERIAL_NUMBER_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Serial Number String")
)

HARDWARE_REV_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Hardware Revision String")
)

FIRMWARE_REV_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Firmware Revision String")
)

SOFTWARE_REV_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Software Revision String")
)

MANUFACTURER_NAME_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Manufacturer Name String")
)

MODEL_NBR_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Model Number String")
)

BATTERY_LEVEL_UUID = "0000{0:x}-0000-1000-8000-00805f9b34fb".format(
    uuid16_dict.get("Battery Level")
)

#
# Custom Services
#
CHANNEL_1_DATA_UUID = "45544942-4c55-4554-4845-524db87ad701"
CHANNEL_2_DATA_UUID = "45544942-4c55-4554-4845-524db87ad703"
UNKNOWN_2_UUID = "45544942-4c55-4554-4845-524db87ad705"
CHANNEL_1_CONFIG_UUID = "45544942-4C55-4554-4845-524DB87AD707"
CHANNEL_2_CONFIG_UUID = "45544942-4c55-4554-4845-524db87ad708"
DEVICE_CONFIG_UUID = "45544942-4c55-4554-4845-524db87ad709"
UNKNOWN_UUID = "45544942-4c55-4554-4845-524db87ad70a"


async def main(address):
    async with BleakClient(address) as client:
        print("\nDecoded Info:\n")
        manufacturer_name = await client.read_gatt_char(MANUFACTURER_NAME_UUID)
        print("Manufacturer Name: {0}".format(
            "".join(map(chr, manufacturer_name))))

        firmware_revision = await client.read_gatt_char(FIRMWARE_REV_UUID)
        print("Firmware Revision: {0}".format(
            "".join(map(chr, firmware_revision))))

        hardware_revision = await client.read_gatt_char(HARDWARE_REV_UUID)
        print("Hardware Revision: {0}".format(
            "".join(map(chr, hardware_revision))))

        software_revision = await client.read_gatt_char(SOFTWARE_REV_UUID)
        print("Software Revision: {0}".format(
            "".join(map(chr, software_revision))))

        battery_level = await client.read_gatt_char(BATTERY_LEVEL_UUID)
        print("Battery Level: {0}%".format(int(battery_level[0])))

        model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        print("Model Number: {0}".format("".join(map(chr, model_number))))

        serial_number = await client.read_gatt_char(SERIAL_NUMBER_UUID)
        print("Serial Number: {0}".format("".join(map(chr, serial_number))))

        print("\nCustom Characteristics:\n")
        probe_1_name = await client.read_gatt_char(CHANNEL_1_CONFIG_UUID)
        print(f"Channel 1 Config Bytes: {probe_1_name.hex(' ')}")
        print(f"Channel 1 Name: {probe_1_name[8:20]}")
        print(f"Channel 1 Alarm Low: {probe_1_name[4:7].hex()}")
        print(f"Channel 1 Alarm High: {probe_1_name[0:3].hex()}")

        probe_2_name = await client.read_gatt_char(CHANNEL_2_CONFIG_UUID)
        print(f"Channel 2 Config Bytes: {probe_2_name.hex(' ')}")
        print(f"Channel 2 Name: {probe_2_name[8:20]}")
        print(f"Channel 2 Alarm Low: {probe_2_name[4:7].hex()}")
        print(f"Channel 2 Alarm High: {probe_2_name[0:3].hex()}")

        device_config = await client.read_gatt_char(DEVICE_CONFIG_UUID)
        print(f"\nDevice Config: {device_config.hex(' ')}")
        temp_unit = device_config[0]
        measurement_interval = device_config[1]
        auto_power_off = device_config[3]
        channel_2_enable = bool(device_config[5])
        if temp_unit == 0:
            print("Temp unit: °C")
        else:
            print("Temp unit: °F")

        print(f"Measurement Interval: {measurement_interval}s")

        if auto_power_off == 0:
            print("Auto Power Off: False")
        else:
            print(
                f"Auto Power Off: {auto_power_off}mins ({auto_power_off/60}h)")

        print(f"Channel 2 Enabled: {channel_2_enable}")

        channel_1 = await client.read_gatt_char(CHANNEL_1_DATA_UUID)
        print(f"\nChannel 1 Data Bytes: {channel_1.hex(' ')}")
        channel_1_temp_float = int(channel_1.hex(), 16)
        print(f"Channel 1 Temp Int16: {channel_1_temp_float}")
        channel_1_temp = channel_1_temp_float / 32
        if channel_1_temp_float == 4294967295:
            print("Channel 1 Temp: Error")
        else:
            print(f"Channel 1 Temp: {channel_1_temp}")

        channel_2 = await client.read_gatt_char(CHANNEL_2_DATA_UUID)
        print(f"\nChannel 2 Data Bytes: {channel_2.hex(' ')}")
        channel_2_temp_float = int(channel_2.hex(), 16)
        print(f"Channel 2 Temp Int16: {channel_2_temp_float}")
        channel_2_temp = channel_2_temp_float / 32
        if not channel_2_enable:
            print("Channel 2 Temp: Disabled")
        elif channel_2_temp_float == 4294967295:
            print("Channel 2 Temp: Error")
        else:
            print(f"Channel 2 Temp: {channel_2_temp}")

        unknown_char = await client.read_gatt_char(UNKNOWN_UUID)
        print(f"\nUnknown Raw Bytes: {unknown_char.hex(' ')}")

        unknown_2_char = await client.read_gatt_char(UNKNOWN_2_UUID)
        print(f"\nUnknown Raw Bytes: {unknown_2_char.hex(' ')}")


async def scan_ble_devices():
    devices = await BleakScanner.discover()
    for d in devices:
        print(d)


async def dump_services(address):
    async with BleakClient(address) as client:
        print(f"Device Connected: {client.is_connected}")
        services = client.services.services

        for service in services:
            service_info = client.services.get_service(service)
            print(f"\nService: {service_info}")
            print(f"Service Obj: {service_info.obj}")

            characteristics = service_info.characteristics
            for characteristic in characteristics:
                characteristic_value = await client.read_gatt_char(
                    characteristic.uuid)
                print(f"\n-> Characteristic: {characteristic}")
                print(
                    f"-> Characteristic Properties: {characteristic.properties}")
                print(
                    f"-> Characteristic Obj: {characteristic.obj}")
                print(
                    f"-> Characteristic Value: {characteristic_value}")
                descriptors = characteristic.descriptors
                for descriptor in descriptors:
                    descriptor_value = await client.read_gatt_descriptor(descriptor.handle)
                    print(f"\n--> Descriptor: {str(descriptor)}")
                    print(f"--> Descriptor Obj: {descriptor.obj}")
                    print(f"--> Descriptor Value: {descriptor_value}")

asyncio.run(main(ADDRESS))
