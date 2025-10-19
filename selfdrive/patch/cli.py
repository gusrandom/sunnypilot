#!/usr/bin/env python3
import argparse, json, os, subprocess, sys
from datetime import datetime

REPO = "/data/openpilot"
PATCH = "/data/patches/torque.patch"
PARAMS_PATH = "/data/params/d"  # Sunnypilot params live here
PARAM_KEY = "TorquePatchApplied"

def now():
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def write_param(obj):
    os.makedirs(PARAMS_PATH, exist_ok=True)
    with open(os.path.join(PARAMS_PATH, PARAM_KEY), "w") as f:
        f.write(json.dumps(obj))

def git_applied() -> bool:
    try:
        subprocess.run(
            ["git", "-C", REPO, "apply", "--reverse", "--check", PATCH],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )
        return True
    except subprocess.CalledProcessError:
        return False

def g(*args, default="unknown"):
    try:
        return subprocess.check_output(["git", "-C", REPO, *args], text=True).strip()
    except Exception:
        return default

def check():
    applied = git_applied()
    status = {
        "applied": bool(applied),
        "mode": "check",
        "branch": g("rev-parse", "--abbrev-ref", "HEAD"),
        "commit": g("rev-parse", "--short", "HEAD"),
        "time": now(),
    }
    write_param(status)
    print(json.dumps(status))
    return 0

def apply():
    rc = subprocess.call(["bash", "/data/patches/apply_torque_patch.sh"])
    applied = git_applied()
    status = {
        "applied": bool(applied),
        "mode": "applied" if rc == 0 and applied else "failed",
        "branch": g("rev-parse", "--abbrev-ref", "HEAD"),
        "commit": g("rev-parse", "--short", "HEAD"),
        "time": now(),
        "script_rc": rc,
    }
    write_param(status)
    print(json.dumps(status))
    return 0 if applied else 1

def main():
    ap = argparse.ArgumentParser(description="Torque patch helper")
    g1 = ap.add_mutually_exclusive_group(required=True)
    g1.add_argument("--check", action="store_true", help="Check if torque.patch is applied")
    g1.add_argument("--apply", action="store_true", help="Apply torque.patch now")
    args = ap.parse_args()

    if not os.path.isdir(os.path.join(REPO, ".git")):
        print(json.dumps({"error": "repo not found", "repo": REPO}), file=sys.stderr)
        return 2
    if not os.path.isfile(PATCH):
        status = {"applied": False, "mode": "missing_patch", "time": now(), "patch": PATCH}
        write_param(status)
        print(json.dumps(status))
        return 1

    if args.check:
        return check()
    if args.apply:
        return apply()

if __name__ == "__main__":
    sys.exit(main())
