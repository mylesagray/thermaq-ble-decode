import asyncio
import platform
import struct
import math

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
UNKNOWN_UUID = "45544942-4c55-4554-4845-524db87ad705"
CHANNEL_1_CONFIG_UUID = "45544942-4C55-4554-4845-524DB87AD707"
CHANNEL_2_CONFIG_UUID = "45544942-4c55-4554-4845-524db87ad708"
DEVICE_CONFIG_UUID = "45544942-4c55-4554-4845-524db87ad709"
TRIM_UUID = "45544942-4c55-4554-4845-524db87ad70a"


async def main(address):
    """
    Decodes a ThermaQ client's BLE API into human readable format
    """
    async with BleakClient(address) as client:
        print("\nDecoded Info:\n")

        # Standard Config Data
        manufacturer_name = await client.read_gatt_char(MANUFACTURER_NAME_UUID)
        print(f"Manufacturer Name: {''.join(map(chr, manufacturer_name))}")

        firmware_revision = await client.read_gatt_char(FIRMWARE_REV_UUID)
        print(f"Firmware Revision: {''.join(map(chr, firmware_revision))}")

        hardware_revision = await client.read_gatt_char(HARDWARE_REV_UUID)
        print(f"Hardware Revision: {''.join(map(chr, hardware_revision))}")

        software_revision = await client.read_gatt_char(SOFTWARE_REV_UUID)
        print(f"Software Revision: {''.join(map(chr, software_revision))}")

        # Battery level - notifiable
        battery_level = await client.read_gatt_char(BATTERY_LEVEL_UUID)
        print(f"Battery Level (notifiable): {format(int(battery_level[0]))}%")

        model_number = await client.read_gatt_char(MODEL_NBR_UUID)
        print(f"Model Number: {''.join(map(chr, model_number))}")

        serial_number = await client.read_gatt_char(SERIAL_NUMBER_UUID)
        print(f"Serial Number: {''.join(map(chr, serial_number))}")

        # Channel name and alarm configuration
        print("\nCustom Characteristics:\n")
        probe_1_data = await client.read_gatt_char(CHANNEL_1_CONFIG_UUID)
        probe_1_name_data = probe_1_data[8:20]
        probe_1_name = probe_1_name_data.decode()
        probe_1_alarm_low_data = round(
            struct.unpack('<f', probe_1_data[4:8])[0], 2)
        probe_1_alarm_high_data = round(
            struct.unpack('<f', probe_1_data[0:4])[0], 2)
        if not math.isnan(probe_1_alarm_low_data):
            probe_1_alarm_low = probe_1_alarm_low_data
        else:
            probe_1_alarm_low = 'Diabled'

        if not math.isnan(probe_1_alarm_high_data):
            probe_1_alarm_high = probe_1_alarm_high_data
        else:
            probe_1_alarm_high = 'Diabled'

        print(f"Channel 1 Config Bytes: {probe_1_data.hex(' ')}")
        print(f"Channel 1 Name: {probe_1_name}")
        print(
            f"Channel 1 Alarm Low: {probe_1_alarm_low}")
        print(
            f"Channel 1 Alarm High: {probe_1_alarm_high}")

        probe_2_data = await client.read_gatt_char(CHANNEL_2_CONFIG_UUID)
        probe_2_name_data = probe_2_data[8:20]
        probe_2_name = probe_2_name_data.decode()
        probe_2_alarm_low_data = round(
            struct.unpack('<f', probe_2_data[4:8])[0], 2)
        probe_2_alarm_high_data = round(
            struct.unpack('<f', probe_2_data[0:4])[0], 2)
        if not math.isnan(probe_2_alarm_low_data):
            probe_2_alarm_low = probe_2_alarm_low_data
        else:
            probe_2_alarm_low = 'Diabled'

        if not math.isnan(probe_2_alarm_high_data):
            probe_2_alarm_high = probe_2_alarm_high_data
        else:
            probe_2_alarm_high = 'Diabled'
        print(f"Channel 2 Config Bytes: {probe_2_data.hex(' ')}")
        print(f"Channel 2 Name: {probe_2_name}")
        print(
            f"Channel 2 Alarm Low: {probe_2_alarm_low}")
        print(
            f"Channel 2 Alarm High: {probe_2_alarm_high}")

        # Device Config Characteristic
        device_config = await client.read_gatt_char(DEVICE_CONFIG_UUID)
        print(f"\nDevice Config Bytes: {device_config.hex(' ')}")
        temp_unit = device_config[0]
        measurement_interval = device_config[1]
        unknown_byte_1 = device_config[2]
        auto_power_off = device_config[3]
        unknown_byte_2 = device_config[4]
        channel_2_enable = bool(device_config[5])
        unknown_byte_3 = device_config[6]

        if temp_unit == 0:
            print("Temp unit: °C")
        elif temp_unit == 1:
            print("Temp unit: °F")
        else:
            print("Temp unit: Unknown data")

        print(f"Measurement Interval: {measurement_interval}s")

        print(f"Unknown byte: {unknown_byte_1}")

        if auto_power_off == 0:
            print("Auto Power Off: False")
        else:
            print(
                f"Auto Power Off: {auto_power_off}mins ({auto_power_off/60}h)")

        print(f"Unknown byte: {unknown_byte_2}")

        print(f"Channel 2 Enabled: {channel_2_enable}")

        print(f"Unknown byte: {unknown_byte_3}")

        # Channel 1 temp reading - notifiable
        channel_1 = await client.read_gatt_char(CHANNEL_1_DATA_UUID)
        print(f"\nChannel 1 Data Bytes: {channel_1.hex(' ')}")
        channel_1_temp_float = struct.unpack('<f', channel_1)
        channel_1_temp = round(channel_1_temp_float[0], 2)
        if math.isnan(channel_1_temp):
            print("Channel 1 Temp (notifiable): No Probe")
        else:
            print(f"Channel 1 Temp (notifiable): {channel_1_temp}")

        # Channel 2 temp reading - notifiable
        channel_2 = await client.read_gatt_char(CHANNEL_2_DATA_UUID)
        print(f"\nChannel 2 Data Bytes: {channel_2.hex(' ')}")
        channel_2_temp_float = struct.unpack('<f', channel_2)
        channel_2_temp = round(channel_2_temp_float[0], 2)
        if not channel_2_enable:
            print("Channel 2 Temp (notifiable): Disabled")
        elif math.isnan(channel_2_temp):
            print("Channel 2 Temp (notifiable): No Probe")
        else:
            print(f"Channel 2 Temp (notifiable): {channel_2_temp}")

        # Channel temperature trim config
        trim_data = await client.read_gatt_char(TRIM_UUID)
        print(f"\nTrim Raw Bytes: {trim_data.hex(' ')}")

        trim_channel_1_temp_data = struct.unpack('<f', trim_data[:4])
        trim_channel_1 = round(trim_channel_1_temp_data[0], 2)
        unknown_channel_1 = trim_data[4:7]
        print(f"Channel 1 Trim: {trim_channel_1}")
        print(f"Channel 1 Unknown: {unknown_channel_1}")

        trim_channel_2_temp_data = struct.unpack('<f', trim_data[7:11])
        trim_channel_2 = round(trim_channel_2_temp_data[0], 2)
        unknown_channel_2 = trim_data[11:]
        print(f"Channel 2 Trim: {trim_channel_2}")
        print(f"Channel 2 Unknown: {unknown_channel_2}")

        # Unknown service - notifiable
        unknown = await client.read_gatt_char(UNKNOWN_UUID)
        print(f"\nUnknown Service Bytes (notifiable): {unknown.hex(' ')}")


async def scan_ble_devices():
    """
    Scans all BLE devices and returns their addresses as seen by OS
    """
    devices = await BleakScanner.discover()
    for d in devices:
        print(d)


async def dump_services(address):
    """
    Dumps all BLE GATT Services, Characteristics and associated Descriptors
    for a given BLE address
    """
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
