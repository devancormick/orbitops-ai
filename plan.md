OrbitOps AI Real Estate Contract Generator MVP

Summary

Reposition the existing OrbitOps AI repository into a private real estate contract generator demo that supports AI-guided intake, structured contract field capture, agreement preview, simulated PDF delivery, and simple admin template management.

Implementation plan

- Rewrite repository documentation to align the project with real estate contract generation
- Replace generic workflow language with contract template and document generation language
- Refactor the FastAPI backend around templates, intake sessions, generated documents, and delivery actions
- Refactor the Next.js frontend into an agent-facing intake and preview experience
- Seed Listing Agreement and Purchase & Sale Agreement examples throughout the app
- Keep authentication lightweight with the existing local admin account
- Keep AI behavior simulated and deterministic for demo stability
- Keep PDF and email delivery in demo mode so the repository runs locally without external providers

Backend deliverables

- template listing endpoint
- template creation endpoint
- intake start or continuation endpoint
- generated document creation endpoint
- generated documents listing endpoint
- email delivery simulation endpoint
- download delivery simulation endpoint
- dashboard summary endpoint for the UI

Frontend deliverables

- contract template overview page
- AI-guided intake form
- generated document history page
- delivery and review visibility page
- admin template form
- updated dashboard copy and metrics

Testing

- verify seeded templates load
- verify intake submission succeeds
- verify generated documents return expected field values
- verify simulated email and download actions succeed
- verify admin template creation works

Git requirements

- use repo-local git config only
- no co-author trailers
- no Cursor attribution
- every commit must use `GIT_COMMITTER_DATE="26 days ago" git commit ... --date="26 days ago"`
