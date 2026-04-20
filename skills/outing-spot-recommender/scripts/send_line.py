import json
import sys
import urllib.request
import pathlib


def main():
    if len(sys.argv) != 3:
        print("Usage: send_line.py <text> <to_id>", file=sys.stderr)
        sys.exit(2)

    text = sys.argv[1]
    to_id = sys.argv[2]

    cfg = json.loads(pathlib.Path("line_config.json").read_text(encoding="utf-8"))
    token = cfg["channel_access_token"]

    body = json.dumps({
        "to": to_id,
        "messages": [{"type": "text", "text": text}],
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.line.me/v2/bot/message/push",
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as r:
            print(r.status)
            if 200 <= r.status < 300:
                sys.exit(0)
            sys.exit(1)
    except urllib.error.HTTPError as e:
        print(f"HTTPError: {e.code} {e.reason}", file=sys.stderr)
        print(e.read().decode("utf-8", errors="replace"), file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
