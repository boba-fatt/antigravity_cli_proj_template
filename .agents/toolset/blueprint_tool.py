#!/usr/bin/env python3
import os
import sys
import json
import argparse
import re
from datetime import datetime

MEMORY_FILE = ".agents/memory/cli_knowledge.jsonl"
BACKUP_FILE_PREFIX = ".agents/memory/cli_knowledge_backup_"
MAX_CACHE_RECORDS = 100

def get_timestamp():
    # Use timezone-aware UTC datetime
    from datetime import timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def ensure_directory():
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)

def append_record(record):
    """Atomically append a record to the JSON Lines file."""
    ensure_directory()
    with open(MEMORY_FILE, "a") as f:
        f.write(json.dumps(record) + "\n")
        f.flush()
        os.fsync(f.fileno())

def read_records():
    """Read all records from the JSON Lines file."""
    if not os.path.exists(MEMORY_FILE):
        return []
    records = []
    with open(MEMORY_FILE, "r") as f:
        for line in f:
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
    return records

def write_records(records):
    """Overwrite the JSON Lines file with a list of records."""
    ensure_directory()
    with open(MEMORY_FILE, "w") as f:
        for record in records:
            f.write(json.dumps(record) + "\n")
        f.flush()
        os.fsync(f.fileno())

def handle_check(cmd):
    """Deterministic pre-flight verification using compiled regex patterns."""
    records = read_records()
    matched_entry = None

    # Scan from newest to oldest entries
    for entry in reversed(records):
        pattern = entry.get("command_regex")
        if pattern:
            try:
                if re.search(pattern, cmd):
                    matched_entry = entry
                    if entry.get("status") == "failed":
                        print(f"[PRE-FLIGHT] BLOCKED: Known failure signature matched: {pattern}")
                        print(json.dumps({"status": "failed", "last_error": entry.get("last_error")}))
                        sys.exit(1)
                    break
            except re.error:
                continue

    if matched_entry and matched_entry.get("status") == "success":
        print(f"[PRE-FLIGHT] HIT: Historical resolution context found.")
        print(json.dumps({"status": "success", "resolved_action": matched_entry.get("resolved_action")}, indent=2))
    else:
        print(f"[PRE-FLIGHT] CLEAN: No matching execution boundaries tripped for: {cmd}")

    # Flag maintenance without blocking active execution
    if len(records) > MAX_CACHE_RECORDS:
        print(f"\n[MAINTENANCE_REQUIRED: COUNT={len(records)}]")

def handle_log_success(cmd, error, fix):
    """Registers a verified fix pathway."""
    record = {
        "command_regex": cmd, # Updated to match handle_check logic
        "error_signature": error,
        "resolved_action": fix,
        "status": "success",
        "occurrences": 1,
        "last_used": get_timestamp(),
        "id": hash(f"{cmd}{error}") % 1000000 # Simple unique ID for the record
    }
    append_record(record)
    print(f"Successfully logged fix for '{cmd}'")

def handle_log_fail(cmd, error):
    """Registers a persistent failure state instantly."""
    record = {
        "command_regex": cmd, # Updated to match handle_check logic
        "error_signature": error,
        "status": "failed",
        "occurrences": 1,
        "last_used": get_timestamp(),
        "id": hash(f"{cmd}{error}") % 1000000
    }
    append_record(record)
    print(f"Successfully logged failure for '{cmd}'")

def handle_review_fails():
    """Pulls historical failure data for review."""
    records = read_records()
    fails = [r for r in records if r.get("status") == "failed"]
    if not fails:
        print("No failed records found.")
        return
    print(json.dumps(fails, indent=2))

def handle_convert_to_fix(record_id, resolved_cmd):
    """Promotes a failure entry into a successful automated fix block."""
    records = read_records()
    found = False
    for r in records:
        if str(r.get("id")) == str(record_id):
            r["status"] = "success"
            r["resolved_action"] = resolved_cmd
            r["last_used"] = get_timestamp()
            found = True
            break
    
    if found:
        write_records(records)
        print(f"Successfully converted record {record_id} to a fix.")
    else:
        print(f"Record ID {record_id} not found.", file=sys.stderr)

def handle_purge(cmd):
    """Purges capability block matching a command when user resolves environment issue."""
    records = read_records()
    initial_count = len(records)
    records = [r for r in records if r.get("command_regex") != cmd]
    
    if len(records) < initial_count:
        write_records(records)
        print(f"Successfully purged records for '{cmd}'.")
    else:
        print(f"No records found matching '{cmd}' to purge.", file=sys.stderr)

def handle_cleanup():
    """Rotates data, deduplicates, and truncates the active database."""
    if not os.path.exists(MEMORY_FILE):
        print("No memory file to clean up.")
        return

    records = read_records()
    if not records:
        print("Memory file is empty.")
        return

    # Backup rotation
    from datetime import timezone
    backup_path = f"{BACKUP_FILE_PREFIX}{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')}.jsonl"
    os.rename(MEMORY_FILE, backup_path)
    print(f"Created backup at {backup_path}")

    # Deduplication
    deduped = {}
    for r in records:
        key = (r.get("command_regex"), r.get("error_signature"))
        if key in deduped:
            existing = deduped[key]
            existing["occurrences"] = existing.get("occurrences", 0) + r.get("occurrences", 1)
            # Take the most recent status/timestamp
            if r.get("last_used", "") > existing.get("last_used", ""):
                existing["status"] = r.get("status", existing.get("status"))
                existing["resolved_action"] = r.get("resolved_action", existing.get("resolved_action"))
                existing["last_used"] = r.get("last_used")
        else:
            deduped[key] = r
            
    sorted_records = list(deduped.values())

    # Sort by frequency (desc) and then recency (desc), keeping top 100
    sorted_records.sort(key=lambda x: (x.get("occurrences", 0), x.get("last_used", "")), reverse=True)
    final_records = sorted_records[:MAX_CACHE_RECORDS]

    write_records(final_records)
    print(f"Cleanup complete. Deduped {len(records)} records down to {len(final_records)}.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity Memory Controller API")
    parser.add_argument("--check", metavar="CMD", help="Deterministic pre-flight verification.")
    parser.add_argument("--log-success", action="store_true", help="Registers a verified fix pathway.")
    parser.add_argument("--log-fail", action="store_true", help="Registers a persistent failure state.")
    parser.add_argument("--review-fails", action="store_true", help="Pulls historical failure data.")
    parser.add_argument("--convert-to-fix", action="store_true", help="Promotes a failure to a fix.")
    parser.add_argument("--cleanup", action="store_true", help="Rotates, deduplicates, and truncates the database.")
    parser.add_argument("--purge", metavar="CMD", help="Purges all records related to a command.")

    # Arguments for specific actions
    parser.add_argument("--cmd", help="Command associated with the log.")
    parser.add_argument("--error", help="Error signature associated with the log.")
    parser.add_argument("--fix", help="Resolution action for log-success.")
    parser.add_argument("--id", help="Record ID for convert-to-fix.")
    parser.add_argument("--resolved-cmd", help="Resolved command for convert-to-fix.")

    args = parser.parse_args()

    if args.check:
        handle_check(args.check)
    elif args.log_success:
        if not args.cmd or not args.error or not args.fix:
            print("Error: --log-success requires --cmd, --error, and --fix.", file=sys.stderr)
            sys.exit(1)
        handle_log_success(args.cmd, args.error, args.fix)
    elif args.log_fail:
        if not args.cmd or not args.error:
            print("Error: --log-fail requires --cmd and --error.", file=sys.stderr)
            sys.exit(1)
        handle_log_fail(args.cmd, args.error)
    elif args.review_fails:
        handle_review_fails()
    elif args.convert_to_fix:
        if not args.id or not args.resolved_cmd:
            print("Error: --convert-to-fix requires --id and --resolved-cmd.", file=sys.stderr)
            sys.exit(1)
        handle_convert_to_fix(args.id, args.resolved_cmd)
    elif args.purge:
        handle_purge(args.purge)
    elif args.cleanup:
        handle_cleanup()
    else:
        parser.print_help()
