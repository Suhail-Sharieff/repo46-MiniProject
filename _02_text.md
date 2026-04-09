

# 📝 Report 2: Text Steganography

## 2.1 Overview

Text steganography is fundamentally different from image steganography — there are **no pixel values to modify**. Instead, it exploits the Unicode standard's existence of **invisible characters** that can be embedded within ordinary text without being visible.

This is a form of **linguistic steganography** using structural/format-level modifications.

---

## 2.2 Zero-Width Character (ZWC) Approach

### The Invisible Characters

| Unicode | Code Point | Name | Visible? | Binary |
|---------|-----------|------|---------|--------|
| `\u200C` | U+200C | Zero Width Non-Joiner | No | `00` |
| `\u202C` | U+202C | Pop Directional Formatting | No | `01` |
| `\u202D` | U+202D | Left-to-Right Override | No | `11` |
| `\u200E` | U+200E | Left-to-Right Mark | No | `10` |

Each invisible character carries **2 bits** of information. Together, 6 invisible characters carry **12 bits** per word — enough for one encoded character.

---

## 2.3 Character Encoding Scheme

The project uses a **custom binary encoding** with XOR obfuscation:

### For ASCII 32–64 (symbols and digits: space, !, ", #, digits, @, etc.):

```
Step 1: t = ASCII value of character
Step 2: t1 = t + 48          (shift up)
Step 3: t2 = t1 XOR 170      (XOR with 10101010)
Step 4: res = 8-bit binary of t2
Step 5: encode = "0011" + res (12 bits total)
```

**Example: Encoding digit '5' (ASCII 53):**
```
t  = 53
t1 = 53 + 48 = 101
t2 = 101 XOR 170 = 203  (01100101 XOR 10101010 = 11001111)
res = "11001111"
encode = "0011" + "11001111" = "001111001111"
```

### For ASCII 65+ (letters and other characters):

```
Step 1: t = ASCII value
Step 2: t1 = t - 48          (shift down)
Step 3: t2 = t1 XOR 170
Step 4: res = 8-bit binary
Step 5: encode = "0110" + res
```

**The 4-bit flag** (`0011` or `0110`) tells the decoder which formula to reverse.

---

## 2.4 Embedding Process

**Cover text word count determines capacity:**
```
Capacity = floor(word_count / 6) characters
(Each character uses 6 pairs of ZWC characters, one per word)
```

**Word structure after embedding:**
```
Original word: "the"
After embedding: "the" + ZWC₁ + ZWC₂ + ZWC₃ + ZWC₄ + ZWC₅ + ZWC₆
Displayed as:   "the" (looks identical — ZWC characters are hidden!)
```

**End-of-message signal:** After all characters are encoded, a **12-bit terminator** `111111111111` maps to `ZWC₄ZWC₄ZWC₄ZWC₄ZWC₄ZWC₄` — the decoder stops when it sees this pattern.

---

## 2.5 Decoding Process

```
For each word in stego file:
    1. Extract any ZWC characters
    2. Map each ZWC → 2-bit binary
    3. Form 12-bit chunk
    4. Check if it's the terminator (111111111111)
    5. If not: read 4-bit flag + 8-bit value
    6. Reverse the XOR and shift operations
    7. chr() to recover the character
```

**Decoding example:**
If we find `ZWC₄ZWC₃ZWC₁ZWC₂ZWC₃ZWC₁`:
```
Map: 11 11 00 01 11 00 = "111100011100"
Flag: first 4 bits = "1111" → not a valid flag!
(In practice flags are 0011 or 0110 only)
```

---

## 2.6 Security Analysis

**Strengths:**
- Visually undetectable — the text looks perfectly normal in any text editor or document viewer.
- XOR with 170 adds a layer of obfuscation (not true encryption, but not plaintext either).
- The encoded file is a valid UTF-8 text file — passes file format checks.

**Weaknesses:**
- Advanced Unicode tools can detect ZWC characters.
- No strong encryption — XOR with a fixed value (170) is reversible by anyone who knows the scheme.
- Known cover text comparison would reveal differences.
- File size slightly increases (invisible characters still take bytes).

**Statistical signature:** A stego text file will have a noticeably higher byte count than the visible character count, which could alert an automated steganalysis tool.

---
