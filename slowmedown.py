#!/usr/bin/env python3
import os
import click
import librosa
import soundfile as sf
import numpy as np
from scipy import signal
from pydub import AudioSegment


def change_speed_preserve_pitch(audio_data, sr, speed_factor):
    """
    Change playback speed while preserving pitch using librosa's phase vocoder.
    
    Args:
        audio_data: numpy array of audio samples
        sr: sample rate
        speed_factor: float, e.g., 0.75 for 75% speed, 1.5 for 150% speed
    
    Returns:
        numpy array of time-stretched audio
    """
    stretched = librosa.effects.time_stretch(audio_data, rate=speed_factor)
    return stretched


def enhance_guitar_frequencies(audio_data, sr):
    """
    Enhance guitar frequency range (60 Hz - 5 kHz) using parametric EQ.
    Covers low E string (~82 Hz) down to bass fundamentals.
    
    Args:
        audio_data: numpy array of audio samples
        sr: sample rate
    
    Returns:
        numpy array with enhanced guitar frequencies
    """
    nyquist = sr / 2
    
    # Design bandpass filter for guitar range (60 Hz - 5 kHz)
    low_freq = 60 / nyquist
    high_freq = 5000 / nyquist
    
    # Create a gentle boost using a bandpass filter
    sos = signal.butter(4, [low_freq, high_freq], btype='band', output='sos')
    filtered = signal.sosfilt(sos, audio_data)
    
    # Mix original with filtered to boost guitar range by ~3dB
    enhanced = audio_data + filtered * 0.4
    
    # Normalize to prevent clipping
    max_val = np.max(np.abs(enhanced))
    if max_val > 1.0:
        enhanced = enhanced / max_val
    
    return enhanced


def mono_to_stereo_effect(audio_data, sr):
    """
    Convert mono audio to pseudo-stereo using phase and delay techniques.
    
    Args:
        audio_data: numpy array of mono audio samples
        sr: sample rate
    
    Returns:
        numpy array with shape (2, n_samples) for stereo output
    """
    if len(audio_data.shape) > 1 and audio_data.shape[0] == 2:
        return audio_data
    
    # Create slight delay for right channel (Haas effect)
    delay_samples = int(0.015 * sr)  # 15ms delay
    
    left_channel = audio_data
    right_channel = np.concatenate([np.zeros(delay_samples), audio_data[:-delay_samples]])
    
    # Apply slight phase shift to right channel using all-pass filter
    b, a = signal.iirfilter(2, 0.5, btype='lowpass', ftype='butter', output='ba')
    right_channel = signal.filtfilt(b, a, right_channel)
    
    # Reduce intensity slightly to create width
    left_channel = left_channel * 0.95
    right_channel = right_channel * 0.85
    
    stereo = np.vstack([left_channel, right_channel])
    return stereo


@click.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--speed', '-s', default=1.0, help='Playback speed factor (e.g., 0.75 for 75% speed)', type=float)
@click.option('--enhance-guitar', '-g', is_flag=True, help='Enhance guitar frequency range (80 Hz - 5 kHz)')
@click.option('--stereo', '-st', is_flag=True, help='Convert mono to pseudo-stereo')
@click.option('--output', '-o', default=None, help='Output file path (default: input_slowed.mp3)', type=click.Path())
@click.option('--format', '-f', default='mp3', type=click.Choice(['mp3', 'wav', 'ogg'], case_sensitive=False), help='Output format')
def slowmedown(input_file, speed, enhance_guitar, stereo, output, format):
    """
    Slow down MP3/audio files for guitar practice while preserving pitch.
    
    Example: python slowmedown.py song.mp3 --speed 0.75 --enhance-guitar --stereo
    """
    click.echo(f"Loading audio file: {input_file}")
    
    # Load audio with librosa
    audio_data, sr = librosa.load(input_file, sr=None, mono=True)
    
    click.echo(f"Sample rate: {sr} Hz, Duration: {len(audio_data)/sr:.2f}s")
    
    # Apply speed change if needed
    if speed != 1.0:
        click.echo(f"Changing speed to {speed*100:.0f}%...")
        audio_data = change_speed_preserve_pitch(audio_data, sr, speed)
    
    # Apply guitar enhancement if requested
    if enhance_guitar:
        click.echo("Enhancing guitar frequencies (80 Hz - 5 kHz)...")
        audio_data = enhance_guitar_frequencies(audio_data, sr)
    
    # Apply stereo effect if requested
    if stereo:
        click.echo("Creating stereo effect...")
        audio_data = mono_to_stereo_effect(audio_data, sr)
    else:
        # Ensure proper shape for mono
        if len(audio_data.shape) == 1:
            audio_data = audio_data.reshape(1, -1)
    
    # Determine output filename
    if output is None:
        base, ext = os.path.splitext(input_file)
        output = f"{base}_slowed.{format}"
    
    # Export processed audio
    click.echo(f"Exporting to {output}...")
    
    # Transpose if needed for soundfile (expects channels last)
    if len(audio_data.shape) == 2:
        audio_data = audio_data.T
    
    # Write to temporary WAV file
    temp_wav = output.replace(f'.{format}', '_temp.wav')
    sf.write(temp_wav, audio_data, sr)
    
    # Convert to final format if MP3 or OGG
    if format.lower() == 'mp3':
        audio_segment = AudioSegment.from_wav(temp_wav)
        audio_segment.export(output, format='mp3', bitrate='320k')
        os.remove(temp_wav)
    elif format.lower() == 'ogg':
        audio_segment = AudioSegment.from_wav(temp_wav)
        audio_segment.export(output, format='ogg', codec='libvorbis')
        os.remove(temp_wav)
    else:
        os.rename(temp_wav, output)
    
    click.echo(f"✓ Done! Saved to {output}")


if __name__ == '__main__':
    slowmedown()
