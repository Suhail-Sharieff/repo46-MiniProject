

# 🎬 Report 4: Video Steganography

## 4.1 Overview

Video steganography is the most complex of the four modalities. A video is a **sequence of image frames** played at a specific frame rate. The project hides secret data in the pixel LSBs of **a single chosen frame** within the video.

**Key insight:** A standard video has 25 frames per second (25 FPS). Embedding in just **one frame** out of thousands is extremely difficult to detect — an attacker would have to analyze every single frame individually.

---

## 4.2 Video Codec and Format

```python
fourcc = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('stego_video.mp4', fourcc, 25.0, size)
```

- **XVID codec**: MPEG-4 Part 2 video compression.
- **25 FPS**: Standard frame rate.
- **Output**: `stego_video.mp4` — standard MP4 container.

**Important caveat:** XVID is a **lossy codec**. Re-encoding the video with XVID may introduce compression artifacts that can corrupt the LSB modifications in the stego frame. For highest reliability, lossless codecs (like HUFFYUV or storing as uncompressed AVI) would be preferred.

---

## 4.3 Frame Selection and Embedding

### Frame Count:
```python
while(cap.isOpened()):
    ret, frame = cap.read()
    if ret == False:
        break
    max_frame += 1
```
Reads through entire video to count frames. User selects a target frame number.

### Selective Frame Modification:
```python
if frame_number == n:    
    change_frame_with = embed(frame)    # Only modify this frame!
    frame = change_frame_with
out.write(frame)                        # Write all frames (modified or not)
```

99.99% of frames are untouched. Only one carries the secret.

---

## 4.4 RC4 Encryption for Video

Unlike basic image or audio steganography, video steganography applies **RC4 encryption**:

```
Plaintext → RC4(key) → Ciphertext → Append *^*^* → Binary → LSB embed
```

**RC4 Details:**
- **KSA** (Key Scheduling Algorithm): Initializes a 256-element state array `S` by scrambling with the key.
- **PRGA** (Pseudo-Random Generation Algorithm): Generates a keystream byte `K = S[(S[i]+S[j]) % 256]`.
- **XOR**: `ciphertext[i] = plaintext[i] XOR keystream[i]`.

**Security property:** If the key is the same, KSA+PRGA generates the same keystream — so decryption is done by XOR-ing ciphertext with the same keystream: `XOR(XOR(P, K), K) = P`.

**Weakness of RC4:** RC4 has known cryptographic vulnerabilities (key biases in early keystream bytes, identical key reuse attacks). However, for this project's scope, it provides adequate obfuscation. AES-256 (in `api.py`'s advanced image mode) is the recommended modern alternative.

## 4.5 Embedding Capacity in a Single Frame

For the provided cover video (assumed 640×480):
```
Capacity per frame = 640 × 480 × 3 ÷ 8 = 115,200 bytes = 112 KB
```

After RC4 encryption, the ciphertext length equals the plaintext length (stream cipher). So capacity is effectively the same minus the message overhead.

---

## 4.6 Known Bug: Premature Return in `embed()`

```python
for i in frame:              # Loop over rows
    for pixel in i:          # Loop over pixels in row
        ...                  # Modify pixel LSBs
    return frame             # ← BUG: This is inside the OUTER for loop!
```

The `return frame` statement is indented under the outer `for i in frame:` loop, not after it. This causes the function to return after processing **only the first row** of the frame. In practice this means:
- Only `width × 3` bits (e.g., 640 × 3 = 1920 bits = 240 characters) can be embedded before the function returns.
- The remaining rows of the frame are unmodified.

This is a residual indentation bug from Jupyter Notebook conversion.

---

## 4.7 Video Steganography Attack Resistance

| Attack Vector | Likelihood | Resistance |
|--------------|-----------|-----------|
| Casual viewing | Low | High — video looks identical |
| Frame-by-frame pixel comparison | Medium | Low — requires original video |
| Statistical LSB analysis (all frames) | Low | High — only 1 frame modified |
| RC4 key brute force | Medium-High | Moderate — RC4 has weaknesses |
| MPEG-4 compression artifacts | Present | Re-encoding destroys LSBs! |

---

## 4.8 Comparison of All Four Modalities

| Feature | Image | Text | Audio | Video |
|---------|-------|------|-------|-------|
| **Carrier** | JPG/PNG pixels | Text file | WAV samples | MP4 frames |
| **Technique** | LSB | ZWC | 2-bit indicator LSB | Frame LSB |
| **Encryption** | None (basic) / AES-256 (advanced) | XOR+shift | None | RC4 |
| **Capacity** | Large (kBs-MBs) | Moderate (limited by word count) | Large (kBs-MBs) | Large per frame |
| **Detection Risk** | Moderate (chi-square) | Low-Moderate | Moderate | Low |
| **Perceptibility** | None (≈0) | None | None | None |
| **File Size Change** | Minimal or identical | Slight increase | Identical | Minimal |
| **Reversibility** | Perfect | Perfect | Perfect | Lossy (XVID) |

---

---