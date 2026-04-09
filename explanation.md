# 📖 explanation.md — Line-by-Line Deep Dive of `core.py`

This file explains **every single line** of `core.py` in plain English so anyone — even with zero prior programming knowledge — can understand what is happening and *why*.

---

## 🔰 What is core.py?

`core.py` is the **command-line engine** of this steganography project. It contains all the algorithms for hiding secret messages inside images, text files, audio files, and video files — and then extracting them back. Think of it like a vault builder: it hides your message inside innocent-looking files.

---

## 📦 Lines 1–11 — Shebang, Encoding Declaration & Imports

```python
#!/usr/bin/env python
# coding: utf-8
```

- **Line 1 (`#!/usr/bin/env python`):** The "shebang" line. On Linux/Mac, this tells the operating system: "Run this file with Python." On Windows it does nothing but is kept for cross-platform compatibility.
- **Line 2 (`# coding: utf-8`):** Tells Python that this file uses UTF-8 character encoding. This is critical because we later use **Zero Width Characters** (special invisible Unicode characters) which need UTF-8 to be stored correctly.

```python
import numpy as np
import pandas as pand
import os
import cv2
from matplotlib import pyplot as plt
```

- **`import numpy as np`:** Imports NumPy — a library for working with arrays of numbers (like pixel values in an image). We give it the alias `np` to type less.
- **`import pandas as pand`:** Imports Pandas — a data analysis library. Although imported, it is not directly used in the visible code (legacy/notebook artifact).
- **`import os`:** Imports Python's built-in Operating System library so we can interact with files and folders.
- **`import cv2`:** Imports **OpenCV** (Open Computer Vision) — the main library used to **read, write, and manipulate images and videos**. Every image operation goes through this.
- **`from matplotlib import pyplot as plt`:** Imports Matplotlib's plotting library (also a notebook artifact — used during development for visualizing images, not needed in production).

---

## 🔡 TEXT STEGANOGRAPHY — Lines 17–164

### Lines 17–68 — `txt_encode(text)` — The Core Text Encoding Algorithm

```python
def txt_encode(text):
```
**Defines a function** called `txt_encode`. A function is a reusable block of code. It takes `text` (the secret message to hide) as input.

```python
    l=len(text)
    i=0
    add=''
```
- `l = len(text)`: Counts how many characters are in the secret message and stores the count in variable `l`.
- `i = 0`: A loop counter, starts at zero.
- `add = ''`: Creates an empty string `add` that will hold the growing **binary representation** of the secret message.

---

#### The Encoding Loop (Lines 21–33)

```python
    while i < l:
        t = ord(text[i])
```
- `while i < l:` — Keep looping for each character in the text.
- `t = ord(text[i])` — Gets the **ASCII integer code** of the current character. For example, `ord('A')` = 65.

```python
        if(t >= 32 and t <= 64):
```
Checks if the character is a **symbol or digit** (ASCII 32–64 covers space, `!`, `"`, `#`, `$`, `%`, digits 0–9, `:`, `;`, `<`, `=`, `>`, `?`, `@`).

```python
            t1 = t + 48
            t2 = t1 ^ 170       # 170: 10101010
            res = bin(t2)[2:].zfill(8)
            add += "0011" + res
```
- `t1 = t + 48`: Shifts the ASCII value up by 48 (obfuscation step 1).
- `t2 = t1 ^ 170`: XOR the shifted value with `170` (binary `10101010`). XOR is a bitwise operation that flips specific bits — this is a lightweight **cipher** step.
- `res = bin(t2)[2:].zfill(8)`: Converts `t2` to 8-bit binary. `bin()` gives e.g. `'0b10110101'`, `[2:]` strips the `0b` prefix, `.zfill(8)` pads with zeros to ensure exactly 8 digits.
- `add += "0011" + res`: Prepends the **flag `"0011"`** to the binary. This flag tells the decoder that the character came from the ASCII 32–64 range.

```python
        else:
            t1 = t - 48
            t2 = t1 ^ 170
            res = bin(t2)[2:].zfill(8)
            add += "0110" + res
```
If the character is a **letter or other character** (ASCII 65+):
- `t1 = t - 48`: Shifts ASCII down by 48.
- XOR and binary conversion same as above.
- `add += "0110" + res`: Prepends **flag `"0110"`** — tells decoder this was an uppercase/lowercase letter.

So each character becomes **12 bits total**: 4-bit flag + 8-bit encoded binary.

```python
        i += 1
```
Move to the next character.

```python
    res1 = add + "111111111111"
```
After all characters are encoded, **append a 12-bit terminator** (`111111111111`) — this is the **end-of-message signal** so the decoder knows when to stop reading.

```python
    print("The string after binary conversion applying all the transformation :- " + (res1))   
    length = len(res1)
    print("Length of binary after conversion:- ", length)
```
Print the encoded binary string and its length (debug/user feedback).

---

#### The Zero-Width Character Dictionary (Line 40)

```python
    HM_SK = ""
    ZWC = {"00": u'\u200C', "01": u'\u202C', "11": u'\u202D', "10": u'\u200E'}
```
This is the **stealth dictionary** — the heart of text steganography!

| Binary Code | Unicode Character | Description |
|------------|-------------------|-------------|
| `"00"` | `\u200C` | Zero Width Non-Joiner — completely invisible in any text editor |
| `"01"` | `\u202C` | Pop Directional Formatting — invisible |
| `"11"` | `\u202D` | Left-to-Right Override — invisible |
| `"10"` | `\u200E` | Left-to-Right Mark — invisible |

These characters **cannot be seen** but are stored in the file. Each pair of binary digits gets mapped to one of these invisible characters.

---

#### Opening Files and Embedding (Lines 41–67)

```python
    file1 = open("Sample_cover_files/cover_text.txt", "r+")
    nameoffile = input("\nEnter the name of the Stego file after Encoding(with extension):- ")
    file3 = open(nameoffile, "w+", encoding="utf-8")
```
- Opens the **cover text file** (ordinary innocent text).
- Asks the user for a name for the **output stego file** (the text that will secretly contain the hidden message).
- Opens the output file in write mode with UTF-8 encoding (essential for zero-width characters).

```python
    word = []
    for line in file1: 
        word += line.split()
```
Reads all words from the cover text into a list called `word`. For example `"Hello World"` becomes `['Hello', 'World']`.

```python
    i = 0
    while(i < len(res1)):  
        s = word[int(i/12)]
```
- Loop processes the binary string `res1` in **12-bit chunks** (because each character = 12 bits).
- `int(i/12)` is the word index — every 12 bits we advance to the next word.

```python
        j = 0
        x = ""
        HM_SK = ""
        while(j < 12):
            x = res1[j+i] + res1[i+j+1]
            HM_SK += ZWC[x]
            j += 2
```
- Inner loop processes 2 bits at a time.
- Takes two consecutive bits from `res1`, looks them up in `ZWC` dictionary, and builds `HM_SK` — the **invisible character string** to attach to this word.

```python
        s1 = s + HM_SK
        file3.write(s1)
        file3.write(" ")
        i += 12
```
- Attaches the invisible characters to the visible word: `"Hello\u200C\u202C\u202D..."`.
- Writes to the stego file.
- The word looks completely normal to a human reading it!

```python
    t = int(len(res1)/12)     
    while t < len(word): 
        file3.write(word[t])
        file3.write(" ")
        t += 1
```
Writes any **remaining words** from the cover text that weren't used to carry data (the cover text is usually much longer than the message).

```python
    file3.close()  
    file1.close()
    print("\nStego file has successfully generated")
```
Close files and confirm success.

---

### Lines 74–90 — `encode_txt_data()` — User Input Wrapper for Text Encoding

```python
def encode_txt_data():
    count2 = 0
    file1 = open("Sample_cover_files/cover_text.txt", "r")
    for line in file1: 
        for word in line.split():
            count2 = count2 + 1
    file1.close()       
    bt = int(count2)
    print("Maximum number of words that can be inserted :- ", int(bt/6))
```
Counts total words in the cover file. Each character needs 12 bits = 6 pairs of 2 bits = 6 invisible characters, and each invisible character lives on a word. So the capacity is `total_words / 6`.

```python
    text1 = input("\nEnter data to be encoded:- ")
    l = len(text1)
    if(l <= bt):
        print("\nInputed message can be hidden in the cover file\n")
        txt_encode(text1)
    else:
        print("\nString is too big please reduce string size")
        encode_txt_data()
```
Gets secret text from user. If it fits, calls `txt_encode`. If not, warns user and recursively asks again (not ideal but functional).

---

### Lines 96–98 — `BinaryToDecimal(binary)` — Helper Function

```python
def BinaryToDecimal(binary):
    string = int(binary, 2)
    return string
```
Converts a binary string like `"10110101"` to its decimal integer equivalent (181). `int(binary, 2)` means "interpret this string in base 2."

---

### Lines 104–143 — `decode_txt_data()` — Text Decoding

```python
def decode_txt_data():
    ZWC_reverse = {u'\u200C': "00", u'\u202C': "01", u'\u202D': "11", u'\u200E': "10"}
```
The **reverse dictionary** — maps invisible characters back to their 2-bit binary codes.

```python
    stego = input("\nPlease enter the stego file name(with extension) to decode the message:- ")
    file4 = open(stego, "r", encoding="utf-8")
    temp = ''
    for line in file4: 
        for words in line.split():
            T1 = words
            binary_extract = ""
            for letter in T1:
                if(letter in ZWC_reverse):
                    binary_extract += ZWC_reverse[letter]
            if binary_extract == "111111111111":
                break
            else:
                temp += binary_extract
```
- Opens the stego file.
- For each word, scans every character.
- If the character is an invisible ZWC — maps it back to 2 bits and appends to `binary_extract`.
- If a word produces the **terminator** `"111111111111"` → stop decoding.
- Otherwise append the extracted bits to `temp`.

```python
    i = 0; a = 0; b = 4; c = 4; d = 12; final = ''
    while i < len(temp):
        t3 = temp[a:b]     # bits 0-3: the 4-bit flag
        a += 12; b += 12; i += 12
        t4 = temp[c:d]     # bits 4-11: the 8-bit encoded value
        c += 12; d += 12
        if(t3 == '0110'):
            decimal_data = BinaryToDecimal(t4)
            final += chr((decimal_data ^ 170) + 48)
        elif(t3 == '0011'):
            decimal_data = BinaryToDecimal(t4)
            final += chr((decimal_data ^ 170) - 48)
    print("\nMessage after decoding from the stego file:- ", final)
```
Decodes 12 bits at a time:
- **Reads 4-bit flag** (`t3 = temp[a:b]`) to know which type of character.
- **Reads 8-bit value** (`t4 = temp[c:d]`).
- **Reverses the encoding**: XOR with 170, then undo the `+48` or `-48` shift.
- `chr()` converts the integer back to a character.
- Result appended to `final`.

---

### Lines 149–164 — `txt_steg()` — Text Steganography Menu

```python
def txt_steg():
    while True:
        print("\n\t\tTEXT STEGANOGRAPHY OPERATIONS") 
        print("1. Encode the Text message")  
        print("2. Decode the Text message")  
        print("3. Exit")  
        choice1 = int(input("Enter the Choice:"))   
        if choice1 == 1:
            encode_txt_data()
        elif choice1 == 2:
            decrypted = decode_txt_data() 
        elif choice1 == 3:
            break
        else:
            print("Incorrect Choice")
        print("\n")
```
A simple **menu loop** for text steganography. Keeps showing options until user picks "Exit."

---

## 🖼️ IMAGE STEGANOGRAPHY — Lines 170–272

### Lines 170–183 — `msgtobinary(msg)` — Universal Binary Converter

```python
def msgtobinary(msg):
    if type(msg) == str:
        result = ''.join([format(ord(i), "08b") for i in msg])
```
If input is a **string**: converts each character to its 8-bit binary representation and joins them. E.g., `"A"` → `"01000001"`.

```python
    elif type(msg) == bytes or type(msg) == np.ndarray:
        result = [format(i, "08b") for i in msg]
```
If input is **bytes or NumPy array** (like an image pixel): returns a **list** of 8-bit binary strings, one per byte.

```python
    elif type(msg) == int or type(msg) == np.uint8:
        result = format(msg, "08b")
```
If input is a **single integer** (like one pixel channel value 0–255): returns a single 8-bit binary string.

```python
    else:
        raise TypeError("Input type is not supported in this function")
    return result
```
If none of the above types: raises an error. Otherwise returns the result.

---

### Lines 189–229 — `encode_img_data(img)` — LSB Image Encoding

```python
def encode_img_data(img):
    data = input("\nEnter the data to be Encoded in Image:")    
    if (len(data) == 0): 
        raise ValueError('Data entered to be encoded is empty')
```
Gets the secret message. **Raises an error** if it's empty.

```python
    nameoffile = input("\nEnter the name of the New Image (Stego Image) after Encoding(with extension):")
    no_of_bytes = (img.shape[0] * img.shape[1] * 3) // 8
    print("\t\nMaximum bytes to encode in Image:", no_of_bytes)
```
- `img.shape[0]` = image height (rows), `img.shape[1]` = image width (columns).
- `* 3` = 3 channels (Red, Green, Blue).
- `// 8` = 8 bits per byte. This tells us **how many bytes of secret data** can fit.
- E.g., a 100×100 pixel image → `100×100×3÷8 = 3750 bytes`.

```python
    if(len(data) > no_of_bytes):
        raise ValueError("Insufficient bytes Error, Need Bigger Image or give Less Data !!")
```
Capacity check — message must fit.

```python
    data += '*^*^*'    
```
Appends a **terminator** `*^*^*` to know where the message ends during decoding.

```python
    binary_data = msgtobinary(data)
    length_data = len(binary_data)
    index_data = 0
```
- Converts entire message+terminator to binary string.
- `length_data` = total bits to embed.
- `index_data` = current position in binary string.

---

#### The Pixel Loop — LSB Replacement (Lines 214–228)

```python
    for i in img:
        for pixel in i:
            r, g, b = msgtobinary(pixel)
```
- Outer loop iterates over **rows** of the image (`i` = one row).
- Inner loop iterates over **pixels** in that row.
- `msgtobinary(pixel)` unpacks each pixel's R, G, B values into 8-bit binary strings. E.g., pixel `[123, 45, 200]` → `r="01111011"`, `g="00101101"`, `b="11001000"`.

```python
            if index_data < length_data:
                pixel[0] = int(r[:-1] + binary_data[index_data], 2) 
                index_data += 1
```
- **The LSB technique**: `r[:-1]` takes the first 7 bits of the Red channel. `binary_data[index_data]` is the secret data bit.
- They are **joined** to form a new 8-bit number where only the **last bit (Least Significant Bit)** is changed.
- `int(..., 2)` converts binary back to integer.
- This changes the Red value by **at most 1** (e.g., 123 → 122 or 124) — imperceptible to the human eye!
- Same process for Green (`pixel[1]`) and Blue (`pixel[2]`) channels.

```python
            if index_data >= length_data:
                break
    cv2.imwrite(nameoffile, img)
    print("\nEncoded the data successfully in the Image...")
```
When all bits are embedded, stops iterating and **saves** the modified image with `cv2.imwrite`.

---

### Lines 235–249 — `decode_img_data(img)` — Image Decoding / Extraction

```python
def decode_img_data(img):
    data_binary = ""
    for i in img:
        for pixel in i:
            r, g, b = msgtobinary(pixel) 
            data_binary += r[-1]  
            data_binary += g[-1]  
            data_binary += b[-1]  
```
- Reads the **last bit** (`[-1]`) of each R, G, B channel of every pixel.
- Builds `data_binary` — the reconstructed bit string.

```python
            total_bytes = [data_binary[i: i+8] for i in range(0, len(data_binary), 8)]
            decoded_data = ""
            for byte in total_bytes:
                decoded_data += chr(int(byte, 2))
                if decoded_data[-5:] == "*^*^*": 
                    print("\n\nThe Encoded data which was hidden in the Image was :-- ", decoded_data[:-5])
                    return 
```
- Every 8 bits → 1 character (`chr(int(byte, 2))`).
- After each character, checks if the last 5 characters are the terminator `*^*^*`.
- If found → prints the recovered message (without the terminator) and **returns**.

---

### Lines 255–272 — `img_steg()` — Image Steganography Menu

```python
def img_steg():
    while True:
        ...
        if choice1 == 1:
            image = cv2.imread("Sample_cover_files/cover_image.jpg")
            encode_img_data(image)
        elif choice1 == 2:
            image1 = cv2.imread(input("Enter the Image you need to Decode:"))
            decode_img_data(image1)
```
- For **encoding**: loads the pre-provided JPG cover image using OpenCV.
- For **decoding**: asks user for their stego image path and loads it.

---

## 🔊 AUDIO STEGANOGRAPHY — Lines 278–376

### Lines 278–320 — `encode_aud_data()` — Audio Encoding

```python
def encode_aud_data():
    import wave
```
Imports Python's built-in `wave` module for reading/writing `.wav` audio files. WAV is used because it's **uncompressed** — MP3 compression would destroy our hidden bits!

```python
    nameoffile = input("Enter name of the file (with extension) :- ")
    song = wave.open(nameoffile, mode='rb')
```
Opens the cover WAV file in **read-binary** mode.

```python
    nframes = song.getnframes()
    frames = song.readframes(nframes)
    frame_list = list(frames)
    frame_bytes = bytearray(frame_list)
```
- `getnframes()`: gets total number of audio frames (samples).
- `readframes(nframes)`: reads ALL frames as raw bytes.
- `bytearray(...)`: converts to a **mutable** byte array so we can edit individual bytes.

```python
    data = input("\nEnter the secret message :- ")
    res = ''.join(format(i, '08b') for i in bytearray(data, encoding='utf-8'))     
    print("The string after binary conversion :- " + (res))
```
Converts the secret message to binary using UTF-8 encoding. Each character → 8 bits.

```python
    data = data + '*^*^*'
    result = []
    for c in data:
        bits = bin(ord(c))[2:].zfill(8)
        result.extend([int(b) for b in bits])
```
Appends terminator, then builds `result` — a **list of individual 0s and 1s** (integers) for the message.

---

#### The Audio LSB Embedding (Lines 303–311)

```python
    j = 0
    for i in range(0, len(result), 1): 
        res = bin(frame_bytes[j])[2:].zfill(8)
        if res[len(res)-4] == result[i]:
            frame_bytes[j] = (frame_bytes[j] & 253)      # 253: 11111101
        else:
            frame_bytes[j] = (frame_bytes[j] & 253) | 2
            frame_bytes[j] = (frame_bytes[j] & 254) | result[i]
        j = j + 1
```
This is more sophisticated than simple LSB — it uses **two specific bit positions**:
- `res[len(res)-4]` = the **4th bit from the end** (bit position 2) — used as indicator.
- Bit manipulation with masks:
  - `253` = `11111101` → clears bit 1 (2nd from right).
  - `254` = `11111110` → clears bit 0 (last bit — the LSB).
  - If the indicator bit already matches the data bit → only clears bit 1 (marks "found").
  - Otherwise → sets both: bit 1 high (marks "needs last bit") and writes data bit to LSB.
- `j` increments: **one audio frame byte per message bit**.

```python
    frame_modified = bytes(frame_bytes)
    stegofile = input("\nEnter name of the stego file (with extension) :- ")
    with wave.open(stegofile, 'wb') as fd:
        fd.setparams(song.getparams())
        fd.writeframes(frame_modified)
    print("\nEncoded the data successfully in the audio file.")    
    song.close()
```
- Converts modified byte array back to bytes.
- Opens new WAV file, **copies all original audio parameters** (sample rate, channels, bit depth etc.) so it sounds identical to the original.
- Writes modified frames and closes files.

---

### Lines 326–355 — `decode_aud_data()` — Audio Decoding

```python
def decode_aud_data():
    import wave
    ...
    extracted = ""
    p = 0
    for i in range(len(frame_bytes)):
        if(p == 1):
            break
        res = bin(frame_bytes[i])[2:].zfill(8)
        if res[len(res)-2] == 0:      # ← checks bit position 1 (the indicator)
            extracted += res[len(res)-4]  # ← 4th from end was the indicator bit
        else:
            extracted += res[len(res)-1]  # ← LSB holds the data
```
Reads each frame byte. Checks the **indicator bit (position 1)**:
- If bit 1 is `0` → the 4th-from-end bit holds the original data.
- If bit 1 is `1` → the LSB holds the data.

```python
        all_bytes = [extracted[i: i+8] for i in range(0, len(extracted), 8)]
        decoded_data = ""
        for byte in all_bytes:
            decoded_data += chr(int(byte, 2))
            if decoded_data[-5:] == "*^*^*":
                print("The Encoded data was :--", decoded_data[:-5])
                p = 1
                break
```
Assembles extracted bits into bytes → characters, checks for `*^*^*` terminator. When found, prints message and sets `p=1` to break outer loop too.

---

### Lines 361–376 — `aud_steg()` — Audio Steganography Menu

Same menu pattern as text/image.

---

## 🔐 RC4 ENCRYPTION — Lines 382–453

### Lines 382–389 — `KSA(key)` — Key Scheduling Algorithm

```python
def KSA(key):
    key_length = len(key)
    S = list(range(256)) 
    j = 0
    for i in range(256):
        j = (j + S[i] + key[i % key_length]) % 256
        S[i], S[j] = S[j], S[i]
    return S
```
This is the **Key Scheduling Algorithm** of the **RC4 stream cipher**.

- `S = list(range(256))`: Creates a list `[0, 1, 2, ..., 255]` — the initial "state array."
- **Loop 256 times**: Scrambles `S` using the key. Each iteration:
  - Computes new `j` based on current `S[i]` + the key byte at position `i mod key_length`.
  - **Swaps** `S[i]` and `S[j]` — this scrambles the array based on the key.
- Returns the fully scrambled `S` array — the **initialized cipher state**.

### Lines 395–406 — `PRGA(S, n)` — Pseudo-Random Generation Algorithm

```python
def PRGA(S, n):
    i = 0
    j = 0
    key = []
    while n > 0:
        n = n - 1
        i = (i + 1) % 256
        j = (j + S[i]) % 256
        S[i], S[j] = S[j], S[i]
        K = S[(S[i] + S[j]) % 256]
        key.append(K)
    return key
```
Generates `n` pseudo-random bytes from the scrambled `S` array:
- Keeps updating positions `i` and `j`.
- Swaps `S[i]` and `S[j]` each iteration.
- Takes `K = S[(S[i]+S[j]) % 256]` — the keystream byte.
- `key.append(K)` → builds the keystream list.

### Lines 412–413 — `preparing_key_array(s)` — Key Preprocessor

```python
def preparing_key_array(s):
    return [ord(c) for c in s]
```
Converts a password string like `"myKey"` into a list of integers `[109, 121, 75, 101, 121]` (ASCII codes). RC4 works with integers, not strings.

### Lines 419–433 — `encryption(plaintext)` — RC4 Encrypt

```python
def encryption(plaintext):
    print("Enter the key : ")
    key = input()
    key = preparing_key_array(key)
    S = KSA(key)
    keystream = np.array(PRGA(S, len(plaintext)))
    plaintext = np.array([ord(i) for i in plaintext])
    cipher = keystream ^ plaintext
    ctext = ''
    for c in cipher:
        ctext = ctext + chr(c)
    return ctext
```
- Gets key from user.
- Runs KSA to initialize state array `S`.
- Runs PRGA to generate a keystream of same length as plaintext.
- **XOR** keystream with plaintext bytes — this produces the ciphertext.
- Converts each XOR'd integer back to a character.

### Lines 439–453 — `decryption(ciphertext)` — RC4 Decrypt

**Identical code** to `encryption()` — RC4 is **symmetric**: applying the same keystream XOR twice recovers the original! `XOR(XOR(plaintext, ks), ks) = plaintext`.

---

## 🎥 VIDEO STEGANOGRAPHY — Lines 459–596

### Lines 459–487 — `embed(frame)` — Embed Message in Single Video Frame

```python
def embed(frame):
    data = input("\nEnter the data to be Encoded in Video :") 
    data = encryption(data)
    print("The encrypted data is : ", data)
```
Gets the secret message → **encrypts it using RC4** before embedding. This is more secure than image steganography (which had no encryption in core.py's basic mode).

```python
    if (len(data) == 0): 
        raise ValueError('Data entered to be encoded is empty')
    data += '*^*^*'
    binary_data = msgtobinary(data)
    length_data = len(binary_data)
    index_data = 0
    for i in frame:
        for pixel in i:
            r, g, b = msgtobinary(pixel)
            if index_data < length_data:
                pixel[0] = int(r[:-1] + binary_data[index_data], 2) 
                index_data += 1
            ...
        return frame
```
Works identically to image LSB embedding — modifies R, G, B LSBs but now on a **single video frame**. Note: `return frame` is **inside the outer for loop** (indentation bug) — it returns after the first row of pixels.

### Lines 493–511 — `extract(frame)` — Extract from Video Frame

Same as `decode_img_data` but calls `decryption(final_decoded_msg)` to **decrypt the RC4 ciphertext** after extraction.

### Lines 517–549 — `encode_vid_data()` — Video Encoding Orchestrator

```python
def encode_vid_data():
    cap = cv2.VideoCapture("Sample_cover_files/cover_video.mp4")
    vidcap = cv2.VideoCapture("Sample_cover_files/cover_video.mp4")    
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
```
- Opens the cover video **twice** (one for counting frames, one for processing) using OpenCV.
- `fourcc` = **four-character code** for video codec. `'XVID'` is MPEG-4 Part 2 — a widely supported compressed video format.

```python
    frame_width = int(vidcap.get(3))
    frame_height = int(vidcap.get(4))
    size = (frame_width, frame_height)
    out = cv2.VideoWriter('stego_video.mp4', fourcc, 25.0, size)
```
Gets video dimensions and creates an **output video writer** at 25 FPS with same dimensions.

```python
    max_frame = 0
    while(cap.isOpened()):
        ret, frame = cap.read()
        if ret == False:
            break
        max_frame += 1
    cap.release()
    print("Total number of Frame in selected Video:", max_frame)
```
Counts total frames by reading through the whole video. `cap.read()` returns `(True, frame)` or `(False, None)` when it ends.

```python
    n = int(input())
    frame_number = 0
    while(vidcap.isOpened()):
        frame_number += 1
        ret, frame = vidcap.read()
        if ret == False:
            break
        if frame_number == n:    
            change_frame_with = embed(frame)
            frame_ = change_frame_with
            frame = change_frame_with
        out.write(frame)
```
Goes through video frame by frame:
- If current frame number = user's chosen frame → **embed the message** in that frame.
- Write every frame (modified or not) to the output video.

The stego video is identical to the original, except ONE frame has the hidden message in its pixel LSBs.

### Lines 555–575 — `decode_vid_data(frame_)` — Video Decoding

Similar to encoding but in reverse — re-reads `stego_video.mp4`, asks for frame number, extracts from that specific frame.

---

## 🧭 MAIN MENU — Lines 602–631

### Lines 602–624 — `main()` — Application Entry Point

```python
def main():
    print("\t\t      STEGANOGRAPHY")   
    while True:  
        print("\n\t\t\tMAIN MENU\n")  
        print("1. IMAGE STEGANOGRAPHY {Hiding Text in Image cover file}")  
        print("2. TEXT STEGANOGRAPHY {Hiding Text in Text cover file}")  
        print("3. AUDIO STEGANOGRAPHY {Hiding Text in Audio cover file}")
        print("4. VIDEO STEGANOGRAPHY {Hiding Text in Video cover file}")
        print("5. Exit\n")  
        choice1 = int(input("Enter the Choice: "))   
        if choice1 == 1: 
            img_steg()
        elif choice1 == 2:
            txt_steg()
        elif choice1 == 3:
            aud_steg()
        elif choice1 == 4:
            vid_steg()
        elif choice1 == 5:
            break
        else:
            print("Incorrect Choice")
        print("\n\n")
```
The **top-level menu**. Keeps showing until user selects "Exit." Routes user to the appropriate steganography module.

### Lines 630–631 — Python Entry Guard

```python
if __name__ == "__main__":
    main()
```
**Critical Python pattern**: `__name__` is a special variable. When you **run** `python core.py`, Python sets `__name__ = "__main__"`, so `main()` executes. When another file **imports** `core.py`, `__name__ = "core"` and `main()` does NOT run automatically. This keeps the file safe to import.

---

## 🗺️ Summary: How All Functions Connect

```
main()
├── img_steg()
│   ├── encode_img_data(img)   → msgtobinary() → LSB pixel modification → cv2.imwrite
│   └── decode_img_data(img)   → reads LSBs → msgtobinary() → terminator check
├── txt_steg()
│   ├── encode_txt_data()      → txt_encode() → ZWC mapping → UTF-8 file write
│   └── decode_txt_data()      → reads ZWC → binary reconstruction → XOR decode
├── aud_steg()
│   ├── encode_aud_data()      → wave frames → 2-bit indicator scheme → WAV write
│   └── decode_aud_data()      → reads indicator bits → assembles bytes → terminator
└── vid_steg()
    ├── encode_vid_data()      → frame selection → embed() → encryption() → LSB
    └── decode_vid_data()      → frame selection → extract() → decryption() → RC4
```

---

## 🔑 Key Concepts Recap

| Concept | Explanation |
|---------|-------------|
| **LSB (Least Significant Bit)** | The last bit of a binary number. Changing it changes the value by ±1 at most. |
| **XOR (^)** | Bitwise operation; `A XOR B XOR B = A`. Used for lightweight scrambling and RC4. |
| **Zero-Width Characters** | Invisible Unicode characters invisible to humans but readable by machines. |
| **Terminator Sequence** | `*^*^*` or `111111111111` marks end of embedded message. |
| **RC4** | A stream cipher that generates a pseudo-random keystream XOR'd with plaintext. |
| **AES-256 (in api.py)** | Military-grade block cipher used in the advanced web mode. |
| **PSNR/SSIM** | Metrics measuring how similar the stego file is to the original. Higher = more invisible. |
