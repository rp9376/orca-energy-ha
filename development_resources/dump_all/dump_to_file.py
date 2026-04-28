import argparse
import os
import time
from orca_api import OrcaApi
from datetime import datetime

HARDCODED_HOST_IP = ""  # Set IP here to skip prompt, e.g. "192.168.1.100"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = os.path.join(SCRIPT_DIR, ".orca_token")


def load_token() -> str:
    if os.path.exists(TOKEN_FILE):
        print("Loading token from file.")
        with open(TOKEN_FILE, "r") as f:
            return f.read().strip()
    return ""


def save_token(token: str) -> None:
    print("Saving token to file.")
    with open(TOKEN_FILE, "w") as f:
        f.write(token)


def main():
    parser = argparse.ArgumentParser(description="Dump Orca tag data to file.")
    parser.add_argument(
        "--host",
        default=HARDCODED_HOST_IP or None,
        help="Device IP address (overrides hardcoded value)",
    )
    parser.add_argument(
        "--tag",
        action="append",
        dest="tags",
        metavar="TAG",
        help="Tag to fetch (can be repeated, e.g. --tag 2_MK1_vklop --tag 2_Poti1). "
        "If omitted, all tags are dumped.",
    )
    args = parser.parse_args()

    host = args.host or input("Enter device IP address: ").strip()

    orca = OrcaApi(username="admin", password="admin", host=host)
    orca.initialize()

    stored_token = load_token()
    if stored_token:
        print("Using stored token.")
        OrcaApi.token = stored_token

    if args.tags:
        for uri in OrcaApi.generate_uri(args.tags):
            url = f"http://{host}{uri}"
            result = orca.fetch_data(url)
            print(f"Data for tags {args.tags}:\n{result}\n")
            time.sleep(1)
    else:
        raw_data = orca.sensor_status_all()

        if OrcaApi.token:
            save_token(OrcaApi.token)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(SCRIPT_DIR, f"tag_dump_{timestamp}.txt")
        with open(filename, "w") as f:
            f.write(raw_data)
        print(f"Raw data saved to {filename}")

    if OrcaApi.token:
        save_token(OrcaApi.token)


if __name__ == "__main__":
    main()
