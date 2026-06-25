#!/usr/bin/env python3
import os
import sys
import json
import subprocess
from datetime import datetime

# Paths to agent infrastructure
MEMORY_FILE = ".agents/memory/cli_knowledge.json"
SCRATCHPAD = ".agents/scratchpad/"
MAX_CACHE_RECORDS = 100

def read_memory():
    """Reads the optimized unified memory layout."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                data = json.load(f)
                if "records" in data:
                    return data
        except json.JSONDecodeError:
            pass
    return {"records": []}

def write_memory(memory):
    """Writes the optimized unified memory layout back to disk."""
    os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def update_cli_knowledge(tool, command, error_sig, action, status):
    """
    Implements the Cache Optimization Laws from agents.md:
    - Regex Generalization (Placeholder / Agent responsibility)
    - Deduplication & Incremental Occurrences
    - Cache Size Capping (Max 100)
    """
    memory = read_memory()
    records = memory["records"]
    
    # 1. Deduplication Check
    existing_record = None
    for r in records:
        if r.get("tool") == tool and r.get("error_signature") == error_sig:
            existing_record = r
            break
            
    timestamp = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    if existing_record:
        existing_record["occurrences"] = existing_record.get("occurrences", 0) + 1
        existing_record["status"] = status
        existing_record["last_used"] = timestamp
        existing_record["resolved_action"] = action
    else:
        # Create a brand new record entry
        new_record = {
            "tool": tool,
            "command_regex": command,  # Agent will substitute variables with regex patterns
            "error_signature": error_sig,
            "resolved_action": action,
            "status": status,
            "occurrences": 1,
            "last_used": timestamp
        }
        records.append(new_record)
        
    # 2. Cache Size Capping (Keep top 100 by frequency/recency)
    if len(records) > MAX_CACHE_RECORDS:
        # Sort by occurrences (ascending), then last_used (ascending) to evict weakest entries
        records.sort(key=lambda x: (x.get("occurrences", 1), x.get("last_used", "")))
        memory["records"] = records[-MAX_CACHE_RECORDS:]
    else:
        memory["records"] = records
        
    write_memory(memory)

def run_command_with_self_healing(tool_name, command, max_retries=3):
    """
    Executes a command. If it fails, checks memory, 
    attempts a fix, and logs the outcome to save token context.
    """
    retries = 0
    last_error = ""
    
    while retries < max_retries:
        print(f"Executing via rtk proxy: {command} (Attempt {retries + 1})")
        
        # Ensure command leverages rtk proxy to preserve context token windows
        full_cmd = f"rtk {command}" if not command.startswith("rtk") else command
        
        result = subprocess.run(full_cmd, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Success!")
            if retries > 0:
                # Log the successful correction pathway
                update_cli_knowledge(tool_name, command, last_error, f"Auto-healed on retry {retries}", "success")
            return True
            
        last_error = result.stderr.strip()
        print(f"Command Failed. Stderr: {last_error}")
        
        # [Self-healing mutation logic based on pre-flight lookups happens here]
        
        retries += 1
        
    # If it falls through all retries, log the sequential failure to the cache
    update_cli_knowledge(tool_name, command, last_error, "Failed all self-healing sequences", "failed")
    return False

if __name__ == "__main__":
    print("Agent Blueprint initialized with Unified Memory Layout.")