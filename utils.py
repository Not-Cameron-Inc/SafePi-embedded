#!/usr/bin/python3

import time
import datetime
import requests
import subprocess
import os

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

# Hardcoded AES key (32 bytes for AES-256)
AES_KEY = b'\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10' \
          b'\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10'
# Hardcoded IV (16 bytes for AES-CBC)
IV = b'\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10'

# Encryption function
def encrypt(plaintext, aes_key, iv):
    """
    This function encrypts plaintext using AES CBC mode. It returns a bytes object.
    """
    aes_key = AES_KEY
    iv = IV
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    plaintext_padded = padder.update(plaintext.encode('utf-8')) + padder.finalize()
    
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(plaintext_padded) + encryptor.finalize()
    return encrypted

# Decryption function
def decrypt(ciphertext, aes_key, iv):
    """
    This function dectyps using the AES CBC mode. It return the decoded string.
    """
    aes_key = AES_KEY
    iv = IV
    cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
    
    unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
    decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
    return decrypted.decode('utf-8')

def send_request(dest, port, path, payload):
    """ 
    This function allows for PUT request server interation to various paths.
    """
    headers = {"Content-Type": "application/json"}
    requests.put(f'https://{dest}:{port}{path}', data=payload, headers=headers) 

def handle_write(message):
    word_list = message.split()
    command = word_list[0]
    if command == 'wifi' and len(word_list) > 2:
        flag = wifi_signin(word_list[1], word_list[2])
        print(f'Wifi setup: {flag}')
    elif command == 'reboot':
        reboot()

def wifi_signin(ssid, password):
    temp_path = f'{os.getcwd()}/tmp/50-cloud-init-temp.yaml'
    config_path = '/etc/netplan/'
    netplan_config_content = f"""\
# This file is generated from information provided by
# the datasource.  Changes to it will not persist across an instance.
# To disable cloud-init's network configuration capabilities, write a file
# /etc/cloud/cloud.cfg.d/99-disable-network-config.cfg with the following:
# network: {{config: disabled}}
network:
    version: 2
    ethernets:
        eth0:
            optional: true
            dhcp4: true
    wifis:
        wlan0:
            optional: true
            access-points:
                {ssid}:
                    password: {password}
            dhcp4: true
    """
    with open(temp_path, "w") as f:
        f.write(netplan_config_content)
    try:
        subprocess.run(['bin/cp', temp_path, config_path], check=True)
        # subprocess.run(["netplan", "apply"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    finally:
        subprocess.run(["/bin/rm", temp_path], check=False)

def reboot():
    try:
        subprocess.run(["reboot"])
    except Exception as e:
        print(f"Error occurred while rebooting: {e}")


if __name__ == "__main__":
    plaintext = 'Hey there!'
    enc_text = encrypt(plaintext, AES_KEY, IV)
    print("Encrypted:", enc_text)
    dec_text = decrypt(enc_text, AES_KEY, IV)
    print("Decrypted:", dec_text)
    # example of data and time we will be using
    print(f'Current date and time: {str(datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"))}')
    wifi_signin('myNetwork', 'thisismypassword')
