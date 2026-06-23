#!/usr/bin/env python3
"""
NGL Link CLI - Send anonymous messages via ngl.link

Usage:
    ngl send <username> <message>        Send a single message
    ngl spam <username> <message> <count> Spam multiple messages
"""

import argparse
import random
import string
import sys
import time
import json
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Optional

import requests


@dataclass
class NGLConfig:
    base_url: str = "https://ngl.link"
    user_agent: str = (
        "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36"
    )
    timeout: int = 30


def generate_device_id() -> str:
    """Generate a random device ID in the format xxxx-xxxx-xxxx-xxxx."""
    segments = [''.join(random.choices(string.hexdigits.lower(), k=4)) for _ in range(4)]
    return '-'.join(segments)


def generate_message_id() -> str:
    """Generate a UUID-like message ID."""
    return str(uuid.uuid4())


def send_message(
    username: str,
    message: str,
    config: NGLConfig = None,
    device_id: str = None,
) -> tuple[bool, str]:
    """
    Send an anonymous message to a user on ngl.link.

    Returns:
        Tuple of (success: bool, message: str)
    """
    if config is None:
        config = NGLConfig()

    if device_id is None:
        device_id = generate_device_id()

    # The actual API endpoint discovered from main.js
    url = f"{config.base_url}/api/submit"

    headers = {
        "User-Agent": config.user_agent,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "*/*",
        "Origin": config.base_url,
        "Referer": f"{config.base_url}/{username}",
        "X-Requested-With": "XMLHttpRequest",
    }

    data = {
        "username": username,
        "question": message,
        "deviceId": device_id,
        "gameSlug": "",
        "referrer": "",
        "push_ref": "",
    }

    try:
        response = requests.post(
            url,
            data=data,
            headers=headers,
            timeout=config.timeout,
        )

        if response.status_code == 200:
            try:
                resp_json = response.json()
                if resp_json.get("questionId"):
                    return True, "Message sent successfully"
            except:
                pass
            return True, "Message sent successfully"
        elif response.status_code == 404:
            return False, "HTTP 404: API endpoint not found"
        elif response.status_code == 429:
            return False, "Rate limited - too many requests"
        else:
            return False, f"HTTP {response.status_code}: {response.reason}"

    except requests.exceptions.Timeout:
        return False, "Request timed out"
    except requests.exceptions.ConnectionError:
        return False, "Connection error - check your internet"
    except requests.exceptions.RequestException as e:
        return False, f"Request failed: {e}"


def spam_messages(
    username: str,
    message: str,
    count: int,
    delay: float = 0,
    threads: int = 1,
    random_device_id: bool = False,
) -> None:
    """Send multiple messages with optional rate limiting."""
    config = NGLConfig()

    print(f"Sending {count} messages to @{username}...")

    def send_one(i: int) -> tuple[int, bool, str]:
        device_id = generate_device_id() if random_device_id else None
        success, msg = send_message(username, message, config, device_id)
        return i, success, msg

    sent = 0
    failed = 0

    if threads == 1:
        for i in range(count):
            _, success, msg = send_one(i)
            if success:
                sent += 1
            else:
                failed += 1
            if delay > 0 and i < count - 1:
                time.sleep(delay)
            if (i + 1) % 10 == 0:
                print(f"  Progress: {i + 1}/{count} (sent: {sent}, failed: {failed})")
    else:
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(send_one, i): i for i in range(count)}

            for future in as_completed(futures):
                _, success, msg = future.result()
                if success:
                    sent += 1
                else:
                    failed += 1

                if delay > 0:
                    time.sleep(delay)

                total = sent + failed
                if total % 10 == 0:
                    print(f"  Progress: {total}/{count} (sent: {sent}, failed: {failed})")

    print(f"\nDone! Sent: {sent}, Failed: {failed}")


def main():
    parser = argparse.ArgumentParser(
        description="NGL Link CLI - Send anonymous messages",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ngl send username Hi
  ngl send username "Hello World"
  ngl spam username Hi 10
  ngl spam username Hi 100 --delay 1 --threads 5
        """
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # send command
    send_parser = subparsers.add_parser("send", help="Send a single message")
    send_parser.add_argument("username", help="NGL username (without @)")
    send_parser.add_argument("message", help="Message to send")
    send_parser.add_argument("--device-id", help="Device ID to use")

    # spam command
    spam_parser = subparsers.add_parser("spam", help="Send multiple messages")
    spam_parser.add_argument("username", help="NGL username (without @)")
    spam_parser.add_argument("message", help="Message to send")
    spam_parser.add_argument("count", type=int, help="Number of messages to send")
    spam_parser.add_argument("--delay", type=float, default=0,
                            help="Delay between messages in seconds")
    spam_parser.add_argument("--threads", type=int, default=1,
                            help="Number of concurrent threads")
    spam_parser.add_argument("--random-device", action="store_true",
                            help="Use random device ID for each message")

    args = parser.parse_args()

    config = NGLConfig()

    if args.command == "send":
        success, msg = send_message(
            args.username,
            args.message,
            config,
            args.device_id,
        )
        if success:
            print(f"Success: {msg}")
            sys.exit(0)
        else:
            print(f"Error: {msg}")
            sys.exit(1)

    elif args.command == "spam":
        spam_messages(
            args.username,
            args.message,
            args.count,
            delay=args.delay,
            threads=args.threads,
            random_device_id=args.random_device,
        )


if __name__ == "__main__":
    main()
