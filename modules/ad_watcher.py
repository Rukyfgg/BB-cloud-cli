# modules/ad_watcher.py

import requests
import time
import random

# Import from the shared utilities module
from .shared_utils import (
    API_URL_WATCH_AD, AD_ID, INFO_STRING, CYCLE_WAIT_TIME_SECONDS, REQUEST_DELAY_SECONDS,
    TOR_PROXIES, load_accounts, generate_full_access_token, renew_tor_identity,
    get_current_ip, verify_tor_connection
)

def run_watcher():
    if not verify_tor_connection():
        print("[!] Halting due to Tor connection issues.")
        return
        
    accounts = load_accounts()
    if not accounts: return

    print("\n[*] Ad Watcher will now run in a continuous loop. Press Ctrl+C to stop.")

    cycle_count = 0
    try:
        while True:
            cycle_count += 1
            print(f"\n{'='*60}\n🚀 STARTING CYCLE #{cycle_count}\n{'='*60}\n")

            for i, account in enumerate(accounts):
                try:
                    email = account.get('email', 'N/A')
                    print(f"--- Processing account ({i+1}/{len(accounts)}): {email} ---")

                    print("[*] Requesting new Tor identity...")
                    if not renew_tor_identity():
                        print("[!] Skipping account due to Tor failure. Will retry.")
                        time.sleep(5)
                        continue
                    
                    new_ip = get_current_ip()
                    print(f"[*] Now using IP: {new_ip}")
                    
                    user_data = account['registration_response']['data']
                    user_id = user_data['id']
                    static_token_part = user_data['accessToken']
                    hardware_id = str(random.randint(10**15, 10**16 - 1))
                    
                    full_access_token = generate_full_access_token(static_token_part)
                    
                    headers = {
                        'User-Agent': 'okhttp/4.9.1', 'access-token': full_access_token,
                        'Content-Type': 'application/json; charset=utf-8'
                    }
                    payload = {
                        "userId": user_id, "adId": AD_ID,
                        "info": INFO_STRING, "hardwareId": hardware_id
                    }

                    print("[*] Sending 'watchAd' request via Tor...")
                    response = requests.post(API_URL_WATCH_AD, headers=headers, json=payload, proxies=TOR_PROXIES, timeout=45)
                    response.raise_for_status()
                    
                    print(f"[*] SUCCESS! Server Response: {response.json()}")

                except requests.exceptions.RequestException as e:
                    print(f"[!] HTTP Request FAILED for {email}: {e}")
                except (KeyError, TypeError) as e:
                    print(f"[!] Data Parsing FAILED for {email}. Check account.json. Details: {e}")
                except Exception as e:
                    print(f"[!] An UNEXPECTED ERROR occurred for {email}: {e}")
                
                finally:
                    time.sleep(REQUEST_DELAY_SECONDS)

            print(f"\n{'='*60}\n✅ CYCLE #{cycle_count} COMPLETE.")
            print(f"[*] Waiting {CYCLE_WAIT_TIME_SECONDS}s before next cycle.")
            print(f"{'='*60}")
            time.sleep(CYCLE_WAIT_TIME_SECONDS)

    except KeyboardInterrupt:
        print("\n\n[!] Script stopped by user. Exiting gracefully.")
