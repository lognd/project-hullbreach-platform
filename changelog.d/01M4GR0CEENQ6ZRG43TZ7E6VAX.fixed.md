Register returns 409 instead of 500 for a lost unique-insert race and rejects over-long usernames; uniqueness is case-insensitive.
