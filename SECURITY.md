# Security Policy

## Scope

This repository is the platform side of Project Hullbreach: the REST API,
the web frontend, and the database schema behind accounts, sessions, ELO,
match history, and the cosmetic store. Game-client and game-server code
live in the separate game repository and have their own policy.

## Supported versions

Only the `main` branch is supported. There are no release branches.

## Reporting a vulnerability

Please do not open a public issue for a security problem. Email
logan@logandapp.com with a description, steps to reproduce, and the
commit hash you tested against. You will get an acknowledgement within
three days and a fix or a mitigation plan within two weeks for anything
that affects authentication, session handling, or user data.

If you are course staff and find something during grading, the same
address works, or flag it in the grading feedback.

## What we consider in scope

Authentication and session-token handling, authorization between the
Player and Administrator roles, anything that exposes another user's data,
SQL or command injection, and secrets committed to the repository.

## What we do ourselves

Passwords are hashed with an established library, never stored or logged
in plain text. Session tokens are sent in headers only, expire, and are
revoked on logout and account deletion. Every change to `api/auth` or the
session layer requires review from a second team member. `.env` is
gitignored and `.env.example` contains only placeholders. Dependencies are
pinned through `uv.lock` and `package-lock.json`.
