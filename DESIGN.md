# System Design Document – Alma Lead Intake API

This document outlines the design decisions and trade-offs made in the implementation of the lead intake API for Alma. It also touches on some near-term enhancements.

---

## Design Decisions

### File Uploads
For the sake of this exercise, I chose to use a very simple filesystem-based storage system for user upload storage. Uploaded documents will be saved to a static directory and the API fetches those same documents to display to internal users. This is unsuitable for a production environment since it assumes API workers
live on the same machine as where the particular files are stored, which will only
be guaranteed in a one machine deployment. For a real production system, I would use
S3 or something similar.

For the actual mechanics of the file upload, I opted to use `multipart/form-data` instead of base64 encoding the file and passing the file contents as a string within a JSON payload. Though it makes the API less consistent in that not every endpoint will have an `application/json` content-type anymore, I decided it would be better to avoid the FE overhead of encoding the file to pass to the BE. That overhead would be felt by the submitting user as latency so, to make their process as frictionless as possible, I am adding a bit of friction to the FE developer experience.

### Transactions and async
I'm not immediately familiar with the nuances and subtleties of how database transactions interact with async awaited functions. Within a transaction, I'm not sure how python internals or the db libraries handle this so when I am explicitly starting a transaction for atomicity, I am avoiding awaiting until I can do more research into potential gotchas. See the docstring in the `EmailNotifier` class for an example.

### File structure and organization
Since the scope of this project is relatively small right now, I have the file structure set up in a fairly generic way. Should this app expand, I would consider splitting this up in a more modular way based on concern. Instead of a single schema, a single model file, a single internal/public routes file, etc. I would have an auth subdirectory, a lead subdirectory, etc each with their own routes, models, and crud files.

### Authentication
For the sake of speed, I implemented a really quick and dirty username/password authentication. Hashing of passwords is taken care of by `passlib` using a hard coded secret. This is very bad practice for any production environment. If deploying in prod, I would want to integrate with a secrets store or, at the very least, load secrets via environment vars that are not committed to source control.


## Future Enhancements (in no particular order)
- Split out directory structure by concern.
- Save secret key in a robust secrets store, or at the very least, add it into env vars instead of having it hard coded.
- S3 file upload integration
- Add role based permissions to help determine which group of attorneys should be responsible for intake and, therefore, which should be eligible to receive the submission email.
- Add queueing system to intelligently choose which eligible attorney should receive the alert email instead of a random choice.
- Implement rate limiting in the (assumed) reverse proxy/api gw layer to protect against DDOS
- Add integration with monitoring system like datadog or newrelic
- Add integration with pagerduty or equivalent.
- Add integration with external email provider
- Add query pagination and sorting options into GET/leads/ endpoint
- Add helper decorator or something similar to standardize database transaction usage. Maybe have an easy way to tie a transaction to the lifecycle of the API request as an opt-out thing.
- Add factories for models to make setting up test objects easier
- Add more tests and fill out the test stubs.
- Consolidate the lead CRUD functions into a class for better organization.
- Make User schema and add to LeadSummary schema.
- Move away from SQLite to Postgres/Mysql
- Implement rate limiting
- Define permissions on who can do what. Should any attorney be able to update any lead?
- Add query manager or other wrapper to automatically respect `deleted_at` so we don't have to always remember to query for `deleted_at == False`
