# High-Capacity and Secure Image Steganography: A Hybrid Approach

## Abstract
This project presents an advanced hybrid steganographic system that addresses the vulnerabilities of traditional Least Significant Bit (LSB) embedding algorithms. Inspired by the principles discussed in the IEEE research paper "Image Steganography: A Review of the Recent Advances" (Document ID: 9335027), this system integrates AES-256 cryptographic principles with a Pseudo-Random Number Generator (PRNG) for bit scattering. The objective is to secure the hidden payload from statistical steganalysis attacks while maintaining high visual fidelity, validated by PSNR and SSIM metrics.

## 1. Introduction
Traditional steganography methods, such as sequential LSB replacement, are notoriously vulnerable to steganalysis. An attacker equipped with Chi-square analysis tools can easily detect the presence of sequential data. Furthermore, without a cryptographic layer, extracted data is immediately visible in plaintext. 

As discussed in recent IEEE literature (9335027), modern steganography requires an intersection of data-hiding and encryption (Hybrid Steganography) alongside techniques to defeat statistical analysis. This project tackles both requirements via a modern web interface.

## 2. Proposed Methodology

### 2.1. Cryptographic Pre-Processing (AES Encryption)
Before any data is embedded into the spatial domain of the cover file, it undergoes symmetric encryption using the **Advanced Encryption Standard (AES)** in Cipher Block Chaining (CBC) mode. 
- The user provides a secret password.
- A SHA-256 hash of this password acts as the 256-bit encryption key.
- The plaintext payload is encrypted, ensuring that even if an attacker successfully extracts the payload from the image, they obtain only high-entropy ciphertext.

### 2.2. PRNG-Based Bit Scattering (Steganalysis Resistance)
Sequential embedding alters the structural statistics of an image predictably. To mitigate this:
- The system utilizes the user's password to seed a deterministic Pseudo-Random Number Generator (PRNG).
- A randomized sequence of pixel indices is generated covering the entire image footprint.
- The encrypted payload bits are scattered non-sequentially across the image following this sequence. 

### 2.3. System Architecture
The application is built on a modular Client-Server architecture:
- **Backend:** A Flask REST API (port 6868) manages the heavy computational workload: image array manipulation (via OpenCV and NumPy), encryption (PyCryptodome), and metric calculations (Scikit-Image).
- **Frontend:** A lightweight vanilla HTML/JS interface (port 3000) allowing users to intuitively encode/decode stego files and observe steganalysis metrics in real-time.

## 3. Evaluation Metrics
To validate the effectiveness and imperceptibility of the steganography, the system calculates and displays real-time quantitative metrics:

- **Peak Signal-to-Noise Ratio (PSNR):** Measures the absolute error between the cover image and the stego-image. A PSNR above 30-40 dB indicates that the distortion is imperceptible to the human eye.
- **Structural Similarity Index Measure (SSIM):** Evaluates the structural coherence between the original and modified images on a scale of 0 to 1. A value $> 0.95$ demonstrates excellent structural integrity.

## 4. Conclusion
By augmenting a classical LSB algorithm with a hybrid cryptographic layer and random scattering techniques, this implementation successfully bridges the gap between theoretical research concepts and a functional, secure application. The real-time metric visualization acts as an empirical validation tool directly aligning with the evaluation criteria standard in steganographic research papers.
