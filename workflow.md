# Antigravity Adaptive Automation Workflow (SLIM & rtk Powered)

## Execution & Tooling Protocol
- **The Script-First Imperative**: Before spawning an autonomous subagent, you must algorithmically prove the task cannot be solved via a self-contained script (Python, PowerShell, Bash). If it can be coded, subagent creation is strictly forbidden.
- **Permanent Promotion**: Move proven scripts that solve repeatable tasks to `.agents/toolset/` and index them in `.agents/toolset/README.md`.

## Phase 1: Toolset Discovery & Script Selection
1. **Read Index**: Open `.agents/toolset/README.md`.
2. **Match & Execute**: If a tool matches the task, execute it via the proxy: `rtk python3 .agents/toolset/<script_name>.py`.
3. **Short-Circuit**: On success, return a 1-sentence status and stop to minimize token burn.

## Phase 2: Script Creation & Promotion
1. **Draft**: Synthesize a self-contained execution script inside `.agents/scratchpad/`. Utilize `SLIM` transport commands where necessary to query schema states without raw data dumps.
2. **Execute**: Run via `rtk` (e.g., `rtk python3 .agents/scratchpad/fix_imports.py`).
3. **Token Limit**: Capture only the final output or targeted error lines. Strip all intermediate print statements.
4. **Promote**: Move successful, repeatable scripts into `.agents/toolset/` and update `README.md`.

## Phase 3: Trained Subagent Escalation (Last Resort)If static scripting cannot handle deep conceptual cross-file edits, spin up a subagent using `agents.md`:
1. **Minimal Context**: Inject *only* targeted file content snippets, the precise error string, and the `.agents/memory/cli_knowledge.json` history dictionary.
2. **Pre-Flight Lookup**: The subagent must cross-reference `cli_knowledge.json` before writing code or running commands to intercept known failures.
3. **Autonomous Execution & Self-Healing Loop**: The subagent attempts to fix the issue.
   - **On CLI Failure**: Intercept stderr, consult memory, auto-correct parameters, and retry (Max 3 attempts).
   - **On Loop Failure (3+ times)**: Log the pattern directly to `.agents/memory/cli_knowledge.json` with `"status": "failed"` following the optimization laws in `agents.md`, then exit and prompt the user.

## Phase 4: Post-Success Reflection & Training
1. **Identify the Core Fix**: Extract the exact command or code line that solved the problem.
2. **Train the System**: Update or append the behavior to `.agents/memory/cli_knowledge.json` with `"status": "success"` following the data hygiene routines in `agents.md`.
3. **Clean Delivery**: Return exactly a 1-sentence success confirmation and the final file git diff back to the Main Agent.