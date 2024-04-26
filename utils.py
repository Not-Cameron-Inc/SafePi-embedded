#!/usr/bin/python3

import time
import datetime
import requests
import subprocess
import requests
import lgpio
import os
import logging
import threading
import json
import ssl
import hashlib
import urllib.parse

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding

# logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


# Hardcoded AES key (32 bytes for AES-256)
AES_KEY = b'\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10' \
          b'\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10'
# Hardcoded IV (16 bytes for AES-CBC)
IV = b'\x01\x23\x45\x67\x89\xab\xcd\xef\xfe\xdc\xba\x98\x76\x54\x32\x10'
INTERVAL = 5

DEFAULT_HEADER = {"Content-Type": "application/x-www-form-urlencoded"}
ACCESS_TOKEN = ''
REFRESH_TOKEN = ''

WEBSERVER = "www.safepi.org"
PORT = 443

# ANSI escape chars
GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"
LOCKLIST = {"Door1": [17,27]}

#####################################################################################
#                                   UTILITIES                                       #
#####################################################################################

def device_functions():
    while True:
        # blink or turn on solid LED to indicate whether network is on.
        threading.Thread(target=manage_indicator).start()
        # update the server
        if ACCESS_TOKEN != '':
            update_status()
        time.sleep(INTERVAL)

def internet_on():
    """ Checks if we are connected to the internet """
    try:
        response = requests.get('http://google.com', timeout=1)
        return True
    except requests.RequestException:
        return False

def update_connection_status(status):
    status_str = f"connected:{status}"
    with open("shared-memory.txt", "w") as file:
        file.write(status_str)

def read_connection_status():
    try:
        with open("shared-memory.txt", "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "connection:False"

def send_request(dest='www.safepi.org', port=443, type='POST', path="", payload=None, headers=DEFAULT_HEADER, token=""):
    """ This function allows requests to the server """
    url = f'https://{dest}:{port}/{path}'

    # Ensure a new dictionary is used for headers to avoid modifying the default
    headers = dict(headers)

    if token:
        headers["Authorization"] = f"Bearer {token}"

    # Prepare data based on the Content-Type
    if headers.get("Content-Type") == "application/json":
        data = json.dumps(payload) if payload else '{}'
    else:
        # URL-encode the payload if the content type is 'application/x-www-form-urlencoded'
        data = urllib.parse.urlencode(payload) if isinstance(payload, dict) else payload

    # print("\nSending data:", url, headers, data)

    try:
        # Select the HTTP method and send the request
        if type == 'GET':
            response = requests.get(url, headers=headers)
        elif type == 'POST':
            response = requests.post(url, data=data, headers=headers)
        elif type == 'PUT':
            response = requests.put(url, data=data, headers=headers)

        # Check the response and raise for bad status
        response.raise_for_status()

        # Return the JSON response
        return response
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return {"error": "failed request", "message": str(e)}

def update_status():
    global ACCESS_TOKEN
    global REFRESH_TOKEN
    locked = read_lock("Door1")
    logging.debug(f'Locked status: {locked}')
    payload = {
        'isLocked': locked,
        'access_token': ACCESS_TOKEN,
        'refresh_token': REFRESH_TOKEN
    }

    headers = {
        'Content-Type': 'application/json'
    }

    response = send_request(
        port=443,
        type='POST',
        path='api/postDoor',
        payload=payload,
        headers=headers
    )
    if not isinstance(response, dict):
        if 'code' in response.text:
            json_response = response.json()
            code = json_response['code']

            if code == 3:
                logging.debug(f"Updating Tokens")
                ACCESS_TOKEN = json_response['access_token']
                REFRESH_TOKEN = json_response['refresh_token']

def current_time():
    return str(datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S"))

def wait_animation(msg, event):
    """ Simple animation to be run in a thread """
    i = 0  # Initialize counter outside the loop
    while not event.is_set():
        i = (i % 3) + 1  # Increment counter, reset to 1 after 4
        dots = '.' * i
        # Clear line and print the message with dots
        print(f'\r{" " * (len(msg) + 4)}', end='\r')  # Clear with spaces
        print(f'\r{msg}{dots}', end='', flush=True)
        time.sleep(1)
    print('\r' + ' ' * (len(msg) + 4), end='\r') 

#####################################################################################
#                                   CRYPTOGRAPHY                                    #
#####################################################################################

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

def decrypt(ciphertext, aes_key, iv):
    """
    This function decrypts using the AES CBC mode. It returns the decoded string.
    """
    # Check if the ciphertext length is valid
    block_size = algorithms.AES.block_size // 8  # AES block size in bytes
    if len(ciphertext) % block_size != 0:
        result = "Incorrect decryption format."
        # raise ValueError("Invalid ciphertext length")
    else:
        # AES key and IV
        aes_key = AES_KEY
        iv = IV

        # Perform decryption
        cipher = Cipher(algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()

        # Unpad the decrypted data
        unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
        decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()
        result = decrypted.decode('utf-8')
    
    # Decode the decrypted data
    return result


#####################################################################################
#                               BLE SERVER COMMANDS                                 #
#####################################################################################
    
def handle_write(message):
    word_list = message.split()
    command = word_list[0]
    if command == 'wifi' and len(word_list) > 2:
        flag = wifi_signin(word_list[1], word_list[2])
        print(f'Wifi setup: {flag}')
    elif command == 'provision':
        provision(word_list[1], word_list[2])
    elif command == 'reboot':
        reboot()
    elif command == 'shutdown':
        shutdown()

def wifi_signin(ssid, password):
    temp_path = f'{os.getcwd()}/tmp/50-cloud-init.yaml'
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
        subprocess.run(['/bin/cp', temp_path, config_path], check=True)
        subprocess.run(["/usr/sbin/netplan", "apply"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False
    finally:
        subprocess.run(["/bin/rm", temp_path], check=False)

def provision(access, refresh):
    global ACCESS_TOKEN
    global REFRESH_TOKEN
    ACCESS_TOKEN = access
    REFRESH_TOKEN = refresh
    # logging.debug(f"ACCESS: {ACCESS_TOKEN}\nREFRESH: {REFRESH_TOKEN}")

def reboot():
    try:
        subprocess.run(["reboot"])
    except Exception as e:
        print(f"Error occurred while rebooting: {e}")

def shutdown():
    try:
        subprocess.run(["shutdown", "-h", "now"])
    except Exception as e:
        print(f"Error occurred while shutting down: {e}")

#####################################################################################
#                                   GPIO CONTROLS                                   #
#####################################################################################
    

def free_gpio_pin(handle, pin):
    """ Manually free a GPIO pin, ignore if not allocated. """
    try:
        lgpio.gpio_free(handle, pin)
    except lgpio.error as e:
        if str(e) != "'GPIO not allocated'":
            print(f"Failed to free pin: {e}")

def setup_gpio(pin):
    handle = lgpio.gpiochip_open(0)
    try:
        # Try to free the pin first in case it was previously claimed
        lgpio.gpio_free(handle, pin)
    except lgpio.error as e:
        # print(f"Error freeing pin {pin}: {e}")
        pass

    # Now attempt to claim the output
    lgpio.gpio_claim_output(handle, pin)
    return handle

def indicator_blinking(stop_blinking_event):
    LED_PIN = 14
    handle = None
    try:
        handle = setup_gpio(LED_PIN)
        while not stop_blinking_event.is_set():
            # Assuming you want to toggle the LED while the event is not set
            lgpio.gpio_write(handle, LED_PIN, 1)  # Turn the LED on
            time.sleep(0.5)  # Adjust timing as needed
            lgpio.gpio_write(handle, LED_PIN, 0)  # Turn the LED off
            time.sleep(0.5)
    except Exception as e:
        # print(f"Exception in blinking: {e}")
        pass
    finally:
        if handle is not None:
            lgpio.gpio_free(handle, LED_PIN)
            lgpio.gpiochip_close(handle)

def manage_indicator():
    stop_blinking_event = threading.Event() 
    blinking_thread = None

    while True:
        connected = internet_on()
        if connected:
            if blinking_thread and blinking_thread.is_alive():
                stop_blinking_event.set() 
                blinking_thread.join() 
        else:
            if blinking_thread is None or not blinking_thread.is_alive():
                stop_blinking_event.clear()  # Clear the event for a fresh start
                blinking_thread = threading.Thread(target=indicator_blinking, args=(stop_blinking_event,))
                blinking_thread.start()        
        time.sleep(INTERVAL) 

def read_lock(door):
    handle = lgpio.gpiochip_open(0)  
    output_pin = LOCKLIST[door][0]
    input_pin = LOCKLIST[door][1] 
    try:
        # Set the output pin
        lgpio.gpio_claim_output(handle, output_pin)
        # Set the input pin
        lgpio.gpio_claim_input(handle, input_pin)
        
        # Set output pin high
        lgpio.gpio_write(handle, output_pin, 1)
        # Give a little time for the state to settle
        time.sleep(0.1)
        
        # Read the input pin
        is_connected = lgpio.gpio_read(handle, input_pin)
        
        # Interpret the result
        if is_connected == 1:
            print("Door1 is LOCKED")
            flag = True
        else:
            print("Door1 is UNLOCKED")
            flag = False
    finally:
        # Clean up, release the pins
        lgpio.gpio_free(handle, output_pin)
        lgpio.gpio_free(handle, input_pin)
        lgpio.gpiochip_close(handle)
        return flag
    

if __name__ == "__main__":
    # example of data and time we will be using
    # print(f'Current date and time: {current_time()}')

    # print(f'Connected: {internet_on()}')

    # payload = {'email': 'test@test.com'}
    # token = 'bcabbf6536edd2ac6043f8d198d91ffca06ad70ea9c01a61d9af54c8336ab870'
    # response = send_request(payload=payload, path='provision_pi', token=token)
    # print(response)
    # access_token = response['access_token']
    # refresh_token = response['refresh_token']
    # print(f'A: {access_token}\nR: {refresh_token}')

    # device_functions()

    # plaintext = "Hello from server"
    # encrypted_text = encrypt(plaintext, AES_KEY, IV)
    # print(f"Encrypted: {encrypted_text}")
    # decrypted_text = decrypt(encrypted_text, AES_KEY, IV)
    # print(f"Decrypted: {decrypted_text}")
    
    # threading.Thread(target=manage_indicator).start()
    update_status()
    