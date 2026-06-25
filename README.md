# Antigravity CLI Project Template

This is a clean project configuration template I built for managing autonomous AI agents running in a local CLI environment. 

The main reason I put this together is that I got sick of prompt bloat and absolute token waste every time I spun up a new project or subagent. It was costing a fortune and burning through context windows because the agent kept repeating mistakes or throwing massive, uncompressed terminal logs into the prompt chat history. This template fixes that by laying down hard rules, a script-first workflow, and a local memory cache so you don't have to constantly re-train the `antigravity_cli` from scratch every single time.

> [!IMPORTANT]
> **Disclaimer:** I am an independent developer. I am not affiliated with Google, the `rtk` team, the `SLIM` author, or any other tools mentioned here. I just use them in my personal setup. This repository does **not** include, install, or download `rtk` or `SLIM`—you have to set those up on your own machine.

---

## The Folder Structure

```text
.
├── rules.md
├── workflow.md
├── agents.md
└── .agents/
    ├── rules/
    │   └── antigravity-rtk-rules.md
    ├── scratchpad/
    │   └── .gitkeep
    ├── toolset/
    │   ├── README.md
    │   └── blueprint_tool.py
    └── memory/
        └── cli_knowledge.json
```
*   **`rules.md`**: Global policies for the Main Agent. Sets workspace boundaries, enforces the terminal proxy, and kills infinite loops with a strict 3-strike fail-safe rule.
*   **`workflow.md`**: The actual step-by-step automation blueprint. Forces the agent to try coding a solution before wasting money on subagents.
*   **`agents.md`**: The operational manual for background subagents. Standardizes how they self-heal when a command crashes and dictates how they write clean logs.
*   **`.agents/rules/antigravity-rtk-rules.md`**: Forces the agent to check the local toolset index before it starts code generation or wastes tokens on deep reasoning steps[cite: 1].
*   **`.agents/toolset/blueprint_tool.py`**: A working Python template that demonstrates the exact schema, deduplication mechanics, and cache capping rules the agent needs to follow when moving a script to the permanent toolset[cite: 2].

---

## How the Workflow Saves Tokens

Instead of letting an LLM jump straight into complex, multi-turn code edits, the configuration enforces a strict **Script-First Lifecycle**:

1.  **Discovery**: The agent must check `.agents/toolset/README.md` first[cite: 1]. If a script already exists for the task (e.g., cleaning imports or running a specialized docker test suite), it runs that tool directly and stops[cite: 1].
2.  **Scratchpad Testing**: If no tool exists, the agent is forbidden from launching an autonomous subagent if the task can be handled via code. It must draft and run a self-contained automation script (Python, Bash, or PowerShell) inside `.agents/scratchpad/`.
3.  **Promotion**: If that script successfully fixes a repeatable or recurring problem, it gets permanently moved into `.agents/toolset/` and documented in the README so it can be automatically discovered next time[cite: 1].
4.  **Escalation**: Autonomous subagents are used only as an absolute last resort for deep, conceptual multi-file edits. When spawned, they receive a bare-minimum context injection (only the target files and the specific error string) to protect your wallet.

---

## Why this beats RAG for CLI operations

Traditional vector-search RAG sucks for local terminal execution because it suffers from semantic drift (pulling up a completely unrelated bash error when you have a syntax issue in a powershell script) and adds a massive token/latency tax.

Instead, this template uses a deterministic, pattern-matched JSON table (`.agents/memory/cli_knowledge.json`)[cite: 2]. Subagents maintain it automatically using these exact hygiene laws:

*   **Regex Generalization**: The agent automatically scrubs out machine-specific file paths, commit hashes, or unique IDs and replaces them with clean regex wildcards.
*   **Deduplication**: Repeating an error doesn't create a massive wall of text. It just updates the last-used timestamp and increments an occurrence counter.
*   **Size Capping**: The total array is strictly capped at 100 records. If it fills up, the oldest, lowest-frequency fixes are dropped to ensure pre-flight lookups take nanoseconds and cost zero tokens.

---

## Leveraging External Utilities

This setup is optimized around two solid external toolchains to handle context compression:

### 1. rtk (Rust Token Killer)

An incredible shell proxy that sits between your commands and the agent, automatically compressing long compilation logs and massive terminal error streams by 60-90% before they ever hit the LLM context window.

*   **Site**: [https://www.rtk-ai.app](https://www.rtk-ai.app)
*   **Source**: [https://github.com/rtk-ai/rtk](https://github.com/rtk-ai/rtk)

### 2. SLIM

A fantastic low-latency transport layer for Model Context Protocol (MCP) servers. It handles compressed pipeline routing so the agent can check database schema changes or system states without dumping full text logs into the chat window.

*   **Author**: Jayanth Chandra
*   **Source**: [https://github.com/jayanthchandra/Slim](https://github.com/jayanthchandra/Slim)

---

## Usage

Just drop this directory structure directly into the root of whatever project workspace you are spinning up. Point your main coding agent or IDE configuration to read `rules.md` at system startup to initialize the operational pipeline.
