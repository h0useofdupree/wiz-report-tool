#!/usr/bin/env python3
"""
fill_csv_synthetic.py

Generate synthetic rows for an existing CSV schema by *reusing your header*.
- Reads the header from the input CSV (first non-empty line).
- Detects delimiter automatically (";" preferred in EU, falls back to ",") unless overridden.
- Fills common security/ops-style columns with realistic-looking values (timestamps, severities,
  statuses, provider/project IDs, regions, risks/threats, etc.). Unknown columns receive generic values.
- Writes an output CSV with your original header and N synthetic rows.

Examples:
  python fill_csv_synthetic.py -i Sample.csv -o Sample_filled.csv -n 10000
  python fill_csv_synthetic.py -i Sample.csv -o Sample_filled.csv -n 250000 --seed 42
  python fill_csv_synthetic.py -i header_only.csv -d ";" -n 50000

Notes:
- Only the header is used from the input file. Existing data rows are ignored.
- If your header uses quotes or exotic separators, you can force a delimiter with --delimiter.
"""

from __future__ import annotations

import argparse
import csv
import random
import uuid
from pathlib import Path
from datetime import datetime, timedelta

# -------------------------------
# Pools / vocab
# -------------------------------

SEVERITIES = ["Critical", "High", "Medium", "Low", "Informational"]
SEVERITY_WEIGHTS = [0.07, 0.18, 0.38, 0.28, 0.09]

STATUSES = ["Open", "In Progress", "Resolved", "Ignored", "Accepted Risk"]
STATUS_WEIGHTS = [0.45, 0.20, 0.25, 0.05, 0.05]

PROVIDERS = ["AWS", "Azure", "GCP"]
REGIONS = {
    "AWS":  ["us-east-1","us-west-2","eu-central-1","eu-west-1","ap-southeast-1"],
    "Azure":["westeurope","northeurope","eastus","southeastasia","germanywestcentral"],
    "GCP":  ["europe-west3","europe-west1","us-central1","asia-southeast1"],
}
RESOURCE_TYPES = [
    "Virtual Machine","Container","Kubernetes Pod","Database","Object Storage Bucket",
    "Serverless Function","Load Balancer","Managed Disk","Container Image","VPC Firewall Rule"
]
RISK_TAGS = [
    "Public Exposure","Data Exfiltration","Privilege Escalation","Lateral Movement",
    "Ransomware","Compliance","Misconfiguration","Unpatched","Secret Exposure"
]
THREAT_TAGS = [
    "CVE-2024-12345","CVE-2025-0101","CryptoMiner","Botnet","Brute Force",
    "Suspicious Beaconing","Unusual Admin Activity","Known Bad IP"
]
DESCRIPTIONS = [
    "Resource appears publicly accessible. Restrict network exposure.",
    "Outdated packages detected. Patch to latest security releases.",
    "Weak encryption policy configured. Enforce modern TLS settings.",
    "Excessive permissions found. Apply least-privilege.",
    "Admin port exposed externally. Restrict inbound rules.",
    "Secret-like data detected. Rotate and purge sensitive info.",
]
ENVIRONMENTS = ["prod","stage","dev"]

# -------------------------------
# Helpers
# -------------------------------

def detect_delimiter(header_line: str, forced: str | None) -> str:
    if forced:
        return forced
    return ";" if ";" in header_line else ","

def read_header(path: Path) -> str:
    with path.open("r", encoding="utf-8", errors="replace") as f:
        for line in f:
            if line.strip():
                return line.rstrip("\r\n")
    raise RuntimeError("Input appears empty: no non-empty lines found.")

def iso(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds") + "Z"

def rand_date_within(days: int = 365) -> datetime:
    now = datetime.utcnow()
    return now - timedelta(days=random.randrange(days),
                           hours=random.randrange(24),
                           minutes=random.randrange(60),
                           seconds=random.randrange(60))

def pick(pool): return random.choice(pool)
def pick_w(pool, weights): return random.choices(pool, weights=weights, k=1)[0]
def pick_n(pool, a=1, b=3): return ", ".join(random.sample(pool, k=random.randint(a,b)))

def mk_name(rtype: str, prov: str) -> str:
    prefix_map = {
        "Virtual Machine":"vm","Container":"ctr","Kubernetes Pod":"pod","Database":"db",
        "Object Storage Bucket":"bucket","Serverless Function":"fn","Load Balancer":"lb",
        "Managed Disk":"disk","Container Image":"img","VPC Firewall Rule":"fw"
    }
    prefix = prefix_map.get(rtype, "res")
    pfx = {"AWS":"prod","Azure":"stg","GCP":"dev"}[prov]
    suffix = "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=6))
    return f"{pfx}-{prefix}-{suffix}"

def account_id(prov: str) -> str:
    if prov == "AWS":
        return str(random.randrange(10**11, 10**12))
    if prov == "Azure":
        return pick(["core-subscription","security-subscription","data-subscription","app-subscription"])
    if prov == "GCP":
        return "proj-" + "".join(random.choices("abcdefghijklmnopqrstuvwxyz0123456789", k=8))
    return "unknown"

def make_ids(prov: str, rtype: str, name: str, region: str) -> tuple[str, str]:
    if prov == "AWS":
        if rtype == "Virtual Machine":
            rid = "i-" + "".join(random.choices("0123456789abcdef", k=17))
            pid = f"arn:aws:ec2:{region}:{account_id('AWS')}:instance/{rid}"
        elif rtype == "Object Storage Bucket":
            rid = name
            pid = f"arn:aws:s3:::{name}"
        else:
            rid = "res-" + "".join(random.choices("0123456789abcdef", k=10))
            pid = f"arn:aws:ec2:{region}:{account_id('AWS')}:{rid}"
    elif prov == "Azure":
        rid = f"/subscriptions/{uuid.uuid4()}/resourceGroups/rg-{name}/providers/Microsoft.Compute/virtualMachines/{name}"
        pid = rid
    else:  # GCP
        proj = account_id("GCP")
        if rtype == "Virtual Machine":
            rid = f"projects/{proj}/zones/{region}/instances/{name}"
        else:
            rid = f"projects/{proj}/global/resources/{name}"
        pid = rid
    return rid, pid

def synth_value(colname: str, ctx: dict) -> str:
    c = colname.strip().lower()
    # timestamps (avoid double-matching "updated"/"status changed")
    if any(k in c for k in ["created at", "created_at", "creation time", "created time"])\
       and not any(k in c for k in ["update", "status change"]):
        return iso(ctx["created"])
    if "status changed" in c:
        return iso(ctx["status_changed"])
    if "updated" in c or "last seen" in c:
        return iso(ctx["updated"])
    # enums/ids
    if "severity" in c: return pick_w(SEVERITIES, SEVERITY_WEIGHTS)
    if "status" in c and "changed" not in c: return pick_w(STATUSES, STATUS_WEIGHTS)
    if "resource type" in c: return ctx["rtype"]
    if "resource name" in c: return ctx["name"]
    if c == "resource id" or "resource id" in c: return ctx["rid"]
    if "provider id" in c: return ctx["pid"]
    if "cloud provider" in c or c == "provider": return ctx["prov"]
    if "account" in c or "subscription" in c or "project" in c: return ctx["account"]
    if "region" in c or "location" in c: return ctx["region"]
    if "container service" in c: return ctx["cservice"]
    if "title" in c: return ctx["title"]
    if "description" in c or "summary" in c: return pick(DESCRIPTIONS)
    if "risk" in c: return pick_n(RISK_TAGS)
    if "threat" in c: return pick_n(THREAT_TAGS)
    if "assignee" in c or "owner" in c or "responsible" in c: return pick(["Alice Müller","Bob Schneider","Dana Hoffmann","—"])
    # common extras if present
    if "environment" in c or c == "env": return pick(ENVIRONMENTS)
    if "cvss" in c:
        return f"{random.uniform(0,10):.1f}"
    if "cwe" in c:
        return pick([f"CWE-{i}" for i in (79,89,22,269,787,20,200,287)])
    if "count" in c or "number" in c:
        return str(random.randint(0, 500))
    if "bool" in c or c.startswith("is ") or c.startswith("has "):
        return random.choice(["true","false"])
    # fallback
    return f"sample-{random.randrange(1_000_000):06d}"

# -------------------------------
# Main
# -------------------------------

def main():
    ap = argparse.ArgumentParser(description="Fill a CSV with synthetic rows based on its header.")
    ap.add_argument("-i", "--input", type=Path, default=Path("Sample.csv"), help="Path to CSV containing the header (first non-empty line).")
    ap.add_argument("-o", "--output", type=Path, default=Path("Sample_filled.csv"), help="Path to write the filled CSV.")
    ap.add_argument("-n", "--rows", type=int, default=10000, help="Number of synthetic rows to generate.")
    ap.add_argument("-d", "--delimiter", type=str, default=None, help="Override delimiter (e.g., ';' or ',').")
    ap.add_argument("--seed", type=int, default=None, help="Random seed for reproducibility.")
    args = ap.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    # Read header & detect delimiter
    header_line = read_header(args.input)
    delim = detect_delimiter(header_line, args.delimiter)

    # Parse header fields with csv to respect quoting if any
    reader = csv.reader([header_line], delimiter=delim)
    cols = next(reader)
    if not cols or all(not c.strip() for c in cols):
        raise RuntimeError("Header appears empty after parsing. Verify the delimiter or pass --delimiter explicitly.")

    # Generate rows
    with args.output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f, delimiter=delim, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(cols)
        for _ in range(args.rows):
            prov = pick(PROVIDERS)
            region = pick(REGIONS[prov])
            rtype = pick(RESOURCE_TYPES)
            name = mk_name(rtype, prov)
            rid, pid = make_ids(prov, rtype, name, region)
            account = account_id(prov)
            created = rand_date_within(360)
            updated = created + timedelta(days=random.randrange(0, 90))
            status_changed = created + timedelta(days=random.randrange(0, 90))
            title = f"{pick(['Public access','Outdated packages','Weak TLS','Open admin port','Excessive permissions','Secret exposure'])} on {rtype.lower()}"
            cservice = pick(["None","EKS","AKS","GKE"]) if ("container" in rtype.lower() or "kubernetes" in rtype.lower()) else "None"

            ctx = dict(
                prov=prov, region=region, rtype=rtype, name=name, rid=rid, pid=pid,
                account=account, created=created, updated=updated, status_changed=status_changed,
                title=title, cservice=cservice
            )
            row = [synth_value(h, ctx) for h in cols]
            writer.writerow(row)

    print(f"✅ Wrote {args.rows} rows to {args.output} (delimiter='{delim}') using header from {args.input}")

if __name__ == "__main__":
    main()
