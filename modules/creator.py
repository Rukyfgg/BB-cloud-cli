# modules/creator.py

import requests
import time
import random
import string
from urllib.parse import quote

# Import from the shared utilities module
from .shared_utils import (
    API_URL_SEND_CODE, API_URL_REGISTER, TOR_PROXIES,
    STATIC_TOKEN_PART_FOR_SEND_CODE, STATIC_TOKEN_PART_FOR_REGISTER,
    generate_full_access_token, renew_tor_identity, load_accounts, save_accounts,
    verify_tor_connection
)


class SmailPro:
    def __init__(self, proxies=None):
        self.session = requests.Session()
        if proxies: self.session.proxies.update(proxies)
        self.smailpro_url = "https://smailpro.com"
        self.api_url = "https://api.sonjj.com"
        self.email_address = None
        base_headers = {'User-Agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36', 'accept-language': 'en-IN,en;q=0.9', 'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"', 'sec-ch-ua-mobile': '?1', 'sec-ch-ua-platform': '"Android"'}
        self.session.headers.update(base_headers)

    def _get_smailpro_payload(self, target_api_url: str) -> str:
        headers = {'authority': 'smailpro.com', 'referer': f'{self.smailpro_url}/', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'same-origin'}
        encoded_url = quote(target_api_url, safe='')
        url = f"{self.smailpro_url}/app/payload?url={encoded_url}"
        if "inbox" in target_api_url and self.email_address: url += f"&email={self.email_address}"
        response = self.session.get(url, headers=headers)
        response.raise_for_status()
        return response.text

    def _call_api(self, endpoint: str, jwt_payload: str) -> dict:
        headers = {'authority': 'api.sonjj.com', 'origin': self.smailpro_url, 'referer': f'{self.smailpro_url}/', 'sec-fetch-dest': 'empty', 'sec-fetch-mode': 'cors', 'sec-fetch-site': 'cross-site'}
        params = {'payload': jwt_payload}
        response = self.session.get(f"{self.api_url}{endpoint}", params=params, headers=headers)
        response.raise_for_status()
        return response.json()

    def start_session(self):
        print("[*] SmailPro: Initializing session via Tor...")
        headers = {'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7', 'authority': 'smailpro.com', 'sec-fetch-dest': 'document', 'sec-fetch-mode': 'navigate', 'sec-fetch-site': 'none', 'sec-fetch-user': '?1', 'upgrade-insecure-requests': '1'}
        response = self.session.get(self.smailpro_url, headers=headers)
        response.raise_for_status()
        if 'XSRF-TOKEN' not in self.session.cookies or 'sonjj_session' not in self.session.cookies:
            raise ConnectionError("SmailPro: Failed to get session cookies.")
        print("[+] SmailPro: Session initialized.")

    def create_email(self) -> (str, dict):
        print("[*] SmailPro: Creating new temporary email...")
        jwt_payload = self._get_smailpro_payload(f"{self.api_url}/v1/temp_email/create")
        response_data = self._call_api("/v1/temp_email/create", jwt_payload)
        if response_data.get("action") == "created" and "email" in response_data:
            self.email_address = response_data["email"]
            print(f"[+] SmailPro: Email Created -> {self.email_address}")
            return self.email_address
        raise ValueError(f"SmailPro: Failed to create email. Response: {response_data}")

    def check_inbox(self) -> (list, dict):
        if not self.email_address: raise ValueError("SmailPro: Email not created.")
        print(f"[*] SmailPro: Checking inbox for {self.email_address}...")
        jwt_payload = self._get_smailpro_payload(f"{self.api_url}/v1/temp_email/inbox")
        response_data = self._call_api("/v1/temp_email/inbox", jwt_payload)
        messages = response_data.get("messages", [])
        if messages: print(f"[+] SmailPro: Found {len(messages)} message(s).")
        else: print("[-] SmailPro: Inbox is empty.")
        return messages

# The BeibeiCloud class is also specific to the creation process.
class BeibeiCloud:
    def __init__(self, proxies=None):
        self.session = requests.Session()
        if proxies: self.session.proxies.update(proxies)
        base_headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36', 'Accept': 'application/json, text/plain, */*', 'Content-Type': 'application/json', 'Accept-Language': 'en-IN,en-GB;q=0.9,en-US;q=0.8,en;q=0.7', 'Origin': 'https://h5.beibeicloud.net', 'Referer': 'https://h5.beibeicloud.net/', 'Sec-Fetch-Dest': 'empty', 'Sec-Fetch-Mode': 'cors', 'Sec-Fetch-Site': 'same-site', 'sec-ch-ua': '"Chromium";v="137", "Not/A)Brand";v="24"', 'sec-ch-ua-mobile': '?0', 'sec-ch-ua-platform': '"Linux"'}
        self.session.headers.update(base_headers)

    def send_validation_code(self, email: str, static_token_part: str) -> dict:
        print(f"[*] BeibeiCloud: Requesting validation code for {email}...")
        fresh_token = generate_full_access_token(static_token_part)
        payload = {"action": 0, "contact": email}
        response = self.session.post(API_URL_SEND_CODE, headers={'Authorization': 'Bearer undefined', 'access-token': fresh_token}, json=payload)
        response.raise_for_status()
        response_json = response.json()
        if response_json.get("code") == 0: print("[+] BeibeiCloud: Validation code sent.")
        else: print(f"[!] BeibeiCloud: Failed to send code. Response: {response_json}")
        return response_json

    def register_account(self, email: str, password: str, otp: str, static_token_part: str) -> dict:
        print(f"[*] BeibeiCloud: Registering account for {email}...")
        fresh_token = generate_full_access_token(static_token_part)
        hardware_id = "web_" + ''.join(random.choices(string.ascii_letters + string.digits, k=20))
        print(f"[*] Using random Hardware ID: {hardware_id}")
        payload = {"loginType": 2, "userKey": email, "password": password, "validCode": otp, "hardwareId": hardware_id}
        response = self.session.post(API_URL_REGISTER, headers={'Authorization': 'Bearer undefined', 'access-token': fresh_token}, json=payload)
        response.raise_for_status()
        response_json = response.json()
        if response_json.get("code") == 0: print("[+] BeibeiCloud: Account registered successfully!")
        else: print(f"[!] BeibeiCloud: Failed to register account. Response: {response_json}")
        return response_json


def generate_random_password(length=12):
    letters = string.ascii_letters
    digits = string.digits
    special_chars = "#?!@$_-"
    password = [
        random.choice(string.ascii_lowercase),
        random.choice(string.ascii_uppercase),
        random.choice(digits),
        random.choice(special_chars)
    ]
    all_chars = letters + digits + special_chars
    password.extend(random.choices(all_chars, k=length - len(password)))
    random.shuffle(password)
    return "".join(password)

def create_one_account(proxies):
    try:
        password = generate_random_password()
        
        smail_client = SmailPro(proxies=proxies)
        smail_client.start_session()
        temp_email = smail_client.create_email()
        if not temp_email: raise Exception("Could not create temporary email.")

        beibei_client = BeibeiCloud(proxies=proxies)
        send_code_response = beibei_client.send_validation_code(temp_email, STATIC_TOKEN_PART_FOR_SEND_CODE)
        if send_code_response.get("code") != 0:
            raise Exception(f"Failed to request validation code: {send_code_response.get('prompt')}")

        print("\n[*] Waiting for OTP...")
        otp_code = None
        for i in range(6):
            print(f"    Polling attempt {i+1}/6...")
            messages = smail_client.check_inbox()
            if messages and messages[0].get("textSubject"):
                otp_code = messages[0].get("textSubject")
                print(f"[+] OTP Found: {otp_code}")
                break
            time.sleep(10)
        if not otp_code: raise Exception("Timeout: Could not retrieve OTP from inbox.")

        register_response = beibei_client.register_account(temp_email, password, otp_code, STATIC_TOKEN_PART_FOR_REGISTER)
        if register_response.get("code") != 0:
            raise Exception(f"Registration failed: {register_response.get('prompt')}")
        
        return {"email": temp_email, "password": password, "registration_response": register_response}

    except Exception as e:
        print(f"\n[!] FAILED TO CREATE ACCOUNT. Error: {e}")
        return None

def run_creator(num_accounts_to_create):
    if not verify_tor_connection() or not renew_tor_identity():
        print("[!] Halting due to Tor connection issues.")
        return

    successful_registrations = load_accounts()
    
    for i in range(num_accounts_to_create):
        print(f"\n\n{'='*20} CREATING ACCOUNT {i+1}/{num_accounts_to_create} {'='*20}")
        
        if i > 0:
            print("\n[*] Requesting a new Tor IP address...")
            if not renew_tor_identity():
                print("[!!!] Halting script because a new Tor IP could not be obtained.")
                break
            time.sleep(5) # Give Tor a moment

        account_data = create_one_account(proxies=TOR_PROXIES)

        if account_data:
            print(f"\n[SUCCESS] Account {i+1} created successfully.")
            successful_registrations.append(account_data)
            if save_accounts(successful_registrations):
                print(f"[+] All {len(successful_registrations)} accounts saved.")
        else:
            print(f"\n[FAILURE] Account {i+1} could not be created. See logs above.")
        
        if i < num_accounts_to_create - 1:
            print("\nWaiting 5 seconds before next attempt...")
            time.sleep(5)

    print(f"\n\n{'='*20} CREATION COMPLETE {'='*20}")
    print(f"Total successful accounts in file: {len(load_accounts())}")
