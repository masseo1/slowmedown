import pytest
import os
import tempfile
import numpy as np
import soundfile as sf
import librosa
from click.testing import CliRunner
from slowmedown import slowmedown


@pytest.fixture
def cli_runner():
    """Fixture for Click CLI testing."""
    return CliRunner()


@pytest.fixture
def temp_audio_file(generate_sine_wave):
    """Create a temporary MP3 file for testing."""
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
        temp_path = f.name
    
    audio_data, sr = generate_sine_wave(440, 1.0, 22050)
    
    wav_temp = temp_path.replace('.mp3', '_temp.wav')
    sf.write(wav_temp, audio_data, sr)
    
    from pydub import AudioSegment
    audio_segment = AudioSegment.from_wav(wav_temp)
    audio_segment.export(temp_path, format='mp3')
    os.remove(wav_temp)
    
    yield temp_path
    
    if os.path.exists(temp_path):
        os.remove(temp_path)


class TestCLIBasic:
    """Basic CLI integration tests."""
    
    def test_basic_slowdown(self, cli_runner, temp_audio_file):
        """Test basic slowdown with --speed 0.75."""
        output_path = temp_audio_file.replace('.mp3', '_slowed.mp3')
        
        try:
            result = cli_runner.invoke(slowmedown, [temp_audio_file, '--speed', '0.75'])
            
            assert result.exit_code == 0
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
            
            input_duration = librosa.get_duration(filename=temp_audio_file)
            output_duration = librosa.get_duration(filename=output_path)
            
            expected_duration = input_duration / 0.75
            assert abs(output_duration - expected_duration) < 0.2
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
    
    def test_all_options_combined(self, cli_runner, temp_audio_file):
        """Test all options: speed, guitar enhancement, stereo."""
        output_path = temp_audio_file.replace('.mp3', '_slowed.mp3')
        
        try:
            result = cli_runner.invoke(slowmedown, [
                temp_audio_file,
                '--speed', '0.5',
                '--enhance-guitar',
                '--stereo'
            ])
            
            assert result.exit_code == 0
            assert os.path.exists(output_path)
            
            audio_data, sr = librosa.load(output_path, sr=None, mono=False)
            
            if len(audio_data.shape) == 2:
                assert audio_data.shape[0] == 2
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
    
    def test_custom_output_path(self, cli_runner, temp_audio_file):
        """Test custom output path with -o."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = os.path.join(tmpdir, 'custom_output.mp3')
            
            result = cli_runner.invoke(slowmedown, [
                temp_audio_file,
                '--speed', '0.75',
                '-o', output_path
            ])
            
            assert result.exit_code == 0
            assert os.path.exists(output_path)


class TestCLIFormats:
    """Test different output formats."""
    
    def test_mp3_output(self, cli_runner, temp_audio_file):
        """Test MP3 output format."""
        output_path = temp_audio_file.replace('.mp3', '_slowed.mp3')
        
        try:
            result = cli_runner.invoke(slowmedown, [
                temp_audio_file,
                '--speed', '0.75',
                '--format', 'mp3'
            ])
            
            assert result.exit_code == 0
            assert os.path.exists(output_path)
            assert output_path.endswith('.mp3')
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
    
    def test_wav_output(self, cli_runner, temp_audio_file):
        """Test WAV output format."""
        output_path = temp_audio_file.replace('.mp3', '_slowed.wav')
        
        try:
            result = cli_runner.invoke(slowmedown, [
                temp_audio_file,
                '--speed', '0.75',
                '--format', 'wav'
            ])
            
            assert result.exit_code == 0
            assert os.path.exists(output_path)
            assert output_path.endswith('.wav')
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
    
    def test_ogg_output(self, cli_runner, temp_audio_file):
        """Test OGG output format."""
        output_path = temp_audio_file.replace('.mp3', '_slowed.ogg')
        
        try:
            result = cli_runner.invoke(slowmedown, [
                temp_audio_file,
                '--speed', '0.75',
                '--format', 'ogg'
            ])
            
            assert result.exit_code == 0
            assert os.path.exists(output_path)
            assert output_path.endswith('.ogg')
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)


class TestCLIEndToEnd:
    """End-to-end verification tests."""
    
    def test_duration_accuracy(self, cli_runner, temp_audio_file):
        """Test that output duration matches expected ratio."""
        output_path = temp_audio_file.replace('.mp3', '_slowed.mp3')
        speed_factor = 0.75
        
        try:
            result = cli_runner.invoke(slowmedown, [
                temp_audio_file,
                '--speed', str(speed_factor)
            ])
            
            assert result.exit_code == 0
            
            input_duration = librosa.get_duration(filename=temp_audio_file)
            output_duration = librosa.get_duration(filename=output_path)
            
            expected_ratio = 1 / speed_factor
            actual_ratio = output_duration / input_duration
            
            assert abs(actual_ratio - expected_ratio) < 0.05
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
    
    def test_stereo_channel_count(self, cli_runner, temp_audio_file):
        """Test that stereo flag produces 2 channels."""
        output_path = temp_audio_file.replace('.mp3', '_slowed.mp3')
        
        try:
            result = cli_runner.invoke(slowmedown, [
                temp_audio_file,
                '--stereo'
            ])
            
            assert result.exit_code == 0
            
            audio_data, sr = librosa.load(output_path, sr=None, mono=False)
            
            if len(audio_data.shape) == 2:
                assert audio_data.shape[0] == 2
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
    
    def test_file_loadable(self, cli_runner, temp_audio_file):
        """Test that output file can be loaded with librosa."""
        output_path = temp_audio_file.replace('.mp3', '_slowed.mp3')
        
        try:
            result = cli_runner.invoke(slowmedown, [temp_audio_file, '--speed', '0.75'])
            
            assert result.exit_code == 0
            
            audio_data, sr = librosa.load(output_path, sr=None)
            
            assert audio_data is not None
            assert len(audio_data) > 0
            assert sr > 0
        finally:
            if os.path.exists(output_path):
                os.remove(output_path)
