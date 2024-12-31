#!/usr/bin/python3

# Author: shx16

import subprocess
import time
import os

def generate_wpa_conf(ssid, username, password, interface):
    # Create a temporary configuration file for wpa_supplicant with the given credentials.
    conf_content = f"""
network={{
        ssid="{ssid}"
        scan_ssid=1
        key_mgmt=WPA-EAP
        eap=PEAP
        identity="{username}"
        password="{password}"
        phase1="peaplabel=0"
        phase2="auth=MSCHAPV2"
}}
    """
    conf_file = "/tmp/wpa_supplicant.conf"
    with open(conf_file, "w") as f:
        f.write(conf_content)

    return conf_file

def check_connection(interface, ssid):
    # Verify if the interface is connected to the network with the SSID provided.
    result = subprocess.run(["iwgetid", interface], stdout=subprocess.PIPE)
    connected_ssid = result.stdout.decode('utf-8').strip()

    print(connected_ssid) # comment this if you want, it's just to check if you're connected to the wireless network

    if ssid in connected_ssid:
        return True
    
    return False

def validate_credentials(ssid, username, password, interface="wlan0"):
    """
    Attempts to connect to the WPA Enterprise network with credentials provided.
    Returns True if the connection is successful, False if it is not.
    """
    # Generar archivo de configuración de wpa_supplicant con las credenciales proporcionadas
    conf_file = generate_wpa_conf(ssid, username, password, 'wlan0')# interface)

    try:
        # Iniciar wpa_supplicant con la configuración generada
        print(f"~ Trying to connect to {ssid} with user {username}")
        
        # Execute wpa_supplicant in background
        subprocess.run(["wpa_supplicant", "-B", "-i", interface, "-c", conf_file], stdout = subprocess.DEVNULL)

        # Wait a moment for wpa_supplicant to try to connect
        time.sleep(50)

        # Verify if the connection was successful
        if check_connection(interface, ssid):
            return True
        else:
            return False

    except Exception as e:
        print(f"Connection error with: {e}")
        return False
    finally:
        # killing wpa_supplicant process
        os.system("ps -eo pid,cmd | grep 'wpa_supplicant -B -i wlan0' | grep -v grep | awk '{print $1}' | xargs kill -9")
    
        # Clean the configuration file
        if os.path.exists(conf_file):
            os.remove(conf_file)

def main():
    ssid = 'CHANGE_THIS' # ESSID 
    interface = 'CHANGE_THIS' # NETWORK INTERFACE
    credentials_file = 'CHANGE_THIS.txt' # use format "domain\username:password"

    with open('credentials.txt', 'r') as credentials:
        credentials = [ credential.rstrip() for credential in credentials ]

        for credential in credentials:
            username = credential.split(':')[0]
            password = credential.split(':')[1]

            if validate_credentials(ssid, username, password, interface):
                print(f"[+] Valid Credentials! User: {username}, Password: {password}")
            else:
                print(f"[-] Invalid Credentials! User: {username}, Password: {password}")

if __name__ == "__main__":
    main()
