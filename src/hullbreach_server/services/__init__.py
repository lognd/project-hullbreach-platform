"""Service layer: database-backed read models the API routes compose.

Routes stay thin (auth, status codes, logging); a service turns ORM rows
into the response models the web client's contract names.
"""
