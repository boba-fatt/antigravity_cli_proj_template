# Antigravity Subagent Configuration (CLI Optimized)

## 1. Token & Context Management (rtk & SLIM)
- **rtk Proxy Enforcement**: Maximize token compression by routing all shell calls through `rtk`. Prefix manual shell commands (`cat`, `rg`, `grep`, `git`) with `rtk` when targeting long files to prevent core agent context bloat.
- **SLIM Optimization**: Rely on SLIM’s low-latency message transport layer for structural routing. Do not execute heavy manual database schema checks; trust SLIM’s compressed data pipeline.

## 2. Self-Healing & Memory Loop
When a CLI or script execution returns a non-zero exit code:
1. **Intercept & Repair**: Analyze the stderr. Adjust parameters, install missing prerequisites if safe, and re-run (Max **3** attempts matching the global fail-safe rule).
## 2. Self-Healing & Memory Loop
When a CLI or script execution returns a non-zero exit code:
1. **State Discovery**: NEVER blindly retry. You must immediately execute a state-discovery command sequence (`ls`, validate paths, check configs) to understand the local state before adjusting parameters.
2. **Intercept & Repair**: Analyze the stderr and state discovery output. Adjust parameters, install missing prerequisites if safe, and re-run (Max **3** attempts matching the global fail-safe rule).
3. **Unified Memory Logging (Decoupled Memory Controller)**: Do not manually read or write raw cache files. You must use the Gateway Pattern via `.agents/toolset/blueprint_tool.py` as a strict CLI API:
   - **On Success**: Run `--log-success --cmd "<cmd>" --error "<err>" --fix "<fix>"` to register a verified fix pathway using an instant, atomic line-append operation to eliminate write-concurrency locks.
   - **On Failure**: Run `--log-fail --cmd "<cmd>" --error "<err>"` to cache a persistent failure state instantly via atomic line-append.
4. **Pre-Flight Check**: Before executing a command, scan the active logs using `--check "<cmd>"`. If a match is found, apply the cached context.
5. **User Recovery for Failed States**: When an environment crash halts execution, the Main Agent must prompt the user to confirm resolution. Upon confirmation, execute `--purge "<cmd>"` to clear the capability block.

## 3. Delivery Requirements
- **Verification**: Provide clear terminal-based proof or validation logs verifying successful state changes.
- **Artifact Generation**: Deliver a dense, non-conversational Task Summary along with the clean structural changes.