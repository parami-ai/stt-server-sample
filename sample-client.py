'''
Usage:
python sample-client.py <token>
'''

import sys
import asyncio
import socketio

sio = socketio.AsyncClient(engineio_logger=False, ssl_verify=False)

api_token = sys.argv[1]
if len(sys.argv) > 2:
    endpoint = sys.argv[2]
else:
    endpoint = "https://stt-2.parami.ai"

@sio.event
def disconnect():
    print("disconnected")


@sio.event
async def connect():
    print("connected")


@sio.event
async def speechData(data):
    print("received", data)


with open("demo_short.wav", "rb") as f:
    wav_content = f.read()

"""
Please follow the following encoding for the audio:

 codec_name:      pcm_s16le
 codec_long_name: PCM signed 16-bit little-endian
 sample_rate:     48000
 bits_per_sample: 16
 
"""

wav_content
# b'RIFF$e\x04...'

# Remove the header metadata, and keep just the data
wav_content = wav_content[44:]

print("No. of bytes:", len(wav_content))
# 480000 in bytes


async def main():
    await sio.connect(
        endpoint + "/socket.io",
        transports=["websocket"],
    )

    await sio.emit("authenticate", api_token)

    print(">> startStream")

    await sio.emit("startStream", {})

    print(">> streaming")

    # Or stream the audio wav content by keeping sending "binaryData" with the audio pytes
    await sio.emit("binaryData", wav_content)

    print(">> waiting")

    for _ in range(100):
        await sio.emit("binaryData", b"\x00")
        await asyncio.sleep(0.04)

    print(">> endStream")

    await sio.emit("endStream", "")

    await asyncio.sleep(2)


loop = asyncio.get_event_loop()
loop.run_until_complete(main())
