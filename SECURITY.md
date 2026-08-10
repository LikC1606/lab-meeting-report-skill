# Security Policy

## Supported Versions

Security fixes are applied to the latest released version on the default branch. Older versions may be affected even when a fix can be backported cleanly.

## Reporting A Vulnerability

Report vulnerabilities privately through [GitHub Security Advisories](https://github.com/LikC1606/lab-meeting-report-skill/security/advisories/new).

Do not open a public issue for a vulnerability and do not include credentials, private research data, unpublished results, personal information, or live Feishu/Lark resource URLs in a report.

Useful reports include:

- the affected version or commit;
- the host agent and operating system;
- a minimal synthetic reproduction;
- the potential impact and security boundary crossed;
- any suggested mitigation.

Relevant security concerns include unintended file access, unsafe overwrites, credential exposure, unscoped Feishu/Lark access, identity fallback, destructive remote operations, prompt-driven data exfiltration, and vulnerabilities in repository scripts or CI configuration.

This repository contains an instruction-driven Agent Skill and local validation tools, not a hosted service. Model behavior and host-agent permissions vary, so a report should distinguish repository behavior from behavior introduced by the host environment.

The maintainer will acknowledge a complete report when practical, investigate it, and coordinate disclosure after a fix or documented mitigation is available. Please allow time for validation before public disclosure.
