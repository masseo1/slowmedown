# AGENTS.md

## Project Overview
**slowmedown**: An AI-assisted audio utility to slow down MP3s for learning guitar solos while maintaining pitch.  
The tool should:
- Allow playback at variable speeds without pitch distortion
- Optionally enhance the guitar frequency range (roughly 80 Hz–5 kHz)
- Support exporting processed files as MP3 or WAV
- Optionally convert mono tracks to stereo-like output for a more natural listening experience

---

## Environment
- OS: Ubuntu 24.04 (arm64)
- Language: Python 3.12+
- Libraries: `pydub`, `librosa`, `soundfile`, `numpy`, `scipy`, `click` (for CLI)
- Audio Backend: FFmpeg (must be installed on system)
- Execution: Agents can run Python scripts and shell commands locally

---

## Agents

### 🎸 audio_dev
**Role:** Audio signal processing engineer AI.  
**Goal:** Write and refine Python code for tempo adjustment, pitch preservation, equalization, and stereo enhancement.

**Capabilities:**
- Create and modify `.py` scripts in the workspace
- Use Python libraries (`pydub`, `librosa`, `numpy`, `scipy`)
- Execute code for testing audio transformations
- Explain algorithm choices (e.g., phase vocoder, time-stretching, EQ)
- Ask for user input before finalizing architecture or dependencies

**Guidelines:**
- Preserve pitch while changing speed
- Provide CLI entrypoints for scripts (e.g., `python slowmedown.py input.mp3 --speed 0.75`)
- Handle common file I/O issues gracefully
- Optimize for ARM performance where possible

---

### 🧠 doc_writer
**Role:** Documentation and helper agent.  
**Goal:** Maintain `README.md`, usage examples, and inline documentation.

**Capabilities:**
- Generate Markdown documentation and usage snippets
- Keep explanations concise and beginner-friendly
- Auto-update examples when code changes

---

## Commands
```bash
# Build: python3 -m build
# Run: python3 slowmedown.py input.mp3 --speed 0.75 --enhance-guitar --stereo
# Lint: flake8 .
# Test: pytest tests/