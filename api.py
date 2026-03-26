import cv2
import numpy as np
import wave
import os

def msgtobinary(msg):
    if type(msg) == str:
        result= ''.join([ format(ord(i), "08b") for i in msg ])
    elif type(msg) == bytes or type(msg) == np.ndarray:
        result= [ format(i, "08b") for i in msg ]
    elif type(msg) == int or type(msg) == np.uint8:
        result=format(msg, "08b")
    else:
        raise TypeError("Input type is not supported in this function")
    return result

def encode_img_data(img, data, nameoffile):
    if (len(data) == 0): 
        raise ValueError('Data entered to be encoded is empty')
    no_of_bytes=(img.shape[0] * img.shape[1] * 3) // 8
    if(len(data)>no_of_bytes):
        raise ValueError("Insufficient bytes Error, Need Bigger Image or give Less Data !!")
    data +='*^*^*'    
    binary_data=msgtobinary(data)
    length_data=len(binary_data)
    index_data = 0
    for i in img:
        for pixel in i:
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
    cv2.imwrite(nameoffile, img)
    return nameoffile

def decode_img_data(img):
    data_binary = ""
    for i in img:
        for pixel in i:
            r, g, b = msgtobinary(pixel) 
            data_binary += r[-1]  
            data_binary += g[-1]  
            data_binary += b[-1]  
            total_bytes = [ data_binary[i: i+8] for i in range(0, len(data_binary), 8) ]
            decoded_data = ""
            for byte in total_bytes:
                decoded_data += chr(int(byte, 2))
                if decoded_data[-5:] == "*^*^*": 
                    return decoded_data[:-5]
    return "No Hidden Data Found"

def txt_encode(text, cover_file_path, out_file_path):
    l=len(text)
    i=0
    add=''
    while i<l:
        t=ord(text[i])
        if(t>=32 and t<=64):
            t1=t+48
            t2=t1^170
            res = bin(t2)[2:].zfill(8)
            add+="0011"+res
        else:
            t1=t-48
            t2=t1^170
            res = bin(t2)[2:].zfill(8)
            add+="0110"+res
        i+=1
    res1=add+"111111111111"
    
    ZWC={"00":u'\u200C',"01":u'\u202C',"11":u'\u202D',"10":u'\u200E'}      
    with open(cover_file_path,"r+") as file1:
        word=[]
        for line in file1: 
            word+=line.split()
    with open(out_file_path,"w+", encoding="utf-8") as file3:
        i=0
        while(i<len(res1)):  
            if int(i/12) < len(word):
                s=word[int(i/12)]
            else:
                s=""
            j=0
            HM_SK=""
            while(j<12):
                x=res1[j+i]+res1[i+j+1]
                HM_SK+=ZWC[x]
                j+=2
            s1=s+HM_SK
            file3.write(s1 + " ")
            i+=12
        t=int(len(res1)/12)     
        while t<len(word): 
            file3.write(word[t] + " ")
            t+=1
    return out_file_path

def BinaryToDecimal(binary):
    return int(binary, 2)

def decode_txt_data(stego_file_path):
    ZWC_reverse={u'\u200C':"00",u'\u202C':"01",u'\u202D':"11",u'\u200E':"10"}
    temp=''
    with open(stego_file_path,"r", encoding="utf-8") as file4:
        for line in file4: 
            for words in line.split():
                binary_extract=""
                for letter in words:
                    if(letter in ZWC_reverse):
                         binary_extract+=ZWC_reverse[letter]
                if binary_extract=="111111111111":
                    break
                else:
                    temp+=binary_extract
    i=0; a=0; b=4; c=4; d=12; final=''
    while i<len(temp):
        t3=temp[a:b]
        a+=12; b+=12; i+=12
        t4=temp[c:d]
        c+=12; d+=12
        if(t3=='0110'):
            final+=chr((BinaryToDecimal(t4) ^ 170) + 48)
        elif(t3=='0011'):
            final+=chr((BinaryToDecimal(t4) ^ 170) - 48)
    return final

# Audio Steganography
def encode_aud_data(in_file, data, out_file):
    song = wave.open(in_file, mode='rb')
    nframes=song.getnframes()
    frames=song.readframes(nframes)
    frame_bytes=bytearray(list(frames))
    data = data + '*^*^*'
    result = []
    for c in data:
        bits = bin(ord(c))[2:].zfill(8)
        result.extend([int(b) for b in bits])
    j = 0
    for i in range(0,len(result),1): 
        res = bin(frame_bytes[j])[2:].zfill(8)
        if res[len(res)-4]== str(result[i]):
            frame_bytes[j] = (frame_bytes[j] & 253)
        else:
            frame_bytes[j] = (frame_bytes[j] & 253) | 2
            frame_bytes[j] = (frame_bytes[j] & 254) | result[i]
        j = j + 1
    frame_modified = bytes(frame_bytes)
    with wave.open(out_file, 'wb') as fd:
        fd.setparams(song.getparams())
        fd.writeframes(frame_modified)
    song.close()
    return out_file

def decode_aud_data(in_file):
    song = wave.open(in_file, mode='rb')
    nframes=song.getnframes()
    frames=song.readframes(nframes)
    frame_bytes=bytearray(list(frames))
    extracted = ""
    for i in range(len(frame_bytes)):
        res = bin(frame_bytes[i])[2:].zfill(8)
        if res[len(res)-2]=='0':
            extracted+=res[len(res)-4]
        else:
            extracted+=res[len(res)-1]
        all_bytes = [ extracted[k: k+8] for k in range(0, len(extracted), 8) ]
        decoded_data = ""
        for byte in all_bytes:
            if len(byte)==8:
                decoded_data += chr(int(byte, 2))
                if decoded_data[-5:] == "*^*^*":
                    return decoded_data[:-5]
    return "No Hidden Data Found"

