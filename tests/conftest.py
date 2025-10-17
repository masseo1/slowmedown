import pytest
import numpy as np


@pytest.fixture
def generate_sine_wave():
    """Factory fixture to generate pure sine waves for testing."""
    def _generate(frequency, duration, sr=22050):
        """Generate a pure sine wave at given frequency.
        
        Args:
            frequency: Frequency in Hz
            duration: Duration in seconds
            sr: Sample rate (default 22050)
            
        Returns:
            tuple: (audio_data, sample_rate)
        """
        t = np.linspace(0, duration, int(sr * duration), endpoint=False)
        audio_data = np.sin(2 * np.pi * frequency * t)
        return audio_data, sr
    return _generate


@pytest.fixture
def sample_rate():
    """Standard sample rate for testing."""
    return 22050
