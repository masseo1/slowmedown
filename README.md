# slowmedown 🎸

AI-assisted audio utility to slow down MP3s for learning guitar solos while maintaining pitch.

## Features

- **Variable Speed Playback**: Slow down audio without pitch distortion using phase vocoder
- **Guitar Frequency Enhancement**: Boost the guitar range (80 Hz - 5 kHz) for clearer solos
- **Mono-to-Stereo Effect**: Create a natural stereo-like listening experience
- **Multiple Export Formats**: Save as MP3 or WAV

## Installation

### Prerequisites
- Python 3.12+
- FFmpeg (required for MP3 support)

```bash
# Install FFmpeg on Ubuntu
sudo apt-get update
sudo apt-get install ffmpeg

# Install Python dependencies
pip install -r requirements.txt
```

## Usage

### Basic Commands

```bash
# Slow down to 75% speed
python slowmedown.py song.mp3 --speed 0.75

# Slow down + enhance guitar frequencies
python slowmedown.py solo.mp3 --speed 0.5 --enhance-guitar

# Full processing: slow + enhance + stereo
python slowmedown.py track.mp3 --speed 0.75 --enhance-guitar --stereo

# Export as WAV instead of MP3
python slowmedown.py song.mp3 --speed 0.8 --format wav

# Specify output file
python slowmedown.py input.mp3 --speed 0.75 --output practice.mp3
```

### CLI Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--speed` | `-s` | Playback speed factor (e.g., 0.75 = 75% speed) | 1.0 |
| `--enhance-guitar` | `-g` | Boost guitar frequency range | Off |
| `--stereo` | `-st` | Convert mono to pseudo-stereo | Off |
| `--output` | `-o` | Output file path | `input_slowed.mp3` |
| `--format` | `-f` | Output format (mp3 or wav) | mp3 |

## Examples

### Learning a Fast Solo
```bash
python slowmedown.py eruption.mp3 --speed 0.6 --enhance-guitar --stereo -o practice.mp3
```

### Light Processing
```bash
python slowmedown.py blues.mp3 --speed 0.85
```

## How It Works

- **Pitch Preservation**: Uses librosa's time-stretch algorithm (phase vocoder) to change tempo without affecting pitch
- **Guitar EQ**: Applies a bandpass filter with gentle boost in the 80 Hz - 5 kHz range where guitars typically sit
- **Stereo Effect**: Creates pseudo-stereo using Haas effect (slight delay) and phase manipulation for natural width

## Technical Details

- **Sample Rate**: Preserves original sample rate
- **Bit Depth**: 16-bit (standard for MP3/WAV)
- **MP3 Bitrate**: 320kbps for high quality exports
- **Processing**: All DSP done in float32 for precision, normalized to prevent clipping

## License

MIT
Takes Mono sound files, makes them sound a bit like stereo
