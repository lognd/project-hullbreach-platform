+++
id = "01M2H5T10SJRRFCSNHGH9AF0ZF"
title = "S07 Sign in from inside the game"
type = "story"
category = "todo"
priority = "medium"
parent = "01M2H5T10DT4023PZH1JHFEWQE"
reporter = "human"
created = "2026-09-15T00:00:00Z"
updated = "2026-09-15T00:00:00Z"
aliases = ["T-0025"]
labels = ["needs-game", "milestone:0.1.0"]
scope = ["src/hullbreach_server/api/auth.py", "src/hullbreach_server/auth/deps.py", "tests/unit/test_auth_game.py"]

[[acceptance]]
text = "given website credentials, when used from the game client, then sign-in succeeds"
bound = false

[[acceptance]]
text = "given a signed-in client, when it joins a match, then the game server can validate the session with the API"
bound = false

[[acceptance]]
text = "given a signed-out client, when building ships offline, then it works, but ranked matches are refused"
bound = false
+++

As a player, I want to sign into my platform account from the game client, so that my matches count toward my rating and my skins appear on my ship.

Open questions:
- Username/password form in the game, or open the website and receive a token (device-code style)?
- How does the game client store the token between launches?
