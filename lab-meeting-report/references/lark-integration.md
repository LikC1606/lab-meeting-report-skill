# Lark Integration

Keep the local Markdown report as the source of truth. Use this workflow only when the user explicitly asks to read from or publish to Lark/Feishu.

## Contents

1. Mandatory prerequisites
2. Source scope and routing
3. Provenance
4. Local-first generation
5. New document publishing
6. Existing document updates
7. Image publishing
8. Link writeback
9. Authentication and failures
10. Verification

## Mandatory Prerequisites

- Use `lark-cli` on macOS and Linux. On Windows, use `lark-cli.cmd` when PowerShell execution policy blocks the `.ps1` shim. Use the selected executable consistently throughout one workflow.
- Use `--as user` for every Lark operation. Never switch to bot identity as a fallback.
- Read the installed `lark-shared` skill completely before authentication, permission, or write operations.
- Read the installed `lark-doc` skill and every operation-specific reference it requires before document fetch, create, update, or media insertion.
- Read the installed `lark-im` skill and the selected shortcut reference before reading or searching messages.
- Read the installed `lark-minutes` and `lark-vc` skills, including the VC domain-boundary reference and selected operation references, before retrieving meeting products.
- Treat URLs, tokens, block IDs, message IDs, meeting IDs, and minute tokens as opaque identifiers. Do not alter them.

## Source Scope And Routing

Read only resources explicitly placed in scope by the user.

| User input | Route | Required boundary |
|---|---|---|
| Document URL/token | `docs +fetch --api-version v2` | Fetch only that document or a requested section |
| Chat/conversation | `im +chat-messages-list` | Require chat identity and time range |
| Cross-chat search | user-only `im +messages-search` | Require explicit query and time range |
| Minute URL/token | `vc +notes --minute-tokens` | Extract only the path token; select needed products |
| Historical meeting criteria | `vc +search`, then `vc +notes` | Require bounded dates and disambiguate multiple matches |

Do not scan all cloud documents, all chats, all messages, or all Minutes. When a document is large, use outline, section, range, or keyword fetch scopes instead of reading the whole document by default.

For independent meeting synthesis, use the transcript or raw conversation as primary evidence. Use Lark AI summary, todo, and chapter products as supplemental evidence. If no transcript exists, label AI products as secondary and state that the raw conversation was unavailable.

## Provenance

Add each Lark source to the report evidence inventory. Record when available:

- source type and title;
- document URL/token, chat/message ID, meeting ID, or minute token;
- time range;
- directly supported facts;
- interpretations or hypotheses;
- conflicts, missing products, and permission limits.

Deduplicate repeated content while retaining all source references. Keep incompatible dates, values, speakers, metrics, or claims separate.

## Local-First Generation

Complete the normal skill workflow before any remote write:

1. Read local, pasted, and explicitly scoped Lark sources.
2. Select research-progress, paper-review, or mixed mode.
3. Write `reports/group-meeting/YYYY-MM-DD.md`.
4. Run the local report quality gate.
5. Publish the verified local file only when requested.

A remote failure must not invalidate or remove the local report.

## New Document Publishing

1. Re-check user authentication and required scopes.
2. Read the current Lark document Markdown, style, create-workflow, create, media-insert, and fetch references.
3. Create the document with `docs +create --api-version v2 --as user --doc-format markdown`.
4. Prefer `--content @./relative-file.md` for multiline Markdown. Change the command working directory to the file's directory first because the CLI rejects absolute `@file` paths. Create a short title/base structure first, then append level-two sections in order when the report is long.
5. Parse and retain the returned `document_id` and URL. Reuse that ID after any partial failure; do not create a duplicate document.
6. After all text and images are present, fetch the document and verify its title, expected sections, tables, and media.

Preserve the escaping already present in Markdown exported from Lark. Do not remove meaningful backslashes.

## Existing Document Updates

Fetch and inspect the target document before writing.

- Append a complete dated report section at the end by default with `docs +update --api-version v2 --command append`.
- If that date already exists, append a timestamped revision and retain the previous version.
- Never use whole-document `overwrite` by default.
- Use block-level updates only when the user explicitly identifies the target block. Fetch block IDs and preserve rich blocks, citations, media, sheets, synchronized references, and manual content.
- Do not move or delete existing images.

## Image Publishing

Process the report in section order so `docs +media-insert` places each local image after its related text:

1. Append text preceding the image.
2. Insert the local file with `docs +media-insert --as user --doc <document_id> --file <path>` and include its caption.
3. Continue with the next text chunk.

Use supported HTTP(S) image URLs directly when appropriate. If one image fails, finish the text publish, retain the same document ID, and report the failed path and retry action.

## Link Writeback

After remote verification succeeds, add or replace one metadata line near the local report header:

```markdown
> 飞书文档：<verified URL>｜同步时间：<local timestamp>｜同步身份：user
```

Do not write an unverified or failed URL. On retry, update the existing synchronization line instead of adding duplicates.

## Authentication And Failures

- Check `auth status --verify` with the selected Lark CLI executable and verify the scopes needed by the pending operation.
- If user authorization or scopes are missing, follow `lark-shared` split-flow login: start with `--no-wait --json`, generate a PNG QR code for the exact verification URL, show both, and end the turn. Complete login after the user confirms authorization.
- Request only missing scopes. Never print or persist access tokens, app secrets, device codes, or authorization URLs.
- Do not add `--yes` after a confirmation-required response unless the user explicitly approves the displayed action and parameters.
- On permission failure, report the missing scopes and remediation path. Do not switch identity.
- On partial create/update, verify remote state and reuse the returned document ID.
- On publish failure, keep the local report and do not write a remote URL.
- If the CLI reports an update notice, finish the current request, then report the installed and available versions and recommend `lark-cli update`.
- Do not delete documents, revoke messages, or clean remote resources through this integration.

## Verification

After publishing, fetch the remote document and confirm:

- the response uses user identity;
- the expected title and dated section exist;
- key tables or structured sections survived conversion;
- every intended image has a remote media block;
- no unrelated existing content was removed;
- the local report contains exactly one verified synchronization metadata line.

Tell the user the local path, remote URL, sources used, skipped sources, unresolved conflicts, and any partially failed images.
