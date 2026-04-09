# 📊 Detailed Modality Reports — Steganography Project

This document contains deep technical reports for each of the four steganography modalities implemented in this project.

---


# 🌐 Report 5: Web API Layer (server.py + api.py)

## 5.1 Architecture

```
Browser (port 3000)
    ↓ HTTP multipart/form-data
Flask API (port 6868)
    ↓ Calls api.py functions
    ↓ Returns file or JSON
Browser displays results
```

## 5.2 Endpoints

### POST /encode
```
Input:  multipart/form-data
  - type: "image" | "text" | "audio"
  - text: "secret message"
  - password: "optional_key" (image only, enables advanced mode)
  - file: <cover file>

Output (basic): Stego file download
Output (advanced image): JSON {message, file_url, metrics: {psnr, ssim}}
```

### POST /decode
```
Input:  multipart/form-data
  - type: "image" | "text" | "audio"
  - password: "key_used_at_encode" (if advanced mode)
  - file: <stego file>

Output: JSON {hidden_text: "recovered message"}
```

## 5.3 Swagger Documentation

The API has **auto-generated Swagger documentation** via `flasgger`. Accessible at `http://localhost:6868/apidocs/` — provides an interactive testing interface for all endpoints.

## 5.4 CORS

```python
CORS(app)
```
Enables **Cross-Origin Resource Sharing** — allows the frontend running on port 3000 to call the API on port 6868 without browser security blocks.

---

*Generated for MiniProject — Hybrid Steganography System*
*Reference IEEE Document: 9335027 — "Image Steganography: A Review of the Recent Advances"*
