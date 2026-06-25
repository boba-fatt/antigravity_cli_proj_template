# Antigravity Living Toolset Lifecycle Rules

## 1. Living Toolset Discovery & Script Selection
- **The Toolset Imperative**: Before writing code, initializing scratchpads, or evaluating subagent escalation, you MUST read `.agents/toolset/README.md` to index existing automation scripts.
- **Direct Execution**: If an indexing match is found, bypass all code generation or subagent spawning. Immediately execute the script via the terminal proxy: `rtk python3 .agents/toolset/<script_name>.py` (or the language equivalent).
- **Short-Circuit on Success**: If the execution succeeds, stop the active loop, deliver a 1-sentence confirmation, and present the final output diff to minimize token consumption.

## 2. Script Promotion & Maintenance
- **Scratchpad Migration**: Scripts developed in `.agents/scratchpad/` that successfully resolve repeatable or recurring workflow tasks must be permanently moved into `.agents/toolset/`.
- **Index Updates**: Upon moving a script to the toolset, you must immediately append its usage documentation, flag parameters, and purpose to `.agents/toolset/README.md` to ensure future discovery.