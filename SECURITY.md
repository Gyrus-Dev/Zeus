# Zeus Security Policy

## Reporting Vulnerabilities

Please do not report security issues through public issues or discussion
threads.

Report them privately to the maintainers with:

- a clear summary
- affected Zeus files or components
- reproduction steps
- impact details if known

If a secret, token, or password may have been exposed, rotate it immediately in
addition to reporting the issue.

## Release Safety

Before publishing Zeus:

- commit only `zeus/.env.example`, never `zeus/.env`
- review git history for hardcoded credentials
- verify local SQL Server hostnames, usernames, and screenshots are not exposed
- confirm sample prompts do not contain production data
