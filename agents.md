# Antigravity Subagent Configuration (CLI Optimized)

## 1. Token & Context Management (rtk & SLIM)
- **rtk Proxy Enforcement**: Maximize token compression by routing all shell calls through `rtk`. Prefix manual shell commands (`cat`, `rg`, `grep`, `git`) with `rtk` when targeting long files to prevent core agent context bloat.
- **SLIM Optimization**: Rely on SLIM’s low-latency message transport layer for structural routing. Do not execute heavy manual database schema checks; trust SLIM’s compressed data pipeline.

## 2. Self-Healing & Memory Loop
When a CLI or script execution returns a non-zero exit code:
1. **Intercept & Repair**: Analyze the stderr. Adjust parameters, install missing prerequisites if safe, and re-run (Max **3** attempts matching the global fail-safe rule).
2. **Unified Memory Logging**: Upon cycle completion, update `.agents/memory/cli_knowledge.json` using this exact schema structure:
   * **Root Object**: Should contain a single key `"records"` holding an array of objects.
   * **Record Keys**:
     * `tool`: String identifier (e.g., "docker", "poetry", "cargo", "powershell", "npm")
     * `command_regex`: Generalized regex pattern string
     * `error_signature`: Cleaned stderr signature string
     * `resolved_action`: Concise resolution summary string
     * `status`: Enumerated string exactly matching "success" or "failed"
     * `occurrences`: Integer counter starting at 1
     * `last_used`: ISO-8601 UTC timestamp string
    - *Example json*: 
     ```json
    {
        "records": [
            {
            "tool": "docker | poetry | cargo | powershell",
            "command_regex": "^docker run -v.*",
            "error_signature": "bind: address already in use",
            "resolved_action": "Kill process on port or append random high port offset",
            "status": "success",
            "occurrences": 4,
            "last_used": "2026-06-24T18:30:00Z"
            }
        ]
    }
    ``` 
3. **Cache Optimization Laws**: When maintaining `cli_knowledge.json`, you must strictly execute these data hygiene routines:
   - **Regex Generalization**: Never write environment-specific absolute file paths, hashes, or unique IDs into `command_regex` or `error_signature`. Replace unique variables with wildcards or generic regex expressions.
   - **Deduplication**: If an entry matching the current `tool` and `error_signature` already exists, do not append a new record. Increment its `occurrences` count, update the `status`, and refresh the `last_used` timestamp.
   - **Cache Size Capping**: Limit the `records` array to a maximum of 100 entries. If a new record causes the array to exceed 100, evict the entry with the lowest `occurrences` count and oldest `last_used` timestamp.
4. **Pre-Flight Check**: Scan `cli_knowledge.json` before every execution. Filter the records array immediately by the active `tool` to minimize processing latency. Proactively apply historical successful fixes and completely avoid patterns flagged with `"status": "failed"`.

## 3. Delivery Requirements
- **Verification**: Provide clear terminal-based proof or validation logs verifying successful state changes.
- **Artifact Generation**: Deliver a dense, non-conversational Task Summary along with the clean structural changes.