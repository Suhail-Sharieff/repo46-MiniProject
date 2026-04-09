
# 🔊 Report 3: Audio Steganography

## 3.1 Overview

Audio steganography embeds secret data within audio sample bytes using a **modified LSB technique**. The project specifically targets **WAV (Waveform Audio File Format)** files — uncompressed audio where every byte is a raw audio sample.

**Why WAV and not MP3?**
- MP3 uses **lossy compression** — it discards audio data it deems unimportant. This would also destroy our hidden bits!
- WAV is uncompressed — every byte is exactly what was stored, making bit-level modifications reliable.

---

## 3.2 WAV File Structure

A WAV file consists of:
```
[RIFF Header][fmt chunk][data chunk]
```

The **data chunk** contains raw PCM audio samples. For a standard 16-bit stereo WAV:
```
Sample Rate: 44,100 Hz (44,100 samples per second)
Bit Depth: 16 bits (2 bytes per sample)
Channels: 2 (stereo)
= 44100 × 2 bytes × 2 channels = 176,400 bytes per second
```

This gives plenty of room to hide data — modifying 1 bit per byte out of 176,400 bytes per second.

---

## 3.3 The 2-Bit Indicator Scheme

This project uses a more sophisticated approach than simple LSB — it employs **2 bit positions per byte**:

| Bit Position | Role | Binary Mask |
|-------------|------|------------|
| Bit 1 (2nd from right) | **Indicator flag** | `11111101` = 253 (clear bit 1) |
| Bit 0 (rightmost/LSB) | **Data payload** | `11111110` = 254 (clear bit 0) |
| Bit 4 (4th from right) | **Original data reference** | Used for comparison |

### Encoding Logic:

For each message bit `result[i]` and audio frame byte `frame_bytes[j]`:

```python
res = bin(frame_bytes[j])[2:].zfill(8)   # Binary representation

if res[len(res)-4] == result[i]:    # 4th bit from end matches data bit?
    frame_bytes[j] = frame_bytes[j] & 253  # Clear indicator (bit 1 = 0)
    # → Signals: "check the 4th bit for data"
else:
    frame_bytes[j] = (frame_bytes[j] & 253) | 2  # Set indicator (bit 1 = 1)
    frame_bytes[j] = (frame_bytes[j] & 254) | result[i]  # Write data to LSB
    # → Signals: "check the LSB for data"
```

**Interpretation:**
- Indicator = 0 → Data is stored in the **4th bit** (was already there).
- Indicator = 1 → Data is stored in the **LSB** (was explicitly written).

This scheme preserves the original value when possible, reducing average modification.

---

## 3.4 Embedding and Extraction Details

### Capacity:
```
Capacity = total_frames bytes / 1 (one bit per frame byte)
For a 10-second 16-bit mono WAV at 44.1kHz:
  = 44,100 × 2 × 10 = 882,000 bytes
  = 882,000 bits / 8 = 110,250 characters
```

### Message Format:
`message + '*^*^*'` — each character converted to 8 bits, stored as list of 0s and 1s.

### Decoding:
For each frame byte:
```
if bit_1 == 0:
    extracted_bit = bit_4   (data is in 4th position)
else:
    extracted_bit = bit_0   (data is in LSB)
```

Assemble bits → 8 at a time → character → check for `*^*^*` terminator.

---

## 3.5 Audio Quality Analysis

**Human Auditory Perception:**
- Human hearing is more sensitive to **frequency patterns** than absolute amplitude.
- Changing the last 1–2 bits of a 16-bit sample (value 0–65535) changes the amplitude by at most 3 units.
- Signal-to-Noise Ratio (SNR) change is approximately: `20 × log₁₀(65535/1.5) ≈ 92.8 dB` — well below audibility.
- **The modification is inaudible.**

**Detection Risk:**
- Spectrum analysis of the LSB plane can reveal unusual patterns.
- Statistical analysis of frame byte distributions can detect sequential embedding.
- No encryption is applied in this mode (in `core.py`). The API version (`api.py`) also provides no audio encryption.

---

## 3.6 File Format Preservation

```python
with wave.open(stegofile, 'wb') as fd:
    fd.setparams(song.getparams())  # ← Copies: nchannels, sampwidth, framerate,
                                    #   nframes, comptype, compname
    fd.writeframes(frame_modified)
```

The stego file is a **perfectly valid** WAV file with identical metadata. It will play in any audio player. The audio will sound identical to the original.

---