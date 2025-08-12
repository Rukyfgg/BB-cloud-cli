# BB-cloud-Tool for Termux

A command-line tool to automate BeibeiCloud account creation, inviting, and ad-watching tasks, specifically configured for use in Termux.

## Update

**Efficiency of creating account is decreased due to recent blacklist of many email domain by bb cloud**

## Tutorial 

https://youtu.be/ovewqi7d5i4

## Features

- **Account Creator**: Automatically creates accounts using a temporary email service and Tor for IP rotation.
- **Inviter**: Uses your created accounts to send invites to a specified code.
- **Ad Watcher**: Cycles through all your accounts to perform the "watch ad" task, with automatic Tor IP rotation for each account.

---

## Installation & Setup on Termux

Follow these steps carefully to ensure the tool works correctly.

**Step 1: Update Termux and Install Core Packages**

Open Termux and run these commands to update your environment and install necessary system libraries.

```bash
pkg update && pkg upgrade -y
pkg install python tor git libjpeg-turbo libcrypt -y
```

**Step 2: Clone the Tool from GitHub**

Clone this repository into your Termux home directory.

```bash
git clone https://github.com/Rukyfgg/BB-cloud-cli.git
cd BB-cloud-cli
```

**Step 3: Install Python Dependencies**

Install all the required Python libraries using `pip`.

```bash
pip install -r requirements.txt
```

**Step 4: Configure Tor**

This is the most critical step. You must edit the Tor configuration file to allow the script to control it.

1.  Open the `torrc` file with the nano text editor:
    ```bash
    nano $PREFIX/etc/tor/torrc
    ```

2.  Scroll to the bottom of the file and add these two lines:
    ```
    ControlPort 9051
    CookieAuthentication 1
    ```

3.  Save the file and exit nano:
    *   Press `Ctrl` + `X`
    *   Press `Y` to confirm you want to save.
    *   Press `Enter` to confirm the file name.

**Step 5: Start Tor**

You must start the Tor service before running the tool. Run it in the background so you can still use your terminal.

```bash
tor &
```

You should see messages like "Bootstrapped 100% (done): Done". You can now press `Enter` to get your command prompt back. Tor is running.

---

## Usage

All commands are run from the `BB-cloud-cli` directory. The tool will create and manage a file named `account.json` in the same directory.

### Create Accounts

To create new accounts, use the `create` command. This process requires a working Tor connection.

```bash
# Example: Create 5 new accounts
python bby_tool.py create -c 5
```

### Send Invites

To use your existing accounts to send invites, use the `invite` command.

```bash
# Example: Send 10 invites using the code 'abcdef12'
python bby_tool.py invite --code abcdef12 -c 10
```

### Watch Ads

To start the continuous ad-watching loop, use the `watchads` command. This will run indefinitely until you stop it with `Ctrl` + `C`.

```bash
# Start the ad watcher
python bby_tool.py watchads
```

---

## Troubleshooting

- **"Could not connect to Tor Control Port..."**:
    1.  Make sure you have started Tor with `tor &`.
    2.  Double-check that you correctly edited the `$PREFIX/etc/tor/torrc` file as described in Step 4.
    3.  Restart Tor: kill the existing process with `pkill tor` and start it again with `tor &`.

- **"ModuleNotFoundError" or "ImportError"**:
    - You likely forgot to install the Python dependencies. Run `pip install -r requirements.txt` again.
    - Make sure you are in the `BB-cloud-cli` directory when running the script.

- **Account creation fails**:
    - Your Tor IP might be blocked. The script automatically requests a new one, but sometimes you can get a streak of bad IPs.
