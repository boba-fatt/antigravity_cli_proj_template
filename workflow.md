# Antigravity Adaptive Automation Workflow (SLIM & rtk Powered)

## Execution & Tooling Protocol
- **Hard Operational Ceilings**: Before spawning an autonomous subagent, you must apply a strict file-boundary heuristic:
  - Tasks modifying **1 to 2 files** are strictly bound to the `.agents/scratchpad/` workflow. Subagent creation is forbidden.
  - Complex tasks targeting **more than 2 files** bypass the scratchpad and escalate directly to subagents.
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

## Phase 3: Trained Subagent Escalation
If the task targets more than 2 files, spin up a subagent using `agents.md`:
1. **Minimal Context**: Inject *only* targeted file content snippets and the precise error string. DO NOT inject raw cache data.
2. **Pre-Flight Lookup**: The subagent must run `.agents/toolset/blueprint_tool.py --check "<cmd>"` to intercept known failures.
3. **Autonomous Execution & Self-Healing Loop**: The subagent attempts to fix the issue.
   - **On CLI Failure**: You must run a state-discovery command sequence (`ls`, path validation, config checks) *before* attempting to mutate parameters and retry (Max 3 attempts).
   - **On Loop Failure (3+ times)**: Run `.agents/toolset/blueprint_tool.py --log-fail --cmd "<cmd>" --error "<err>"` to cache a persistent failure state instantly, then exit and prompt the user.
   - **User Recovery Prompt**: For environment crashes, prompt the user to confirm resolution. If resolved, execute `.agents/toolset/blueprint_tool.py --purge "<cmd>"` to clear the capability block.

## Phase 4: Post-Success Reflection & Maintenance
1. **Identify the Core Fix**: Extract the exact command or code line that solved the problem.
2. **Train the System**: Run `.agents/toolset/blueprint_tool.py --log-success --cmd "<cmd>" --error "<err>" --fix "<fix>"` to atomically append the verified fix pathway.
3. **Clean Delivery**: Return exactly a 1-sentence success confirmation and the final file git diff back to the Main Agent.
4. **Housekeeping (Idle Time)**: When the workspace pipeline is completely idle, the Main Agent should trigger `.agents/toolset/blueprint_tool.py --cleanup` to rotate, deduplicate, and truncate the active cache database.