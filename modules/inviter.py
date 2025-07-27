# modules/inviter.py

import requests
import time

# Import from the shared utilities module
from .shared_utils import (
    API_URL_INVITE, load_accounts, save_accounts, generate_full_access_token,
    generate_random_hardware_id
)

def run_inviter(invite_code, num_to_send):
    all_accounts = load_accounts()
    if not all_accounts: return

    available_accounts = [acc for acc in all_accounts if not acc.get('used_for_invite', False)]
    total_available = len(available_accounts)
    print(f"[*] Found {total_available} available accounts for inviting.")

    if total_available == 0:
        print("✅ All accounts have already been used for invites. Nothing to do.")
        return

    if num_to_send > total_available:
        print(f"⚠️ Warning: You requested {num_to_send}, but only {total_available} are available.")
        print(f"[*] Proceeding with all {total_available} available accounts.")
        num_to_send = total_available
    
    accounts_to_process = available_accounts[:num_to_send]
    successful_invites = 0

    for i, account_data in enumerate(accounts_to_process):
        print("\n" + "="*50)
        try:
            user_id = account_data['registration_response']['data']['id']
            user_email = account_data['email']
            static_token = account_data['registration_response']['data']['accessToken']
        except KeyError as e:
            print(f"⚠️ Skipping account #{i+1} due to missing data: {e}")
            continue

        print(f"[*] Processing invite {i+1} of {num_to_send} | Account: {user_email}")

        access_token = generate_full_access_token(static_token)
        hardware_id = generate_random_hardware_id()
        print(f"    - Generated Hardware ID: {hardware_id}")

        headers = {'User-Agent': 'okhttp/4.9.1', 'Content-Type': 'application/json', 'access-token': access_token}
        payload = {"userId": user_id, "inviteCode": invite_code, "hardwareId": hardware_id}

        print(f"    - Sending invite request...")
        try:
            # Note: Inviter does not use Tor in the original script. Add proxies=TOR_PROXIES if needed.
            response = requests.post(API_URL_INVITE, headers=headers, json=payload, timeout=20)
            response.raise_for_status()
            response_data = response.json()
            print(f"    - ✅ Server Response (Status {response.status_code}): {response_data}")

            if response_data.get('code') == 0:
                successful_invites += 1
                account_data['used_for_invite'] = True
                save_accounts(all_accounts) # Save progress immediately
                print("    - 💾 Success! Account marked as used and file updated.")
            else:
                print(f"    - ⚠️ Server returned an error: '{response_data.get('prompt', 'Unknown error')}'.")

        except requests.exceptions.RequestException as e:
            print(f"    - ❌ Failed to send request for {user_email}: {e}.")

        time.sleep(2)

    print("\n" + "="*50)
    print(f"✅ Script finished. Sent {successful_invites} successful invite(s).")
