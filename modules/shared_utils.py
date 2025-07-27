# modules/shared_utils.py

import time
import json
import random
import hashlib
import requests
import base64
import os
import string

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from stem import Signal
from stem.control import Controller

# --- Main Configuration ---
OUTPUT_FILE = "account.json"

# --- API Configuration ---
API_URL_BASE = 'https://api.beibeicloud.net'
API_URL_WATCH_AD = f'{API_URL_BASE}/bby/activity/watchAd'
API_URL_INVITE = f'{API_URL_BASE}/bby/activity/invite'
API_URL_SEND_CODE = f'{API_URL_BASE}/bby/security/sendValidCode'
API_URL_REGISTER = f'{API_URL_BASE}/bby/security/add'

# --- Token Generation Configuration ---
AES_KEY = b"*(^_hy6%&f734*$\x00"
APP_VERSION = "2.1.4"
MAGIC_NUMBER = 5739146
STATIC_TOKEN_PART_FOR_SEND_CODE = "Cd2hSROIFzV7lmm5hiXQju5Hg1bSYaz9pLEuZAlQbeRbsl1FiZK4xknOC4byUoo9r5bOrhI1yfHRGtznYL6ym2byjX9fFbYaI0mN5XXrN48="
STATIC_TOKEN_PART_FOR_REGISTER = "Ut78FhG4wJcYZghMkwkUVVG3nwklwuM6ctcjIm04SHyDfuwdVnlM1EDAT5PdxIpAGakEOwntIaXLEBwI1CNnYG4El5dBHA7tBOHwSHMG0uk="

# --- Tor Configuration ---
TOR_CONTROL_PORT = 9051
TOR_SOCKS_PORT = 9050
TOR_PROXIES = {
    'http': f'socks5h://127.0.0.1:{TOR_SOCKS_PORT}',
    'https': f'socks5h://127.0.0.1:{TOR_SOCKS_PORT}'
}

# --- Ad Watcher Configuration ---
AD_ID = "300018224"
INFO_STRING = "Network"
CYCLE_WAIT_TIME_SECONDS = 2 * 60 + 10  # 2m 10s
REQUEST_DELAY_SECONDS = 2

# === TOKEN GENERATION FUNCTIONS ===

def _encrypt_part2(timestamp, random_num):
    payload = {
        "timestamp": str(timestamp), "random": str(random_num),
        "version": APP_VERSION, "clientSide": "web"
    }
    plaintext = json.dumps(payload, separators=(',', ':')).encode('utf-8')
    cipher = AES.new(AES_KEY, AES.MODE_ECB)
    padded_data = pad(plaintext, AES.block_size)
    encrypted_bytes = cipher.encrypt(padded_data)
    return base64.b64encode(encrypted_bytes).decode('utf-8')

def _generate_part3_signature(timestamp, random_num):
    hex_string = hex((random_num * random_num) + MAGIC_NUMBER)[2:]
    string_to_hash = f"{timestamp}_{hex_string}"
    return hashlib.md5(string_to_hash.encode('utf-8')).hexdigest()

def generate_full_access_token(static_user_token):
    current_timestamp = int(time.time())
    random_number = random.randint(10001, 99999)
    part2 = _encrypt_part2(current_timestamp, random_number)
    part3 = _generate_part3_signature(current_timestamp, random_number)
    return f"{static_user_token}_{part2}_{part3}"

# === TOR & NETWORK FUNCTIONS ===

def renew_tor_identity():
    """Connects to Tor Control Port and requests a new IP using cookie auth."""
    try:
        with Controller.from_port(port=TOR_CONTROL_PORT) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
            # print("[*] Tor: New identity requested.")
            return True
    except AuthError as e:
        print(f"[TOR ERROR] Authentication failed: {e}")
        print("              Ensure script has permissions for Tor's auth cookie file.")
        return False
    except SocketError:
        print(f"[TOR ERROR] Could not connect to Tor Control Port on {TOR_CONTROL_PORT}.")
        print("              Is the Tor service running and configured correctly in torrc?")
        return False
    except Exception as e:
        print(f"[TOR ERROR] An unexpected error occurred with Tor: {e}")
        return False

def get_current_ip():
    """Checks the current public IP address through the Tor proxy."""
    try:
        response = requests.get("https://api.ipify.org", proxies=TOR_PROXIES, timeout=20)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return "Could not check IP"

def verify_tor_connection():
    """Performs an initial check to see if Tor is connectable."""
    print("[*] Verifying Tor SOCKS proxy connection...")
    try:
        response = requests.get('https://check.torproject.org/api/ip', proxies=TOR_PROXIES, timeout=20)
        response.raise_for_status()
        if not response.json().get("IsTor"):
            print("[!] Warning: SOCKS proxy seems to work, but traffic is not routed through Tor.")
            return False
        print(f"[+] Tor proxy connection successful. Current IP: {response.json().get('IP')}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"\n[!!!] CRITICAL: Could not connect to the Tor SOCKS proxy on 127.0.0.1:{TOR_SOCKS_PORT}.")
        print(f"      Please ensure Tor is running on Termux ('tor &'). Error: {e}")
        return False

# === UTILITY FUNCTIONS ===

def load_accounts():
    """Loads accounts from the JSON file."""
    if not os.path.exists(OUTPUT_FILE):
        print(f"[!] '{OUTPUT_FILE}' not found. No accounts to process.")
        return []
    try:
        with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
            accounts = json.load(f)
        print(f"[*] Successfully loaded {len(accounts)} account(s) from {OUTPUT_FILE}.")
        return accounts
    except (json.JSONDecodeError, IOError) as e:
        print(f"[!] ERROR loading {OUTPUT_FILE}: {e}")
        return []

def save_accounts(accounts_list):
    """Saves the list of accounts to the JSON file."""
    try:
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(accounts_list, f, indent=4)
        # print(f"[*] Successfully saved {len(accounts_list)} account(s) to {OUTPUT_FILE}.")
        return True
    except IOError as e:
        print(f"[!] ERROR saving accounts to {OUTPUT_FILE}: {e}")
        return False

def generate_random_hardware_id(length=16):
    """Generates a random alphanumeric hardwareId."""
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
