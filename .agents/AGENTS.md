# Antigravity Rules & Automation Pipeline (AGENTS.md)

## 1. Terminal Proxy & rtk Execution Policy
- **Mandatory Interception**: You MUST prefix all high-volume shell execution, testing, compilation, and discovery commands with the `rtk` proxy (e.g., `rtk npm test`, `rtk rg "pattern"`).
- **Tool Bypass Override**: Because native workspace tools (e.g., built-in file viewers/greppers) bypass auto-rewrite hooks, explicitly drop to a terminal shell using `rtk <command>` whenever reading or searching targets exceeding 50 lines.
- **Context Injection**: Never accept raw, uncompressed terminal text loops if an `rtk` compressed equivalent can be streamed.

## 2. Dynamic Operational Boundaries
- **Workspace Default**: Maintain autonomous operations within the workspace root and `~/.gemini/antigravity/logs/`.
- **Flexible Escalation**: If a solution strictly requires altering files outside the workspace root or executing highly destructive commands (`sudo`, `rm -rf` outside build targets), do not halt or fail. Explicitly request permission from the user via `ASK_USER`.

## 3. Subagent & Workflow Oversight Heuristics
- **Hard Operational Ceilings**: Before spawning an autonomous subagent, you must apply a strict file-boundary heuristic:
  - Tasks modifying **1 to 2 files** are strictly bound to the `.agents/scratchpad/` workflow. Subagent creation is forbidden.
  - Complex tasks targeting **more than 2 files** bypass the scratchpad and escalate directly to subagents.
- **Permanent Promotion**: Move proven scripts that solve repeatable tasks to `.agents/toolset/` and index them in `.agents/toolset/README.md`.
- **Minimal Context**: Inject *only* targeted file content snippets and the precise error string into subagents. DO NOT inject raw cache data.
- **Pre-Flight Lookup**: The subagent must run `.agents/toolset/blueprint_tool.py --check "<cmd>"` to intercept known failures before executing code.

## 4. Living Toolset Discovery & Script Selection
- **The Toolset Imperative**: Before writing code, initializing scratchpads, or evaluating subagent escalation, you MUST read `.agents/toolset/README.md` to index existing automation scripts.
- **Direct Execution**: If an indexing match is found, bypass all code generation or subagent spawning. Immediately execute the script via the terminal proxy: `rtk python3 .agents/toolset/<script_name>.py` (or the language equivalent).
- **Short-Circuit on Success**: If the execution succeeds, stop the active loop, deliver a 1-sentence confirmation, and present the final output diff to minimize token consumption.

## 5. Script Promotion & Maintenance
- **Scratchpad Migration**: Scripts developed in `.agents/scratchpad/` that successfully resolve repeatable or recurring workflow tasks must be permanently moved into `.agents/toolset/`.
- **Index Updates**: Upon moving a script to the toolset, you must immediately append its usage documentation, flag parameters, and purpose to `.agents/toolset/README.md` to ensure future discovery.

## 6. Self-Healing & Memory Loop
When a CLI or script execution returns a non-zero exit code:
1. **State Discovery**: NEVER blindly retry. You must immediately execute a state-discovery command sequence (`ls`, validate paths, check configs) to understand the local state before adjusting parameters.
2. **Intercept & Repair**: Analyze the stderr and state discovery output. Adjust parameters, install missing prerequisites if safe, and re-run (Max **3** attempts matching the global fail-safe rule).
3. **Unified Memory Logging (Decoupled Memory Controller)**: Do not manually read or write raw cache files. You must use the Gateway Pattern via `.agents/toolset/blueprint_tool.py` as a strict CLI API:
   - **On Success**: Run `--log-success --cmd "<cmd>" --error "<err>" --fix "<fix>"` to register a verified fix pathway using an instant, atomic line-append operation to eliminate write-concurrency locks.
   - **On Failure**: Run `--log-fail --cmd "<cmd>" --error "<err>"` to cache a persistent failure state instantly via atomic line-append.
4. **Pre-Flight Check**: Before executing a command, scan the active logs using `--check "<cmd>"`. If a match is found, apply the cached context.
5. **User Recovery for Failed States**: When an environment crash or loop failure (3+ sequential failures) halts execution, the Main Agent must log the failure using `blueprint_tool.py --log-fail`, pause operations, and prompt the user to confirm resolution. Upon confirmation, execute `--purge "<cmd>"` to clear the capability block.

## 7. Delivery Requirements
- **Verification**: Provide clear terminal-based proof or validation logs verifying successful state changes.
- **Artifact Generation**: Deliver a dense, non-conversational Task Summary along with the clean structural changes.
