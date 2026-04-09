
# 🖼️ Report 1: Image Steganography

## 1.1 Overview

Image steganography in this project hides secret text inside digital images using the **Least Significant Bit (LSB)** technique. The core principle: changing the last bit of a pixel's color value changes the colour by at most 1 unit out of 255 — completely invisible to the human eye.

Two modes exist:
| Mode | Location | Encryption | Scattering |
|------|----------|-----------|------------|
| Basic | `core.py` `encode_img_data()` | None | Sequential |
| Advanced | `api.py` `encode_img_advanced()` | AES-256-CBC | PRNG-based |

---

## 1.2 How It Works — Basic Mode

### Step 1: Capacity Check

```
Capacity = (height × width × 3) ÷ 8 bytes
Example: 640×480 image → 640 × 480 × 3 ÷ 8 = 115,200 bytes = 112.5 KB
```

The image is treated as a 3D array: `[rows][columns][channels (R,G,B)]`.

### Step 2: Message Preparation

The secret text gets a **terminator appended**: `"Hello"` → `"Hello*^*^*"`.

The entire string is converted to a **flat binary string**:
```
"H"  → 01001000
"e"  → 01100101
"l"  → 01101100
"l"  → 01101100
"o"  → 01101111
"*"  → 00101010
"^"  → 01011110
(and so on for *^*^*)
```

### Step 3: LSB Embedding

For each pixel (R, G, B), the **last bit** of each channel is replaced with the next message bit.

**Before embedding** (pixel RGB = [200, 150, 100]):
```
R: 200 = 1100 1000  →  bit 7 (MSB) to bit 0 (LSB)
G: 150 = 1001 0110
B: 100 = 0110 0100
```

**Embedding 3 bits** (e.g., 0, 1, 1):
```
R: 1100 100[0]  (last bit replaced with secret bit 0) → R = 200
G: 1001 011[1]  (last bit replaced with secret bit 1) → G = 151
B: 0110 010[1]  (last bit replaced with secret bit 1) → B = 101
```

The visual colour change: RGB went from `(200, 150, 100)` to `(200, 151, 101)` — identical to the human eye.

### Step 4: Decoding

The decoder reads the **last bit of every R, G, B channel sequentially**. Every 8 bits → 1 character. Stops when it encounters `*^*^*`.

---

## 1.3 How It Works — Advanced Mode (AES + PRNG)

### Phase 1: AES-256-CBC Encryption

```python
key = hashlib.sha256(password.encode()).digest()  # 256-bit key from password
cipher = AES.new(key, AES.MODE_CBC)               # CBC mode with random IV
ct_bytes = cipher.encrypt(pad(plaintext, 16))     # PKCS7 padding
iv + ":" + base64(ct_bytes)                       # Combined output
```

1. Password → SHA-256 hash → 32-byte (256-bit) AES key.
2. AES encrypts the plaintext in **16-byte blocks** (CBC mode chains blocks together).
3. A **random Initialization Vector (IV)** ensures the same message encrypted twice gives different ciphertext.
4. Output format: `base64(IV) : base64(ciphertext)` — safe for embedding.

An attacker who extracts bits from the stego image gets only high-entropy ciphertext — **useless without the password**.

### Phase 2: PRNG Pixel Scattering

```python
random.seed(password)         # Password determines scatter pattern
indices = list(range(len(flat_img)))
random.shuffle(indices)       # Deterministic random order
```

Instead of embedding bits in pixels sequentially (row by row), bits are scattered **across the entire image** in a pseudo-random order determined by the password.

**Why this matters:** Sequential LSB embedding creates a detectable statistical signature. The pixel value histogram changes in a characteristic way that can be detected by Chi-square analysis. PRNG scattering destroys this pattern.

**Visual comparison:**
```
Sequential: [modified][modified][modified][ normal ][ normal ]
                ↑ Attack works here: chi-square detects clustering

Scattered:  [modified][ normal ][modified][ normal ][modified]
                ↑ Statistical signature destroyed across whole image
```

---

## 1.4 Quality Metrics

### PSNR (Peak Signal-to-Noise Ratio)

```
PSNR = 10 × log₁₀(255² / MSE)
MSE = (1/N) × Σ(pixel_original - pixel_stego)²
```

- Higher PSNR = less distortion.
- **> 40 dB**: Imperceptible change.
- **30-40 dB**: Acceptable.
- **< 30 dB**: Visible distortion.
- LSB modifications typically yield **PSNR ≈ 51-58 dB** (excellent imperceptibility).

### SSIM (Structural Similarity Index Measure)

```
SSIM = (2μ₁μ₂ + C₁)(2σ₁₂ + C₂) / (μ₁² + μ₂² + C₁)(σ₁² + σ₂² + C₂)
```

- Range: 0 to 1. A value of 1 means **identical** images.
- Measures **luminance**, **contrast**, and **structural** similarity.
- LSB steganography typically yields **SSIM > 0.9999** — practically perfect.

---

## 1.5 Attack Resistance Analysis

| Attack Type | Basic Mode | Advanced Mode |
|-------------|-----------|---------------|
| Visual Inspection | ✅ Resistant | ✅ Resistant |
| LSB Statistical Analysis | ❌ Vulnerable | ✅ Resistant (PRNG scattering) |
| Chi-Square Test | ❌ Vulnerable | ✅ Resistant |
| Payload Extraction (without key) | ❌ Plaintext exposed | ✅ AES ciphertext only |
| Brute Force on Password | N/A | Difficult (SHA-256 + AES-256) |

---