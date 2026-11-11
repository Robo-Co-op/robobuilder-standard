#!/usr/bin/env python3
"""Receiver side of the encrypted secret transfer (robobuilder secret-transfer skill).

Runs on the machine that should receive secrets (e.g. a production server). Python 3 stdlib + the
`openssl` CLI only. It NEVER prints secret values -- only names and lengths.

  init   [--dir D] [--rotate]          create keypair if missing; print the PUBLIC cert (base64)
  list   FILE.cms [--dir D]            decrypt in memory; show secret names + lengths
  apply  FILE.cms --env-file F [--map SECRET=VAR ...] [--only A,B] [--dir D]
                                       write secrets into a KEY=value env file (backup first)
  export FILE.cms --out F [--dir D]    write the decrypted JSON bundle to F (mode 0600)

Default key dir: /root/.secret-transfer when run as root, else ~/.secret-transfer.
"""
import argparse
import base64
import datetime
import json
import os
import re
import subprocess
import sys
import tempfile

FORMAT = "secret-transfer/v1"
NAME_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
PLAIN_VALUE_RE = re.compile(r"^[A-Za-z0-9_@%+=:,./\-]*$")


def die(msg):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def default_dir():
    if os.geteuid() == 0:
        return "/root/.secret-transfer"
    return os.path.join(os.path.expanduser("~"), ".secret-transfer")


def paths(d):
    return os.path.join(d, "key.pem"), os.path.join(d, "cert.pem")


def run_openssl(args, data=None):
    try:
        p = subprocess.run(["openssl"] + args, input=data, capture_output=True, check=False)
    except FileNotFoundError:
        die("openssl not found on PATH")
    if p.returncode != 0:
        # stderr from openssl never contains plaintext secrets
        die("openssl failed: " + p.stderr.decode(errors="replace").strip()[:500])
    return p.stdout


def cmd_init(a):
    d = a.dir or default_dir()
    key, cert = paths(d)
    os.makedirs(d, mode=0o700, exist_ok=True)
    os.chmod(d, 0o700)
    if a.rotate or not (os.path.exists(key) and os.path.exists(cert)):
        old = os.umask(0o077)
        try:
            host = os.uname().nodename
            run_openssl(["req", "-x509", "-newkey", "rsa:4096", "-nodes", "-sha256",
                         "-keyout", key, "-out", cert, "-days", "825",
                         "-subj", f"/CN=secret-transfer@{host}"])
        finally:
            os.umask(old)
        os.chmod(key, 0o600)
        os.chmod(cert, 0o644)
        print(f"created keypair in {d}", file=sys.stderr)
    fp = run_openssl(["x509", "-in", cert, "-noout", "-fingerprint", "-sha256"]).decode().strip()
    print(fp, file=sys.stderr)
    # stdout = the only thing callers need: base64 of the PUBLIC certificate
    print(base64.b64encode(open(cert, "rb").read()).decode())


def decrypt(a):
    d = a.dir or default_dir()
    key, cert = paths(d)
    if not os.path.exists(key):
        die(f"no private key in {d}; run `init` first (on this machine, as this user)")
    out = run_openssl(["cms", "-decrypt", "-binary", "-inform", "DER",
                       "-in", a.file, "-inkey", key, "-recip", cert])
    try:
        bundle = json.loads(out)
    except ValueError:
        die("decrypted payload is not valid JSON")
    if bundle.get("format") != FORMAT or not isinstance(bundle.get("secrets"), dict):
        die(f"unexpected bundle format (want {FORMAT})")
    return bundle


def describe(bundle):
    print(f"bundle: run_id={bundle.get('run_id')} created_at={bundle.get('created_at')}")
    for k in sorted(bundle["secrets"]):
        print(f"  {k}  ({len(bundle['secrets'][k])} chars)")


def cmd_list(a):
    describe(decrypt(a))


def env_line(var, value):
    if "\n" in value or "\r" in value:
        die(f"{var}: multi-line value cannot go in an env file; use `export` instead")
    if PLAIN_VALUE_RE.match(value):
        return f"{var}={value}\n"
    if "'" not in value:
        return f"{var}='{value}'\n"
    die(f"{var}: value contains a single quote and special characters; use `export` instead")


def cmd_apply(a):
    bundle = decrypt(a)
    secrets = bundle["secrets"]
    mapping = {}
    for m in a.map or []:
        if "=" not in m:
            die(f"--map expects SECRET=VAR, got {m!r}")
        s, v = m.split("=", 1)
        if not NAME_RE.match(v):
            die(f"invalid env var name {v!r}")
        mapping[s] = v
    names = sorted(secrets)
    if a.only:
        wanted = [n.strip() for n in a.only.split(",") if n.strip()]
        missing = [n for n in wanted if n not in secrets]
        if missing:
            die("not in bundle: " + ", ".join(missing))
        names = wanted
    updates = {mapping.get(n, n): secrets[n] for n in names}

    f = a.env_file
    lines = open(f).read().splitlines(True) if os.path.exists(f) else []
    st = os.stat(f) if os.path.exists(f) else None
    if st:
        ts = datetime.datetime.now(datetime.timezone.utc).strftime("%Y%m%d-%H%M%S")
        bak = f"{f}.bak-secret-transfer-{ts}"
        with open(bak, "w") as b:
            b.writelines(lines)
        os.chown(bak, st.st_uid, st.st_gid)
        os.chmod(bak, 0o600)
        print(f"backup: {bak}")

    done = set()
    for i, l in enumerate(lines):
        m = re.match(r"^\s*(?:export\s+)?([A-Za-z_][A-Za-z0-9_]*)=", l)
        if m and m.group(1) in updates:
            lines[i] = env_line(m.group(1), updates[m.group(1)])
            done.add(m.group(1))
    if lines and not lines[-1].endswith("\n"):
        lines[-1] += "\n"
    for var in updates:
        if var not in done:
            lines.append(env_line(var, updates[var]))

    fd, tmp = tempfile.mkstemp(dir=os.path.dirname(os.path.abspath(f)), prefix=".secret-transfer-")
    with os.fdopen(fd, "w") as t:
        t.writelines(lines)
    os.chmod(tmp, 0o600)
    if st:
        os.chown(tmp, st.st_uid, st.st_gid)
    os.replace(tmp, f)
    for var in updates:
        print(f"{'updated' if var in done else 'added'}: {var}")
    print("note: running services only see new env values after they reload/restart; "
          "reload or restart the service the way its runbook says")


def cmd_export(a):
    bundle = decrypt(a)
    old = os.umask(0o077)
    try:
        with open(a.out, "w") as o:
            json.dump(bundle, o)
    finally:
        os.umask(old)
    os.chmod(a.out, 0o600)
    describe(bundle)
    print(f"written: {a.out} (0600) -- delete it (shred -u) when done")


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("init"); s.add_argument("--dir"); s.add_argument("--rotate", action="store_true"); s.set_defaults(fn=cmd_init)
    s = sub.add_parser("list"); s.add_argument("file"); s.add_argument("--dir"); s.set_defaults(fn=cmd_list)
    s = sub.add_parser("apply"); s.add_argument("file"); s.add_argument("--dir")
    s.add_argument("--env-file", required=True); s.add_argument("--map", action="append")
    s.add_argument("--only"); s.set_defaults(fn=cmd_apply)
    s = sub.add_parser("export"); s.add_argument("file"); s.add_argument("--dir")
    s.add_argument("--out", required=True); s.set_defaults(fn=cmd_export)
    a = p.parse_args()
    a.fn(a)


if __name__ == "__main__":
    main()
