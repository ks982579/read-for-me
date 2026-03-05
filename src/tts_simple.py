import torch
import numpy as np
from scipy.io.wavfile import write
from time import sleep
from functools import partial

# Patch torch.load - safe since TTS checkpoints are trusted
torch.load = partial(torch.load, weights_only=False)

from TTS.api import TTS

TEST = False

# read_path = '/home/kevinsullivan/University/InternationalUniversity/13_NetworksDistributedSystems/PearsonAudio/ch1.txt'
read_path = '/home/kevinsullivan/University/InternationalUniversity/13_NetworksDistributedSystems/materials/networks_course_book_u06.txt'
# read_path = '/home/kevinsullivan/Projects/survival-guides/computers/networking/'
write_path = '/home/kevinsullivan/Downloads'
# filename = 'computer-networks-pearson-ch1'
# filename = 'networking-unit-6-3'
filename = 'networking-coursebook-u06'

# def chunk_text(text, max_chars=200):
#     sentences = text.replace('!', '.').replace('?', '.').

TTS_MODELS = [
    'tts_models/multilingual/multi-dataset/xtts_v2', 
    'tts_models/multilingual/multi-dataset/xtts_v1.1', 
    'tts_models/multilingual/multi-dataset/your_tts',
    'tts_models/multilingual/multi-dataset/bark', 
    'tts_models/bg/cv/vits', 
    'tts_models/cs/cv/vits', 
    'tts_models/da/cv/vits', 
    'tts_models/et/cv/vits', 
    'tts_models/ga/cv/vits',
    'tts_models/en/ek1/tacotron2', # too big?
    'tts_models/en/ljspeech/tacotron2-DDC',
    'tts_models/en/ljspeech/tacotron2-DDC_ph',
    'tts_models/en/ljspeech/glow-tts',
    'tts_models/en/ljspeech/speedy-speech',
    'tts_models/en/ljspeech/tacotron2-DCA',
    'tts_models/en/ljspeech/vits',
    'tts_models/en/ljspeech/vits--neon',
    'tts_models/en/ljspeech/fast_pitch',
    'tts_models/en/ljspeech/overflow', # Good but does not do long sentences
    'tts_models/en/ljspeech/neural_hmm',
    'tts_models/en/vctk/vits',
    'tts_models/en/vctk/fast_pitch',
    'tts_models/en/sam/tacotron-DDC',
    'tts_models/en/blizzard2013/capacitron-t2-c50',
    'tts_models/en/blizzard2013/capacitron-t2-c150_v2',
    'tts_models/en/multi-dataset/tortoise-v2',
    'tts_models/en/jenny/jenny',
    'tts_models/es/mai/tacotron2-DDC',
    'tts_models/es/css10/vits',
    'tts_models/fr/mai/tacotron2-DDC',
    'tts_models/fr/css10/vits',
    'tts_models/uk/mai/glow-tts',
    'tts_models/uk/mai/vits',
    'tts_models/zh-CN/baker/tacotron2-DDC-GST',
    'tts_models/nl/mai/tacotron2-DDC',
    'tts_models/nl/css10/vits',
    'tts_models/de/thorsten/tacotron2-DCA',
    'tts_models/de/thorsten/vits',
    'tts_models/de/thorsten/tacotron2-DDC',
    'tts_models/de/css10/vits-neon',
    'tts_models/ja/kokoro/tacotron2-DDC',
    'tts_models/tr/common-voice/glow-tts',
    'tts_models/it/mai_female/glow-tts',
    'tts_models/it/mai_female/vits',
    'tts_models/it/mai_male/glow-tts',
    'tts_models/it/mai_male/vits',
    'tts_models/ewe/openbible/vits',
    'tts_models/hau/openbible/vits',
    'tts_models/lin/openbible/vits',
    'tts_models/tw_akuapem/openbible/vits',
    'tts_models/tw_asante/openbible/vits',
    'tts_models/yor/openbible/vits',
    'tts_models/hu/css10/vits',
    'tts_models/el/cv/vits',
    'tts_models/fi/css10/vits',
    'tts_models/hr/cv/vits',
    'tts_models/lt/cv/vits',
    'tts_models/lv/cv/vits',
    'tts_models/mt/cv/vits',
    'tts_models/pl/mai_female/vits',
    'tts_models/pt/cv/vits',
    'tts_models/ro/cv/vits',
    'tts_models/sk/cv/vits',
    'tts_models/sl/cv/vits',
    'tts_models/sv/cv/vits',
    'tts_models/ca/custom/vits',
    'tts_models/fa/custom/glow-tts',
    'tts_models/bn/custom/vits-male',
    'tts_models/bn/custom/vits-female',
    'tts_models/be/common-voice/glow-tts'
]

def test():
    tts = TTS()
    print(tts.list_models().list_tts_models())

def main():
    if torch.cuda.is_available():
        free, total = torch.cuda.mem_get_info()
        print(f"VRAM Free: {free/1e9:.1f} GB / {total/1e9:.1f} GB")
        sleep(3)
    device = 'cuda' if torch.cuda.is_available() else 'cpu'
    # tts = TTS("tts_models/en/ek1/tacotron2").to(device) # fills up nvidia
    tts = TTS(
        # model_name="tts_models/en/ljspeech/overflow", # OK - long sentences sometimes don't work
        model_name="tts_models/en/jenny/jenny",
        gpu=True
    ).to(device)

    with open(read_path, 'r') as file:
        lines = file.readlines()


    # samples = []
    # for line in lines:
    #     that = line.strip()
    #     if that is not None and that != '':
    #         samples.extend(tts.tts(text=line, split_sentences=False))
    #
    # audio = np.array(samples, dtype=np.float32)

    # normalize to  int16 for WAV
    # audio_int16 = (audio * 32767).astype(np.int16)
    # write(f"{write_path}/{filename}.wav", rate=22050, data=audio_int16)
    # print('done?')

    # do formatting magic if desired
    text = ' '.join(lines)
    intro = "Hi, I am Jenny and I will be your voice for this reading. Get ready to learn bitch!"
    text = intro + ' ' + text

    # text = CONTENT
    tts.tts_to_file(
        text=text,
        speed=1,
        file_path=f"{write_path}/{filename}.mp3",
        split_sentences=True,
    )


CONTENT = """
Pervasive Computing and the Internet of Things: A Comprehensive Guide.
Introduction to Pervasive Computing.
Pervasive computing, also known as ubiquitous computing, aims to make computing available from any geographical location and electronic device at any time. Unlike traditional computing limited to desktop or laptop computers, pervasive computing extends to cellphones, sensors, actuators, home appliances, and wearable devices. The goal is to make computing omnipresent—available everywhere and anywhere you need it.

Core Properties of Pervasive Computing.
According to Poslad (2011), pervasive computing systems exhibit five essential properties:

Context Awareness: Network nodes must understand their environment and context to optimize performance.
Distribution: Systems are deployed across distributed networks rather than centralized infrastructure.
Autonomy: Network nodes are self-governing and operate without human intervention.
Human-Computer Interaction (HCI): Interactions should be minimized and hidden from users.
Intelligence: Nodes integrate artificial intelligence to make smart decisions.
From Traditional Internet to IoT.
The Internet of Things (IoT) represents one of the most significant outcomes of pervasive computing. While the traditional internet connects only computers, IoT expands connectivity to include a vast array of electronics—sensors, actuators, home appliances, handheld devices, and switches. This fundamental difference transforms how devices interact and share data in our connected world.

IoT Protocol Standards.
The Internet Engineering Task Force (IETF) established the Constrained RESTful Environments (CoRE) research group to develop protocol standards specifically for constrained IP networks. These networks feature nodes with limited memory, low power consumption, and low throughput capacity—characteristics typical of IoT devices.

Constrained Application Protocol (CoAP).
CoAP is a specialized web transfer protocol designed for wireless networks with severely constrained nodes. These devices often have:

8-bit microcontrollers.
Small ROM and RAM.
Low power consumption.
Low data transfer rates.
CoAP operates on a request/response architecture similar to HTTP but optimized for constrained environments. It incorporates fundamental web concepts like Uniform Resource Identifiers (URIs) and media types. The protocol is standardized in RFCs 7252, 7959, 8613, and 8974.

IPv6 over Low-Power Wireless Personal Area Networks (6LoWPAN).
6LoWPAN enables IPv6 communication over Low-Power Wireless Personal Area Networks (LoWPAN). These networks consist of devices with:

Low power consumption.
Limited computation speed.
Restricted memory.
Low bit rates.
Devices in a LoWPAN follow the IEEE 802.15.4-2003 standard. The 6LoWPAN network assumptions, problem statements, and goals are standardized in RFC 4919.

WebSocket Protocol.
WebSocket serves a different purpose within the IoT ecosystem. It supports browser-based applications requiring bidirectional communication with servers without the overhead of opening multiple HTTP connections.

Key characteristics:

Operates over ports 80 and 443 to leverage existing HTTP proxies.
Utilizes existing infrastructure concepts (proxies, filtering, authentication).
Defined in RFC 6455.
IoT Technologies and Hardware Platforms.
Advances in System-on-Chip (SoC) technology have produced low-power, low-cost, lightweight network nodes that serve as hardware platforms for various IoT implementations.

Radio Frequency Identification (RFID).
RFID systems use electromagnetic fields to identify, track objects, and record data. The system architecture includes:

RFID Tags (Transponders):

Attached to target objects.
Passive tags: Powered by radio waves from the reader (no battery).
Active tags: Battery-powered for longer range and independent operation.
Function as both transmitters and responders.
RFID Readers:

Act as transceivers.
Contain a Radio Frequency Interface (RFI) module.
Include a wireless switch.
Emit radio waves to power passive tags and communicate with all tags.
Long Range (LoRa).
LoRa is a spread spectrum modulation technique designed for Low-Power Wide Area Network (LPWAN) technology. It excels at providing long-range communication using minimal power—for example, communicating over 160 meters using just 86.5 megajoules of energy.

Frequency Bands:

European Union: 868 MHz and 433 MHz.
United States: 915 MHz and 433 MHz.
These operate on Industrial, Scientific, and Medical (ISM) band frequencies. LoRaWAN is the MAC layer protocol that operates on networks with star topology.

NodeMCU.
NodeMCU is an open-source firmware and development kit for building IoT products. It's based on the Espressif Non-OS SDK for the ESP8266, a low-cost Wi-Fi chip featuring:

Full TCP/IP stack.
Microcontroller capabilities.
Developed by Espressif Systems (Chinese manufacturer based in Shanghai).
Conclusion.
Pervasive computing and IoT represent a paradigm shift in how we interact with technology. By understanding the protocols (CoAP, 6LoWPAN, WebSocket) and technologies (RFID, LoRa, NodeMCU) that power these systems, we can better appreciate the infrastructure enabling our increasingly connected world. As these technologies continue to evolve, they promise even more seamless integration of computing into every aspect of our daily lives.
"""

if __name__ == "__main__":
    if TEST:
        test()
    else:
        main()
