# System Design Document – Alma Lead Intake API

This document outlines the design decisions and trade-offs made in the implementation of the lead intake API for Alma. It also touches on some near-term enhancements.

---

## Design Decisions

### File Uploads

### Transactions

---

## Authentication

- Internal routes require JWT-based auth via `/internal/token`
- Passwords are hashed using `pbkdf2_sha256` via `passlib`
- Seed script creates a hardcoded internal user (`attorney` / `supersecure`)


## Future Enhancements
- Save secret key in a robust secrets store, or at the very least, add it into env vars instead of having it hard coded.
- S3 file upload integration
- Add role based permissions to help determine which group of attorneys should be responsible for intake and, therefore, which should be eligible to receive the submission email.
- Add queueing system to intelligently choose which eligible attorney should receive the alert email instead of a random choice.
- Implement rate limiting in the (assumed) reverse proxy/api gw layer to protect against DDOS

