# Testing Plan for slowmedown

## Overview
Create comprehensive tests for the audio processing pipeline to verify tempo changes, pitch preservation, frequency enhancement, and stereo conversion.

---

## Phase 1: Test Infrastructure Setup
- [x] Add `pytest` to requirements.txt
- [x] Create `tests/` directory
- [x] Create `tests/test_audio_processing.py` for unit tests
- [x] Create `tests/test_cli.py` for integration/CLI tests
- [x] Create `tests/conftest.py` for pytest fixtures (synthetic audio generation)

---

## Phase 2: Unit Tests - Audio Processing Functions

### 2.1 `change_speed_preserve_pitch()` Tests - Duration Verification
- [x] **Duration verification**: Output length = input length / speed_factor
  - Test with speed=0.75 (expect 1.33x longer)
  - Test with speed=1.5 (expect 0.67x shorter)
  - Test with speed=1.0 (expect same length)
- [x] **Array shape**: Verify output is 1D numpy array
- [x] **Sample rate**: Confirm SR unchanged

### 2.2 `change_speed_preserve_pitch()` Tests - Pitch Preservation (DEFERRED)
- [ ] **Pitch preservation**: Use `librosa.piptrack()` to extract fundamental frequency
  - Verify F0 remains constant despite tempo change
  - Note: Requires further research on reliable pitch extraction methods

### 2.3 `enhance_guitar_frequencies()` Tests
- [x] **Frequency boost verification**: Generate sine waves at test frequencies
  - 80 Hz (low end of boost range) - should be boosted
  - 1 kHz (middle of guitar range) - should be boosted most
  - 50 Hz (below range) - should be attenuated/unchanged
  - 8 kHz (above range) - should be attenuated/unchanged
- [x] **Normalization**: Verify output doesn't exceed [-1.0, 1.0]
- [x] **No clipping**: Check max(abs(output)) <= 1.0
- [x] **Array shape preservation**: Input shape == output shape

### 2.4 `mono_to_stereo_effect()` Tests
- [x] **Stereo output shape**: (2, n_samples) for mono input
- [x] **Already stereo passthrough**: Stereo input returns unchanged
- [x] **Channel difference**: Left != Right (verify Haas delay applied)
- [x] **Delay verification**: ~15ms offset between channels
- [x] **Amplitude check**: Both channels within [-1.0, 1.0]

---

## Phase 3: Integration Tests - CLI Command

### 3.1 File I/O Tests
- [x] Create small test MP3 fixture (~1 second sine wave)
- [x] Test basic slowdown: `--speed 0.75`
  - Verify output file created
  - Load output, check duration ratio
- [x] Test all options combined: `-s 0.5 -g -st`
- [x] Test output formats: MP3, WAV, OGG
- [x] Test custom output path: `-o custom.mp3`

### 3.2 End-to-End Verification
- [x] **Duration check**: 
  ```python
  input_duration = librosa.get_duration(filename=input_file)
  output_duration = librosa.get_duration(filename=output_file)
  assert abs(output_duration / input_duration - 1/speed_factor) < 0.05
  ```
- [x] **File existence**: Output file created and non-empty
- [x] **Format verification**: Can load output with librosa
- [x] **Stereo channel count**: Stereo flag produces 2 channels

---

## Phase 4: Edge Cases & Error Handling
- [ ] Empty/corrupted input file
- [ ] Invalid speed factors (0, negative, extreme values)
- [ ] Missing FFmpeg (should fail gracefully)
- [ ] Very short audio (<100ms)
- [ ] Very long audio (memory handling)
- [ ] Unicode filenames

---

## Testing Strategy

### Synthetic Audio Generation
Create fixtures with known properties:
```python
def generate_sine_wave(frequency, duration, sr=22050):
    """Generate pure sine wave for testing"""
    t = np.linspace(0, duration, int(sr * duration))
    return np.sin(2 * np.pi * frequency * t), sr
```

### Key Verification Methods

**1. Duration Testing (Primary slowdown verification)**
```python
original_duration = len(audio_data) / sr
processed_duration = len(processed_audio) / sr
expected_duration = original_duration / speed_factor
assert abs(processed_duration - expected_duration) < 0.1  # 100ms tolerance
```

**2. Pitch Preservation Testing**
```python
# Extract fundamental frequencies
pitches_original, mag_orig = librosa.piptrack(y=original, sr=sr)
pitches_processed, mag_proc = librosa.piptrack(y=processed, sr=sr)

# Compare dominant frequencies (should be similar despite tempo change)
f0_orig = extract_dominant_pitch(pitches_original, mag_orig)
f0_proc = extract_dominant_pitch(pitches_processed, mag_proc)
assert abs(f0_orig - f0_proc) < 5  # Within 5 Hz
```

**3. Frequency Response Testing**
```python
# Generate test frequencies across spectrum
test_freqs = [50, 80, 500, 1000, 3000, 5000, 8000, 10000]
for freq in test_freqs:
    signal, sr = generate_sine_wave(freq, 1.0)
    enhanced = enhance_guitar_frequencies(signal, sr)
    
    # Compare amplitudes
    amp_original = np.max(np.abs(signal))
    amp_enhanced = np.max(np.abs(enhanced))
    
    # Frequencies in 80-5000Hz should be boosted
    if 80 <= freq <= 5000:
        assert amp_enhanced >= amp_original
```

---

## Test Execution Commands
```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=slowmedown --cov-report=html

# Run specific test file
pytest tests/test_audio_processing.py -v

# Run specific test
pytest tests/test_audio_processing.py::test_speed_change_duration -v
```

---

## Success Criteria
- [x] All unit tests pass
- [x] All integration tests pass
- [ ] Code coverage > 80%
- [ ] Edge cases handled gracefully
- [ ] Tests run in < 30 seconds
- [x] No actual large audio files in repo (use synthetic signals)
