+++
id = "01M5V5GNFS3X1PRMT0QDTQNEZ5"
title = "Profile rating should read current_rating, not the 1200 default"
type = "bug"
category = "todo"
priority = "medium"
reporter = "lognd"
created = "2026-10-26T03:54:23Z"
updated = "2026-10-26T03:58:37Z"
scope = ["src/hullbreach_server/auth/schemas.py", "src/hullbreach_server/services/profile.py"]
+++

found while working T-0054: UserProfile.from_user hardcodes rating 1200; now that RatingChange exists, /me and login profiles should use services.matches.current_rating.
