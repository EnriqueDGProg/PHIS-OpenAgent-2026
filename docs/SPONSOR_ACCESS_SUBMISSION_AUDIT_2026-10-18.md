# Sponsor access and Submission Hub inspection — 2026-10-18
Status: PARTIAL; no sponsor provisioning, no submission created, no code implementation.

## Source actually inspected
Authenticated browser session: https://hackathon.genai.works/submissions and https://hackathon.genai.works/messages. At inspection, only the General Chat channel was selected in the provided messages tab, not each of the four sponsor-support channels. Therefore sponsor thread messages and redemption details were NOT inspected in this pass. Prior complete official ten-section rules and sponsor Markdown overviews continue as authority where relevant.

## Submission Hub findings
- UI displays "0/3 submissions", "No submissions yet", and "Add Submission".
- UI says only one submission expected per team, up to three entries targeting distinct tracks. This appears to differ from official rules wording section 3.2 "Every submission selects exactly one primary track" but is not necessarily contradictory: multiple submissions with distinct tracks may be permissible by portal. Await reconciliation if attempting more than one; our policy is ONE high-quality entry.
- Detailed Add Submission form fields were not visible without clicking. No submission was created, and the team-composition-locking clause §2.2 is a reason to avoid exploratory creation.
- Consequently no verification of metadata.json, video URL versus file upload, link formats, deck upload, or edit-after-submit functionality.

## Support channels — verified descriptions, NOT verified current threads
- Help Meterless: mandatory for every submission; participants told to ask setup and token questions, no secrets.
- Help Zetaris: mandatory for every submission; setup and access support.
- Help Cursor: required development environment for every submission; credits/access questions welcomed.
- Help NVIDIA Tools: help with Nemotron tech or tokens.
- Help Desk previous observed message from Isreal Hosana, dated Oct 15: setup details expected both in HackOS and by email. No observed issuance or confirmed updated credentials.
- Current message tab was General Chat. Four sponsor channels' contents, new answers and access procedures remain NOT VERIFIED.

## Mandatory technology and recommended integration route
Zetaris: real dataset query with bounded SQL and source provenance via a team-scoped account/namespace; instance hostname and permission still missing.
Meterless: meaningful executed World Model (producer record -> persistent state -> later consumer retrieval affects orchestration/explanation), not simply documenting reference architecture. Implementation/license/service specifics still missing.
Cursor: verifiable use as required build environment once competition window opens, credentials/access not confirmed.
NVIDIA: Nemotron best fit for model layer if verified credits; official rule 5.2 conditional, API keys and redemption not confirmed.
No cost-bearing deployment, API secrets, or private health data.

## Revised critical path and GO/NO-GO
P0 19–21 Oct: finish access confirmation through exact sponsor threads/email, preserve written authority, verify rule-compliant starter materials. Avoid code commits before 22 Oct 00:00 UTC.
P0 22 Oct: complete sponsor login/probes and minimum full-stack loop with Zetaris + Meterless + Cursor, scientific source clearance.
P0 23–25 Oct: E2E, evidence UI, scientist gates, adversarial tests.
P0 26 Oct: freeze, reproducible video (1–4 min) and deck, README and real integration explanation.
P0 27 Oct: final validation/submission internally by 20:00 Madrid.
Status: GO for prep. HOLD for sponsor provisioning, submission form field verification, Track 02 reuse answer and authorized build. No feature implementation today.

## Next human interaction
In the CONNECTED browser, open the Help Meterless channel so the browser URL includes that conversation selection; repeat for Help Zetaris, Help Cursor, Help NVIDIA Tools, keeping one tab per selected channel. They cannot all be the same generic /messages link. Then trigger another review. No API keys or credentials should be pasted in chat.
