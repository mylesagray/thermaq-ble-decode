"""
Module to decode BLE commands from ETI Ltd Bluetooth Low Energy Thermometers
"""
import asyncio
import platform
import struct
import math
import logging

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
COMMANDS_NOTIFICATIONS_UUID = "45544942-4c55-4554-4845-524db87ad705"
CHANNEL_1_CONFIG_UUID = "45544942-4C55-4554-4845-524DB87AD707"
CHANNEL_2_CONFIG_UUID = "45544942-4c55-4554-4845-524db87ad708"
DEVICE_CONFIG_UUID = "45544942-4c55-4554-4845-524db87ad709"
TRIM_UUID = "45544942-4c55-4554-4845-524db87ad70a"


def getProbeType(probe_index, probe_data):
    # Data for probe type is packed into the last byte of the
    # Device Config packet - the first 4 bits are the first channel
    # the second four bits are the second channel, if we want to access
    # the data for the second channel, we bitshift 4 spaces to the left
    # An example byte for probe data is 17 - or 0001 0001 in binary
    # which when bitshifted, gives us the probe type for each channel
    if probe_index == 1:
        probe_data >>= 4
    # To get the probe type, they are indexed as:
    # 0: Pluggable K Type Thermocouple
    # 1: Fixed K Type Thermocouple
    # Anything else: Unknown
    #
    # We bitwise AND the data to filter for only the sensor index we are interested in
    # In this case, 15 int == 0000 1111 in binary - bitwise ANDing this against our value
    # selects only the four least significant bits of data, which we then use the integer
    # representation of to select our probe type
    probe_type = probe_data & 15
    if probe_type != 1:
        if probe_type != 2:
            return "Unknown"
        return "Fixed K Type"
    return "Pluggable K Type"


def getNotificationType(notification_data):
    match notification_data:
        case 0:
            return "NONE"
        case 1:
            return "BUTTON PRESSED"
        case 2:
            return "SHUTDOWN"
        case 3:
            return "INVALID SETTING"
        case 4:
            return "INVALID COMMAND"
        case 5:
            return "COMMUNICATION_ERROR"
        case 6:
            return "UNKNOWN NOTIFICATION"
        case 7:
            return "CHECKPOINT"
        case 8:
            return "REQUEST REFRESH"
        case _:
            return "UNKNOWN NOTIFICATION"


def getCommandType(command_data):
    if command_data == 0:
        return [16, "Measure"]
    elif command_data == 1:
        return [32, "Identify"]
    elif command_data == 2:
        return [48, "Set Defaults"]
    elif command_data != 3:
        return [0, "None"]
    else:
        return [64, "Factory Reset"]


def decodeTemp(temp):
    return round(struct.unpack('<f', temp)[0], 2)


async def writeData(client, uuid, data):
    await client.write_gatt_char(uuid, data)
    await client.read_gatt_char(uuid)


async def notification_handler(characteristic, data):
    print(f"{characteristic.description}: {data}")


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

        # Device Config Characteristic
        device_config = await client.read_gatt_char(DEVICE_CONFIG_UUID)
        print(f"\nDevice Config Bytes: {device_config.hex(' ')}")
        temp_unit = device_config[0]
        measurement_interval = device_config[1]
        # Either this or the other unknown byte are Emissivity
        unknown_byte_1 = device_config[2]
        auto_power_off = device_config[3]
        unknown_byte_2 = device_config[4]
        channel_2_enable = bool(device_config[5])
        probe_type = device_config[6]

        temp_unit_symbol = ""
        if temp_unit == 0:
            temp_unit_symbol = "°C"
            print(f"Temp unit: {temp_unit_symbol}")
        elif temp_unit == 1:
            temp_unit_symbol = "°F"
            print(f"Temp unit: {temp_unit_symbol}")
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

        print(f"Channel 1 Probe Type: {getProbeType(0, probe_type)}")
        if channel_2_enable:
            print(f"Channel 2 Probe Type: {getProbeType(1, probe_type)}")

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
            f"Channel 1 Alarm Low: {probe_1_alarm_low}{temp_unit_symbol}")
        print(
            f"Channel 1 Alarm High: {probe_1_alarm_high}{temp_unit_symbol}")

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
            f"Channel 2 Alarm Low: {probe_2_alarm_low}{temp_unit_symbol}")
        print(
            f"Channel 2 Alarm High: {probe_2_alarm_high}{temp_unit_symbol}")

        # Channel 1 temp reading - notifiable
        channel_1 = await client.read_gatt_char(CHANNEL_1_DATA_UUID)
        print(f"\nChannel 1 Data Bytes: {channel_1.hex(' ')}")
        channel_1_temp_float = struct.unpack('<f', channel_1)
        channel_1_temp = round(channel_1_temp_float[0], 2)
        if math.isnan(channel_1_temp):
            print("Channel 1 Temp (notifiable): No Probe")
        else:
            print(
                f"Channel 1 Temp (notifiable): {channel_1_temp}{temp_unit_symbol}")

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
            print(
                f"Channel 2 Temp (notifiable): {channel_2_temp}{temp_unit_symbol}")

        # Channel temperature trim config
        trim_data = await client.read_gatt_char(TRIM_UUID)
        print(f"\nTrim Raw Bytes: {trim_data.hex(' ')}")

        trim_channel_1_temp_data = struct.unpack('<f', trim_data[:4])
        trim_channel_1 = round(trim_channel_1_temp_data[0], 2)
        trim_channel_1_date_set = f"{trim_data[4]}/{trim_data[5]}/{trim_data[6]}"
        print(f"Channel 1 Trim: {trim_channel_1}{temp_unit_symbol}")
        print(f"Channel 1 Trim Date Set: {trim_channel_1_date_set}")

        trim_channel_2_temp_data = struct.unpack('<f', trim_data[7:11])
        trim_channel_2 = round(trim_channel_2_temp_data[0], 2)
        trim_channel_2_date_set = f"{trim_data[11]}/{trim_data[12]}/{trim_data[13]}"
        print(f"Channel 2 Trim: {trim_channel_2}{temp_unit_symbol}")
        print(f"Channel 2 Trim Date Set: {trim_channel_2_date_set}")

        # Commands and Notifications Service - notifiable
        commands_notifications_data = await client.read_gatt_char(COMMANDS_NOTIFICATIONS_UUID)
        print("\nCommands and Notifications Bytes (notifiable): "
              f"{commands_notifications_data.hex(' ')}")
        command_data = struct.unpack(
            '1B', commands_notifications_data[0:1])[0]
        notification_data = struct.unpack(
            '1B', commands_notifications_data[1:2])[0]
        print(f"Command: {getCommandType(command_data)[1]}")
        print(
            f"Notification: {getNotificationType(notification_data)}")

        # await client.start_notify(CHANNEL_1_DATA_UUID, notification_handler)
        # await client.start_notify(CHANNEL_2_DATA_UUID, notification_handler)
        # await client.start_notify(BATTERY_LEVEL_UUID, notification_handler)
        # await asyncio.sleep(5)
        # await client.stop_notify(CHANNEL_1_DATA_UUID)
        # await client.stop_notify(CHANNEL_2_DATA_UUID)
        # await client.stop_notify(BATTERY_LEVEL_UUID)

        # Identify command
        # write_data = bytearray(
        #     b'\x20\x00')
        # await writeData(client, COMMANDS_NOTIFICATIONS_UUID, write_data)


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
