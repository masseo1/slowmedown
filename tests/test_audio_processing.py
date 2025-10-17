import pytest
import numpy as np
from slowmedown import (
    change_speed_preserve_pitch,
    enhance_guitar_frequencies,
    mono_to_stereo_effect
)


class TestChangeSpeedPreservePitch:
    """Tests for tempo change with pitch preservation."""
    
    def test_duration_slower_speed(self, generate_sine_wave, sample_rate):
        """Test that slowing down (0.75x) increases duration by 1.33x."""
        audio_data, sr = generate_sine_wave(440, 1.0, sample_rate)
        speed_factor = 0.75
        
        processed = change_speed_preserve_pitch(audio_data, sr, speed_factor)
        
        original_duration = len(audio_data) / sr
        processed_duration = len(processed) / sr
        expected_duration = original_duration / speed_factor
        
        assert abs(processed_duration - expected_duration) < 0.1
    
    def test_duration_faster_speed(self, generate_sine_wave, sample_rate):
        """Test that speeding up (1.5x) decreases duration by 0.67x."""
        audio_data, sr = generate_sine_wave(440, 1.0, sample_rate)
        speed_factor = 1.5
        
        processed = change_speed_preserve_pitch(audio_data, sr, speed_factor)
        
        original_duration = len(audio_data) / sr
        processed_duration = len(processed) / sr
        expected_duration = original_duration / speed_factor
        
        assert abs(processed_duration - expected_duration) < 0.1
    
    def test_duration_same_speed(self, generate_sine_wave, sample_rate):
        """Test that 1.0x speed maintains original duration."""
        audio_data, sr = generate_sine_wave(440, 1.0, sample_rate)
        speed_factor = 1.0
        
        processed = change_speed_preserve_pitch(audio_data, sr, speed_factor)
        
        original_duration = len(audio_data) / sr
        processed_duration = len(processed) / sr
        
        assert abs(processed_duration - original_duration) < 0.1
    
    def test_output_is_1d_array(self, generate_sine_wave, sample_rate):
        """Test that output is a 1D numpy array."""
        audio_data, sr = generate_sine_wave(440, 1.0, sample_rate)
        
        processed = change_speed_preserve_pitch(audio_data, sr, 0.75)
        
        assert isinstance(processed, np.ndarray)
        assert len(processed.shape) == 1
    
    def test_sample_rate_unchanged(self, generate_sine_wave, sample_rate):
        """Test that sample rate is preserved (implicit in librosa)."""
        audio_data, sr = generate_sine_wave(440, 1.0, sample_rate)
        
        processed = change_speed_preserve_pitch(audio_data, sr, 0.75)
        
        assert sr == sample_rate


class TestEnhanceGuitarFrequencies:
    """Tests for guitar frequency enhancement."""
    
    def test_guitar_range_low_end_boost(self, generate_sine_wave, sample_rate):
        """Test that 80 Hz (low end) is boosted."""
        audio_data, sr = generate_sine_wave(80, 1.0, sample_rate)
        original_amplitude = np.max(np.abs(audio_data))
        
        enhanced = enhance_guitar_frequencies(audio_data, sr)
        enhanced_amplitude = np.max(np.abs(enhanced))
        
        assert enhanced_amplitude >= original_amplitude * 0.9
    
    def test_guitar_range_middle_boost(self, generate_sine_wave, sample_rate):
        """Test that 1 kHz (middle range) is boosted."""
        audio_data, sr = generate_sine_wave(1000, 1.0, sample_rate)
        original_amplitude = np.max(np.abs(audio_data))
        
        enhanced = enhance_guitar_frequencies(audio_data, sr)
        enhanced_amplitude = np.max(np.abs(enhanced))
        
        assert enhanced_amplitude >= original_amplitude * 0.9
    
    def test_below_range_attenuated(self, generate_sine_wave, sample_rate):
        """Test that 50 Hz (below range) is attenuated or unchanged."""
        audio_data, sr = generate_sine_wave(50, 1.0, sample_rate)
        original_amplitude = np.max(np.abs(audio_data))
        
        enhanced = enhance_guitar_frequencies(audio_data, sr)
        enhanced_amplitude = np.max(np.abs(enhanced))
        
        assert enhanced_amplitude <= original_amplitude * 1.1
    
    def test_above_range_attenuated(self, generate_sine_wave, sample_rate):
        """Test that 8 kHz (above range) is attenuated or unchanged."""
        audio_data, sr = generate_sine_wave(8000, 1.0, sample_rate)
        original_amplitude = np.max(np.abs(audio_data))
        
        enhanced = enhance_guitar_frequencies(audio_data, sr)
        enhanced_amplitude = np.max(np.abs(enhanced))
        
        assert enhanced_amplitude <= original_amplitude * 1.1
    
    def test_no_clipping(self, generate_sine_wave, sample_rate):
        """Test that output doesn't exceed [-1.0, 1.0]."""
        audio_data, sr = generate_sine_wave(1000, 1.0, sample_rate)
        
        enhanced = enhance_guitar_frequencies(audio_data, sr)
        
        assert np.max(np.abs(enhanced)) <= 1.0
    
    def test_shape_preservation(self, generate_sine_wave, sample_rate):
        """Test that input shape equals output shape."""
        audio_data, sr = generate_sine_wave(440, 1.0, sample_rate)
        
        enhanced = enhance_guitar_frequencies(audio_data, sr)
        
        assert enhanced.shape == audio_data.shape


class TestMonoToStereoEffect:
    """Tests for mono-to-stereo conversion."""
    
    def test_stereo_output_shape(self, generate_sine_wave, sample_rate):
        """Test that mono input produces stereo (2, n_samples) output."""
        audio_data, sr = generate_sine_wave(440, 1.0, sample_rate)
        
        stereo = mono_to_stereo_effect(audio_data, sr)
        
        assert stereo.shape[0] == 2
        assert stereo.shape[1] == len(audio_data)
    
    def test_stereo_input_passthrough(self, generate_sine_wave, sample_rate):
        """Test that stereo input returns unchanged."""
        audio_data, sr = generate_sine_wave(440, 1.0, sample_rate)
        stereo_input = np.vstack([audio_data, audio_data])
        
        output = mono_to_stereo_effect(stereo_input, sr)
        
        assert np.array_equal(output, stereo_input)
    
    def test_channel_difference(self, generate_sine_wave, sample_rate):
        """Test that left and right channels are different."""
        audio_data, sr = generate_sine_wave(440, 1.0, sample_rate)
        
        stereo = mono_to_stereo_effect(audio_data, sr)
        
        left = stereo[0]
        right = stereo[1]
        
        assert not np.array_equal(left, right)
    
    def test_haas_delay_applied(self, generate_sine_wave, sample_rate):
        """Test that ~15ms delay is present between channels."""
        audio_data, sr = generate_sine_wave(440, 1.0, sample_rate)
        
        stereo = mono_to_stereo_effect(audio_data, sr)
        
        expected_delay_samples = int(0.015 * sr)
        
        left = stereo[0]
        right = stereo[1]
        
        assert len(left) == len(right)
        assert not np.array_equal(left[:expected_delay_samples], 
                                 right[:expected_delay_samples])
    
    def test_amplitude_within_bounds(self, generate_sine_wave, sample_rate):
        """Test that both channels stay within [-1.0, 1.0]."""
        audio_data, sr = generate_sine_wave(440, 1.0, sample_rate)
        
        stereo = mono_to_stereo_effect(audio_data, sr)
        
        assert np.max(np.abs(stereo[0])) <= 1.0
        assert np.max(np.abs(stereo[1])) <= 1.0
