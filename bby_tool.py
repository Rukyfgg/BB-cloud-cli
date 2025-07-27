# bby_tool.py

import argparse
import sys
import os

# Ensure the 'modules' directory is in the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'modules'))

try:
    from modules.creator import run_creator
    from modules.inviter import run_inviter
    from modules.ad_watcher import run_watcher
except ImportError as e:
    print(f"Error: Failed to import a module. Make sure all files are in the correct folders.")
    print(f"Details: {e}")
    sys.exit(1)

def handle_create(args):
    """Handler for the 'create' command."""
    print("--- Running Account Creator ---")
    run_creator(args.count)

def handle_invite(args):
    """Handler for the 'invite' command."""
    print("--- Running Inviter ---")
    run_inviter(args.code, args.count)

def handle_watchads(args):
    """Handler for the 'watchads' command."""
    print("--- Running Ad Watcher ---")
    run_watcher()

def main():
    """Main function to set up and parse command-line arguments."""
    parser = argparse.ArgumentParser(
        prog="bby_tool.py",
        description="A command-line tool for automating BeibeiCloud tasks.",
        epilog="Use 'python bby_tool.py <command> --help' for more information on a specific command."
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands', required=True)

    # --- Create Command ---
    parser_create = subparsers.add_parser('create', help='Create new BeibeiCloud accounts using Tor.')
    parser_create.add_argument(
        '-c', '--count',
        type=int,
        required=True,
        help='The number of accounts to create.'
    )
    parser_create.set_defaults(func=handle_create)

    # --- Invite Command ---
    parser_invite = subparsers.add_parser('invite', help='Use existing accounts to send invites.')
    parser_invite.add_argument(
        '--code',
        type=str,
        required=True,
        help='The invite code to use for the invitations.'
    )
    parser_invite.add_argument(
        '-c', '--count',
        type=int,
        required=True,
        help='The number of invites to send from available accounts.'
    )
    parser_invite.set_defaults(func=handle_invite)

    # --- WatchAds Command ---
    parser_watch = subparsers.add_parser('watchads', help='Run the ad watcher in a continuous loop using all accounts.')
    parser_watch.set_defaults(func=handle_watchads)

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    print("===================================")
    print("=      BeibeiCloud CLI Tool       =")
    print("===================================\n")
    main()
