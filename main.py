import numpy as np
import wave
import struct
from tqdm import tqdm
import os

def generate_sine_wave(frequency, duration, sample_rate=44100, amplitude=32767):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave_data = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave_data

# Function to generate a sine wave of a given frequency with fade in and fade out
def generate_sine_wave_with_fade(frequency, duration, fade_duration, sample_rate=44100, amplitude=32767):
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    wave_data = amplitude * np.sin(2 * np.pi * frequency * t)
    
    # Create fade in and fade out envelopes
    fade_in = np.linspace(0, 1, int(sample_rate * fade_duration))
    fade_out = np.linspace(1, 0, int(sample_rate * fade_duration))
    
    # Apply fade in
    if len(fade_in) < len(wave_data):
        wave_data[:len(fade_in)] *= fade_in
    
    # Apply fade out
    if len(fade_out) < len(wave_data):
        wave_data[-len(fade_out):] *= fade_out
    
    return wave_data

def binary_to_tones(binary_data, tone_duration=0.2, sample_rate=44100):
    tones = []
    
    freq_0 = 440  # A4
    freq_1 = 880  # A5
    
    for byte in tqdm(binary_data):
        for bit in f'{byte:08b}':
            if bit == '0':
                tone = generate_sine_wave(freq_0, tone_duration, sample_rate)
            else:
                tone = generate_sine_wave(freq_1, tone_duration, sample_rate)
            tones.append(tone)
    
    return np.concatenate(tones)

def nibble_to_tones(binary_data, tone_duration=0.2, sample_rate=44100):
    tones = []

    hex_to_frequency = {
        '0': 261.63,  # C4
        '1': 293.66,  # D4
        '2': 329.63,  # E4
        '3': 349.23,  # F4
        '4': 392.00,  # G4
        '5': 440.00,  # A4
        '6': 493.88,  # B4
        '7': 523.25,  # C5
        '8': 587.33,  # D5
        '9': 659.25,  # E5
        'a': 698.46,  # F5
        'b': 783.99,  # G5
        'c': 880.00,  # A5
        'd': 987.77,  # B5
        'e': 1046.50, # C6
        'f': 1174.66  # D6
    }

    silence_duration = 0.1
    
    for byte in tqdm(binary_data):
        for nibble in f'{byte:02x}':
            #tone = generate_sine_wave(hex_to_frequency[nibble], tone_duration, sample_rate)
            tone = generate_sine_wave_with_fade(hex_to_frequency[nibble], duration=tone_duration, fade_duration=0.05 * tone_duration, sample_rate=sample_rate)
            #silence = generate_silence(silence_duration, sample_rate)
            tones.append(tone)
            #tones.append(silence)
    
    return np.concatenate(tones)

def generate_silence(duration, sample_rate=44100):
    return np.zeros(int(sample_rate * duration), dtype=np.int16)

def save_wave_file(filename, data, sample_rate=44100):
    wave_file = wave.open(filename, 'w')
    
    wave_file.setparams((1, 2, sample_rate, 0, 'NONE', 'not compressed'))
    
    for value in data:
        wave_file.writeframes(struct.pack('<h', int(value)))
    
    wave_file.close()

def binary_file_to_music(binary_filename, output_wav_filename, tone_duration=0.1):
    song_duration = 60.0 # seconds

    bytes_to_read = int(song_duration / tone_duration)
    file_size = os.path.getsize(binary_filename)
    middle_point = file_size // 2
    start_point = max(0, middle_point - (bytes_to_read // 2))

    with open(binary_filename, 'rb') as file:
        file.seek(start_point)
        binary_data = file.read(bytes_to_read)

    # tones = binary_to_tones(binary_data, tone_duration)
    tones = nibble_to_tones(binary_data, tone_duration)

    save_wave_file(output_wav_filename, tones)

if __name__ == "__main__":
    binary_filename = "/home/eashan/BuckeyeVerticalSoftware/build/main"
    output_wav_filename = "output_music2.wav"
    binary_file_to_music(binary_filename, output_wav_filename)
