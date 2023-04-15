# ThermaQ Blue BLE Protocol Decoding

## Data dump

### Device Info Service

```ini
Service: 0000180a-0000-1000-8000-00805f9b34fb (Handle: 12): Device Information
Service Obj: <CBService: 0x7fb6ae740de0, isPrimary = YES, UUID = Device Information>

-> Characteristic: 00002a25-0000-1000-8000-00805f9b34fb (Handle: 13): Serial Number String
-> Characteristic Properties: ['read']
-> Characteristic Obj: <CBCharacteristic: 0x7fb6ae04d9c0, UUID = Serial Number String, properties = 0x2, value = {length = 8, bytes = 0x3233313436353538}, notifying = NO>
-> Characteristic Value: bytearray(b'23146558')

-> Characteristic: 00002a27-0000-1000-8000-00805f9b34fb (Handle: 15): Hardware Revision String
-> Characteristic Properties: ['read']
-> Characteristic Obj: <CBCharacteristic: 0x7fb6ae086a30, UUID = Hardware Revision String, properties = 0x2, value = {length = 3, bytes = 0x312e30}, notifying = NO>
-> Characteristic Value: bytearray(b'1.0')

-> Characteristic: 00002a26-0000-1000-8000-00805f9b34fb (Handle: 17): Firmware Revision String
-> Characteristic Properties: ['read']
-> Characteristic Obj: <CBCharacteristic: 0x7fb6ae064720, UUID = Firmware Revision String, properties = 0x2, value = {length = 4, bytes = 0x312e3035}, notifying = NO>
-> Characteristic Value: bytearray(b'1.05')

-> Characteristic: 00002a28-0000-1000-8000-00805f9b34fb (Handle: 19): Software Revision String
-> Characteristic Properties: ['read']
-> Characteristic Obj: <CBCharacteristic: 0x7fb6ae08f0d0, UUID = Software Revision String, properties = 0x2, value = {length = 7, bytes = 0x312e3333424543}, notifying = NO>
-> Characteristic Value: bytearray(b'1.33BEC')

-> Characteristic: 00002a29-0000-1000-8000-00805f9b34fb (Handle: 21): Manufacturer Name String
-> Characteristic Properties: ['read']
-> Characteristic Obj: <CBCharacteristic: 0x7fb6ae064780, UUID = Manufacturer Name String, properties = 0x2, value = {length = 7, bytes = 0x455449204c7464}, notifying = NO>
-> Characteristic Value: bytearray(b'ETI Ltd')

-> Characteristic: 00002a24-0000-1000-8000-00805f9b34fb (Handle: 23): Model Number String
-> Characteristic Properties: ['read']
-> Characteristic Obj: <CBCharacteristic: 0x7fb6ae086a90, UUID = Model Number String, properties = 0x2, value = {length = 7, bytes = 0x3239322d393231}, notifying = NO>
-> Characteristic Value: bytearray(b'292-921')
```

### Custom Service

Temperature in C, Single Channel called "Rocket Group" enabled:

```ini
Service: 45544942-4c55-4554-4845-524db87ad700 (Handle: 25): Unknown
Service Obj: <CBService: 0x7fb6ae7e17e0, isPrimary = YES, UUID = 45544942-4C55-4554-4845-524DB87AD700>

-> Characteristic: 45544942-4c55-4554-4845-524db87ad701 (Handle: 26): Unknown
-> Characteristic Properties: ['read', 'notify']
-> Characteristic Obj: <CBCharacteristic: 0x7fb6ae50b710, UUID = 45544942-4C55-4554-4845-524DB87AD701, properties = 0x12, value = {length = 4, bytes = 0xd7b7ac41}, notifying = NO>
-> Characteristic Value: bytearray(b'\xd7\xb7\xacA')

--> Descriptor: 00002902-0000-1000-8000-00805f9b34fb (Handle: 28): Client Characteristic Configuration
--> Descriptor Obj: <CBDescriptor: 0x7fb6ae7e77d0, UUID = Client Characteristic Configuration, value = (null)>

-> Characteristic: 45544942-4c55-4554-4845-524db87ad705 (Handle: 29): Unknown
-> Characteristic Properties: ['read', 'write-without-response', 'notify']
-> Characteristic Obj: <CBCharacteristic: 0x7fb6ae50a280, UUID = 45544942-4C55-4554-4845-524DB87AD705, properties = 0x16, value = {length = 2, bytes = 0x0000}, notifying = NO>
-> Characteristic Value: bytearray(b'\x00\x00')

--> Descriptor: 00002902-0000-1000-8000-00805f9b34fb (Handle: 31): Client Characteristic Configuration
--> Descriptor Obj: <CBDescriptor: 0x7fb6ad72a770, UUID = Client Characteristic Configuration, value = (null)>

-> Characteristic: 45544942-4c55-4554-4845-524db87ad707 (Handle: 32): Unknown
-> Characteristic Properties: ['read', 'write-without-response']
-> Characteristic Obj: <CBCharacteristic: 0x7fb6ae510600, UUID = 45544942-4C55-4554-4845-524DB87AD707, properties = 0x6, value = {length = 20, bytes = 0xffffffffffffffff526f636b65742047726f7570}, notifying = NO>
-> Characteristic Value: bytearray(b'\xff\xff\xff\xff\xff\xff\xff\xffRocket Group')

-> Characteristic: 45544942-4c55-4554-4845-524db87ad709 (Handle: 34): Unknown
-> Characteristic Properties: ['read', 'write-without-response']
-> Characteristic Obj: <CBCharacteristic: 0x7fb6ae506ec0, UUID = 45544942-4C55-4554-4845-524DB87AD709, properties = 0x6, value = {length = 7, bytes = 0x00010000000011}, notifying = NO>
-> Characteristic Value: bytearray(b'\x00\x01\x00\x00\x00\x00\x11')

-> Characteristic: 45544942-4c55-4554-4845-524db87ad70a (Handle: 36): Unknown
-> Characteristic Properties: ['read', 'write-without-response']
-> Characteristic Obj: <CBCharacteristic: 0x7fb6ae506f20, UUID = 45544942-4C55-4554-4845-524DB87AD70A, properties = 0x6, value = {length = 14, bytes = 0x0000000000000000000000000000}, notifying = NO>
-> Characteristic Value: bytearray(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

-> Characteristic: 45544942-4c55-4554-4845-524db87ad703 (Handle: 38): Unknown
-> Characteristic Properties: ['read', 'notify']
-> Characteristic Obj: <CBCharacteristic: 0x7fb6ae50a940, UUID = 45544942-4C55-4554-4845-524DB87AD703, properties = 0x12, value = {length = 0, bytes = 0x}, notifying = NO>
-> Characteristic Value: bytearray(b'')

--> Descriptor: 00002902-0000-1000-8000-00805f9b34fb (Handle: 40): Client Characteristic Configuration
--> Descriptor Obj: <CBDescriptor: 0x7fb6ae788df0, UUID = Client Characteristic Configuration, value = (null)>

-> Characteristic: 45544942-4c55-4554-4845-524db87ad708 (Handle: 41): Unknown
-> Characteristic Properties: ['read', 'write-without-response']
-> Characteristic Obj: <CBCharacteristic: 0x7fb6ae50a9a0, UUID = 45544942-4C55-4554-4845-524DB87AD708, properties = 0x6, value = {length = 20, bytes = 0xffffffffffffffff000000000000000000000000}, notifying = NO>
-> Characteristic Value: bytearray(b'\xff\xff\xff\xff\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
```

### Battery Service

```ini
Service: 0000180f-0000-1000-8000-00805f9b34fb (Handle: 43): Battery Service
Service Obj: <CBService: 0x7fb6ae738720, isPrimary = YES, UUID = Battery>

-> Characteristic: 00002a19-0000-1000-8000-00805f9b34fb (Handle: 44): Battery Level
-> Characteristic Properties: ['read', 'notify']
-> Characteristic Obj: <CBCharacteristic: 0x7fb6ae0805d0, UUID = Battery Level, properties = 0x12, value = {length = 1, bytes = 0x64}, notifying = NO>
-> Characteristic Value: bytearray(b'd')

--> Descriptor: 00002902-0000-1000-8000-00805f9b34fb (Handle: 46): Client Characteristic Configuration
--> Descriptor Obj: <CBDescriptor: 0x7fb6ae77d960, UUID = Client Characteristic Configuration, value = (null)>
```
