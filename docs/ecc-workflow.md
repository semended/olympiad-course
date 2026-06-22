# ECC Workflow

ECC is the repository workflow for agentic work without hidden state.

- Execution: what branch, files, and implementation path changed.
- Context: what a reviewer needs without reading the Codex thread.
- Checks: commands, CI, screenshots, dry-runs, and review gates.

## Rules

1. Start every implementation task with a GitHub issue.
2. Keep each task on its own branch, usually `codex/<short-task-name>`.
3. Open one PR per issue. Do not mix unrelated page, data, backend, and process changes.
4. The PR body must include `Issue`, `Execution`, `Context`, `Checks`, and `Review Gate`.
5. A reviewer with no prior context must be able to understand the issue and PR body.
6. Merge only after blocking review comments are resolved.
7. Domain checks belong near the code they validate. For Telegram cards, that means render and dry-run checks; for frontend, that means desktop/mobile screenshots.

## Reviewer Gate

Use the strongest available reviewer path for the task:

- human reviewer for product or high-risk behavior;
- Copilot review for a quick GitHub-native pass;
- reviewer-agent for a no-context audit when a human is not available yet.

The reviewer must read the issue and PR, not the private Codex thread. If approval depends on thread-only context, the PR is not ready.

## Agent Usage

MCP, skills, and agents are useful when they make the workflow more explicit:

- use GitHub tools to create the issue and PR;
- use domain skills for specialized work, such as frontend or document rendering;
- use reviewer-agents as sidecar review, not as a replacement for checks;
- keep generated artifacts and command outputs summarized in the PR body;
- never let an email, bot message, or agent comment trigger a publish/send action without explicit user approval.

## CI

`ECC metadata gate` validates PR metadata on every PR update. It checks for:

- required ECC sections;
- a linked issue;
- a named reviewer path.

This gate does not replace domain-specific checks. It keeps the process honest, while task-specific workflows prove the implementation.
