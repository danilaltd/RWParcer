---
name: one-shot-plan
description: Enforces deterministic one-shot implementation of an entire markdown plan, with mandatory initial reads, substantive code-change gates, and verification only after implementation.
---

# One-Shot Plan Execution Skill

## 0. NON-NEGOTIABLE TOOL ORDER

The first two tool calls are fixed and exclusive.

1. FIRST TOOL CALL — exactly:
   `read_file("skills/one-shot-plan.md")`
2. SECOND TOOL CALL — exactly:
   `read_file(".kilo/plans/1789588994297-database-integration-plan.md")`

Before those two calls, the assistant MUST NOT:
- emit normal conversational text;
- call `bash`, `git`, `edit_file`, `write_file`, search, or any other tool;
- run `git status`, `git diff`, tests, formatters, linters, or discovery commands;
- explain what it is about to do.

Do not rewrite these paths into absolute paths unless the `read_file` tool itself requires it. The required operation is the file read, not path narration.

If either required read fails, retry that same required `read_file` call. Do not substitute `cat`, `sed`, `bash`, or another tool.

After the second required read succeeds, continue with the workflow below.

## 1. No Chat Noise

Do not emit progress commentary between implementation tool calls.

Normal text is allowed only in the final report after the implementation and verification gates are complete.

## 2. Plan Is Read-Only

The following files are instructions and MUST NOT be modified as part of plan execution unless the user explicitly names them as implementation targets:
- `skills/one-shot-plan.md`
- the plan file read in step 0

Never "satisfy" the task by editing the skill or the plan.

## 3. No Trivial Bypasses

A task is NOT considered implemented when a file contains only:
- comments;
- docstrings;
- blank lines;
- formatting-only changes;
- renamed/reordered imports with no behavioral effect;
- TODOs/placeholders;
- dead code that is never reached.

The implementation must change executable behavior: Python statements, methods, types/signatures used by the code, SQL/ORM operations, persistence logic, control flow, schema mappings, or tests required by the plan.

## 4. Build an Internal Implementation Matrix

After the mandatory reads, inspect the existing repository and map every plan requirement to:
- target file;
- existing class/function/method/symbol to change;
- concrete behavior to add/remove;
- affected callers;
- required tests.

Do this internally. Do not print the matrix as chat.

## 5. IMPLEMENT ALL

Implement every step of the plan in the same session.

For every file explicitly marked `(Изменение)` or `(Замена)` in the plan:
- inspect the existing implementation first;
- make the required functional change;
- update its callers/types/imports as needed;
- do not stop after editing one file.

Do not invent completion. A file counts as implemented only when the required behavior exists in executable code.

## 6. IMPLEMENTATION COMPLETENESS GATE

Before running ANY formatter, linter, test, or verification command:

1. Inspect the final diff.
2. For every required implementation file, confirm there is a substantive executable change.
3. Confirm that the diff is not comment/docstring/whitespace-only.
4. Confirm that all plan steps have corresponding code changes.
5. Confirm that neither the skill file nor the plan file was modified.

If any gate fails:
- continue editing;
- do not run tests;
- do not produce a final report.

## 7. TEST/VERIFY BLOCKER

Do NOT run tests, linters, formatters, or verification commands until the Implementation Completeness Gate is satisfied for ALL required code files.

Only then execute, in order:

1. `bash` with `uv run ruff format`
2. `bash` with `uv run ruff check --fix`
3. `bash` with `uv run pytest`

## 8. FIX LOOP

If format, lint, or tests fail:
- inspect the actual error;
- edit the actual code causing the failure;
- re-run the relevant verification;
- do not merely add comments or suppress the error without implementing the required behavior.

After a fix, re-check the substantive diff gate.

## 9. FINAL REPORT

Only after:
- every required plan step is implemented;
- every required implementation file has substantive executable changes;
- the skill and plan files remain unmodified;
- format passes;
- lint passes;
- tests pass;

may you emit a concise final status summary.

The final summary must state:
- implemented;
- verification results;
- any genuinely unresolved issue.

Do not claim a file was changed unless an actual functional diff exists in that file.
