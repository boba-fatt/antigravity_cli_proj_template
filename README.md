# Antigravity CLI Project Template

This is a clean project configuration template I built for managing autonomous AI agents running in a local CLI environment. 

The main reason I put this together is that I got sick of prompt bloat and absolute token waste every time I spun up a new project or subagent. It was costing a fortune and burning through context windows because the agent kept repeating mistakes or throwing massive, uncompressed terminal logs into the prompt chat history. This template fixes that by laying down hard rules, a script-first workflow, and a local memory cache so you don't have to constantly re-train the `antigravity_cli` from scratch every single time.

> [!IMPORTANT]
> **Disclaimer:** I am an independent developer. I am not affiliated with Google, the `rtk` team, the `SLIM` author, or any other tools mentioned here. I just use them in my personal setup. This repository does **not** include, install, or download `rtk` or `SLIM`—you have to set those up on your own machine.

---

## 🚀 Quick Start One-Liners

Copy and paste the appropriate command below to download the template into a new directory, navigate into it, and launch `agy` in a single command. (Be sure to replace `YOUR_PROJECT_NAME_HERE` with your desired project name):

### Windows (PowerShell)
```powershell
$proj="YOUR_PROJECT_NAME_HERE"; git clone --depth=1 https://github.com/boba-fatt/antigravity_cli_proj_template $proj && cd $proj; agy
```

### Linux / macOS (Bash)
```bash
proj="YOUR_PROJECT_NAME_HERE"; git clone --depth=1 https://github.com/boba-fatt/antigravity_cli_proj_template "$proj" && cd "$proj" && agy
```

---

## The Folder Structure

```text
.
└── .agents/
    ├── AGENTS.md
    ├── scratchpad/
    │   └── .gitkeep
    ├── toolset/
    │   ├── README.md
    │   └── blueprint_tool.py
    └── memory/
        └── cli_knowledge.jsonl
```
*   **`.agents/AGENTS.md`**: The consolidated, unified ruleset for both the Main Agent and all subagents. Sets workspace boundaries, enforces `rtk` proxying, sets scratchpad vs subagent ceilings, dictates script-first workflows, and details the fail-safe logging sequence. Automatically detected by Antigravity on startup.
*   **`.agents/toolset/blueprint_tool.py`**: A strict CLI API-style controller to handle all storage I/O, deduplication natively in code, ensuring high-speed concurrent JSON Lines processing.

---

## How the Workflow Saves Tokens

Instead of letting an LLM jump straight into complex, multi-turn code edits, the configuration enforces a strict **Hard Operational Ceilings**:

1.  **Discovery**: The agent must check `.agents/toolset/README.md` first[cite: 1]. If a script already exists for the task, it runs that tool directly and stops.
2.  **Scratchpad Testing**: For tasks modifying 1 to 2 files, the agent is strictly bound to the `.agents/scratchpad/` workflow. Subagent creation is forbidden.
3.  **Promotion**: If that script successfully fixes a repeatable or recurring problem, it gets permanently moved into `.agents/toolset/` and documented in the README.
4.  **Escalation**: For complex tasks targeting more than 2 files, the agent bypasses the scratchpad and escalates directly to subagents.

---

## Why this beats RAG for CLI operations

Traditional vector-search RAG sucks for local terminal execution because it suffers from semantic drift and adds a massive token tax.

Instead, this template uses a deterministic, pattern-matched Decoupled Memory Controller (Gateway Pattern) via `.agents/toolset/blueprint_tool.py` against `.agents/memory/cli_knowledge.jsonl`.

*   **Atomic Logging**: Eliminates write-concurrency locks using high-speed `.jsonl` line appends.
*   **State Discovery**: Forces agents to validate local state (e.g., `ls`) rather than blindly retrying failed commands.
*   **Idle Maintenance**: Offloads deduplication and size capping to an idle-time `--cleanup` flag process.

---

## Leveraging External Utilities

This setup is optimized around two solid external toolchains to handle context compression:

### 1. rtk (Rust Token Killer)

An incredible shell proxy that sits between your commands and the agent, automatically compressing long compilation logs and massive terminal error streams by 60-90% before they ever hit the LLM context window.

*   **Site**: [https://www.rtk-ai.app](https://www.rtk-ai.app)
*   **Source**: [https://github.com/rtk-ai/rtk](https://github.com/rtk-ai/rtk)

### 2. SLIM (Context Compressor)

A fantastic low-latency transport layer for Model Context Protocol (MCP) servers. It handles compressed pipeline routing so the agent can check database schema changes or system states without dumping full text logs into the chat window.

*   **Original Author**: Jayanth Chandra (Source: [jayanthchandra/Slim](https://github.com/jayanthchandra/Slim))
*   **Antigravity-Adapted Fork**: [boba-fatt/Slim-Antigravity](https://github.com/boba-fatt/Slim-Antigravity)
    *   *Reworked specifically to locate all active Antigravity plugins and extensions, resolve system-independent path separators, and dynamically interpolate `$extensionPath` during initialization.*

#### Install & Configure Slim for Antigravity:
```bash
# 1. Install the plugin natively via the agy CLI
agy plugin install https://github.com/boba-fatt/Slim-Antigravity

# 2. Run the initialization process
node ~/.gemini/config/plugins/slim/dist/index.js init --cli gemini
```

## Usage

Simply drop the `.agents/` directory directly into the root of any project workspace you spin up. The `.agents/AGENTS.md` file will be automatically discovered, loaded, and followed by Antigravity at system startup.
