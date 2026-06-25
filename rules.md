# Antigravity Main Agent Rules

## 1. Terminal Proxy & rtk Execution Policy
- **Mandatory Interception**: You MUST prefix all high-volume shell execution, testing, compilation, and discovery commands with the `rtk` proxy (e.g., `rtk npm test`, `rtk rg "pattern"`).
- **Tool Bypass Override**: Because native workspace tools (e.g., built-in file viewers/greppers) bypass auto-rewrite hooks, explicitly drop to a terminal shell using `rtk <command>` whenever reading or searching targets exceeding 50 lines.
- **Context Injection**: Never accept raw, uncompressed terminal text loops if an `rtk` compressed equivalent can be streamed.

## 2. Dynamic Operational Boundaries
- **Workspace Default**: Maintain autonomous operations within the workspace root and `~/.gemini/antigravity/logs/`.
- **Flexible Escalation**: If a solution strictly requires altering files outside the workspace root or executing highly destructive commands (`sudo`, `rm -rf` outside build targets), do not halt or fail. Explicitly request permission from the user via `ASK_USER`.

## 3. Subagent & Workflow Oversight
- **Workflow Enforcement**: You must strictly execute the script-first methodology dictated in `workflow.md` before spinning up subagents.
- **Fail-Safe Mechanism**: If any self-healing script or subagent loop fails 3 times sequentially, use `.agents/toolset/blueprint_tool.py --log-fail` to log the pattern instantly, immediately pause operations, summarize the roadblock, and return control to the USER. When the user resolves the issue, use `--purge` to clear the failed state.