import cv2
import numpy as np

def msgtobinary(msg):
    if type(msg) == str: return ''.join([ format(ord(i), "08b") for i in msg ])
    elif type(msg) == bytes or type(msg) == np.ndarray: return [ format(i, "08b") for i in msg ]
    elif type(msg) == int or type(msg) == np.uint8: return format(msg, "08b")
    else: raise TypeError("Input type is not supported in this function")

def KSA(key):
    key_length = len(key)
    S=list(range(256)) 
    j=0
    for i in range(256):
        j=(j+S[i]+key[i % key_length]) % 256
        S[i],S[j]=S[j],S[i]
    return S

def PRGA(S,n):
    i=0; j=0; key=[]
    while n>0:
        n=n-1
        i=(i+1)%256
        j=(j+S[i])%256
        S[i],S[j]=S[j],S[i]
        K=S[(S[i]+S[j])%256]
        key.append(K)
    return key

def rc4_encrypt_decrypt(text, key_str):
    if not key_str: key_str = "default_key"
    key = [ord(c) for c in key_str]
    S = KSA(key)
    keystream = np.array(PRGA(S, len(text)))
    text_arr = np.array([ord(i) for i in text])
    cipher = keystream ^ text_arr
    return ''.join([chr(c) for c in cipher])

def embed_vid_frame(frame, data, password):
    data = rc4_encrypt_decrypt(data, password)
    data +='*^*^*'
    binary_data=msgtobinary(data)
    length_data = len(binary_data)
    index_data = 0
    for row in frame:
        for pixel in row:
            r, g, b = msgtobinary(pixel)
            if index_data < length_data:
                pixel[0] = int(r[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data < length_data:
                pixel[1] = int(g[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data < length_data:
                pixel[2] = int(b[:-1] + binary_data[index_data], 2) 
                index_data += 1
            if index_data >= length_data:
                break
        if index_data >= length_data:
            break
    return frame

def extract_vid_frame_fast(frame, password):
    flat_frame = frame.flatten()
    data_binary = ""
    decoded_data = ""
    for val in flat_frame:
        data_binary += format(val, "08b")[-1]
        if len(data_binary) % 8 == 0:
            byte = data_binary[-8:]
            try:
                decoded_data += chr(int(byte, 2))
            except:
                pass
            if decoded_data.endswith("*^*^*"):
                encrypted_msg = decoded_data[:-5]
                return rc4_encrypt_decrypt(encrypted_msg, password)
    return "No Hidden Data Found"

def test():
    # create original video
    frame = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    msg = "hello world!"
    frame_ste = frame.copy()
    frame_ste = embed_vid_frame(frame_ste, msg, "pass")
    extracted = extract_vid_frame_fast(frame_ste, "pass")
    print("Direct extraction:", extracted)

    # test codec
    fourcc = cv2.VideoWriter_fourcc(*'mp4v') # try XVID, HFYU, FFV1, png, etc
    out = cv2.VideoWriter('test.mp4', fourcc, 25.0, (100,100))
    out.write(frame_ste)
    out.release()
    
    cap = cv2.VideoCapture('test.mp4')
    ret, frame_read = cap.read()
    print("Same frame after mp4v?", np.array_equal(frame_ste, frame_read))
    extracted_mp4 = extract_vid_frame_fast(frame_read, "pass")
    print("Extracted from mp4v mp4:", extracted_mp4)
    
    # Now try FFV1 / avi
    fourcc_pf = cv2.VideoWriter_fourcc(*'FFV1') 
    out2 = cv2.VideoWriter('test.avi', fourcc_pf, 25.0, (100,100))
    out2.write(frame_ste)
    out2.release()
    
    cap2 = cv2.VideoCapture('test.avi')
    ret, frame_read2 = cap2.read()
    print("Same frame after FFV1 avi?", np.array_equal(frame_ste, frame_read2))
    extracted_avi = extract_vid_frame_fast(frame_read2, "pass")
    print("Extracted from FFV1 avi:", extracted_avi)

if __name__ == "__main__":
    test()
