+++
id = "01M5VSBWBK5KZ4H6913F333GGC"
title = "Cookie policy and notice say no cookies; login now sets an HttpOnly session cookie"
type = "bug"
category = "todo"
priority = "medium"
reporter = "a-carten"
created = "2026-10-26T09:41:17Z"
updated = "2026-10-26T09:44:30Z"
scope = ["web/src/pages/CookiePolicy.tsx", "web/src/components/CookieNotice.tsx", "web/tests/unit/CookiePolicy.test.tsx", "web/tests/unit/CookieNotice.test.tsx", "web/src/pages/DataPolicy.tsx", "docs/index.md"]

[[acceptance]]
text = "Given the cookie policy and notice render, then they name the hullbreach_session cookie and no longer claim the site sets no cookies"
bound = true
+++

found while working ~6TZCHZ0: login now sets the strictly-necessary HttpOnly hullbreach_session cookie, so CookiePolicy.tsx ('does not set cookies', 'reloading the page signs you out') and CookieNotice.tsx ('This site sets no cookies') are now false. Reword to name the session cookie (HttpOnly, SameSite=Lax, set at login, cleared at logout, expires with the session) and drop the reload claim; update the tests.
