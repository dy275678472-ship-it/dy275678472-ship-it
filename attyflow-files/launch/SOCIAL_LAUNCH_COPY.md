# Attyflow Launch — Social Copy (Product Hunt Day)

Copy-paste blocks for LinkedIn and Reddit. Replace `[YOUR_NAME]` where noted.

---

## LinkedIn — Launch Post (long)

**Hook + story**

Today we're launching **Attyflow** on Product Hunt 🚀

Contract review shouldn't start with a blank ChatGPT prompt.

Attyflow scores risky clauses, explains the loophole, and drafts negotiation-ready redlines — inside the workflow US attorneys already use: **Microsoft Word**.

**What you can try free (no credit card):**
→ Paste any NDA / indemnity / liability clause
→ Get a risk score + issue summary + redline language
→ 3 free audits in the sandbox

Built for solo attorneys, boutiques, and legal ops teams reviewing NDAs, MSAs, and vendor paper.

**Links:**
• Try free: https://attyflow.com/taskpane.html
• Launch page: https://attyflow.com/launch/
• Sample report: https://attyflow.com/sample-redline-report

Would love feedback from transactional lawyers and legal ops — what clause would you test first?

#LegalTech #ContractReview #LegalAI #ProductHunt #LawFirm

---

## LinkedIn — Short post (reshare)

We just launched Attyflow on Product Hunt — AI contract risk review + redlines for lawyers, Word-native.

3 free clause audits, no card: https://attyflow.com/taskpane.html

Feedback from attorneys & legal ops welcome 🙏

#LegalTech #ProductHunt

---

## LinkedIn — Comment templates (for supporters)

**Template A (colleague):**
Congrats on the launch! I tested the NDA checker on a one-way confidentiality clause — the risk framing was clearer than a generic AI summary. Worth a look for transactional teams.

**Template B (legal ops):**
Useful for vendor MSA triage — paste the liability cap, get a structured issue list before counsel review. Free sandbox is a low-friction way to evaluate.

**Template C (founder reply to comments):**
Thanks [Name] — great point on [topic]. We built Attyflow for first-pass triage, not replacing partner sign-off. Would love to see how it handles your [NDA/MSA] clause if you're open to trying the sandbox.

---

## Reddit — r/legaltech

**Title:**
`[Launch] Attyflow — AI clause risk scoring + redlines for Word (3 free audits, no card)`

**Body:**

Hi r/legaltech — I'm the maker of **Attyflow**, launching today on Product Hunt.

**Problem:** Generic AI chat isn't structured enough for contract triage. Associates still spend too long on first-pass NDA/MSA markup.

**What Attyflow does:**
- Paste a clause → risk score + level + plain-English issue explanation
- Negotiation-ready redline suggestion (attorney review required)
- Buyer / seller / mutual position toggle
- Word taskpane + browser sandbox

**Free to try:** https://attyflow.com/taskpane.html (3 audits, no credit card)

**Not legal advice** — software workflow only. We don't train on submitted contract text (see security page).

I'd genuinely appreciate blunt feedback:
1. Is the redline output useful enough to edit, or too generic?
2. Which clause type would you test first — NDA, indemnity, or liability cap?

Product Hunt: [add PH link when live]

---

## Reddit — r/lawyers (use only if sub rules allow product posts)

**Title:**
`Tool for first-pass contract clause review (free sandbox) — looking for attorney feedback`

**Body:**

Transactional attorneys — I built a focused contract review tool (not a general legal chatbot).

You paste a clause, pick buyer/seller/mutual, and get a risk score + issue explanation + suggested redline language. Works in browser or Word.

Free sandbox (3 audits): https://attyflow.com/taskpane.html

Looking for honest feedback on whether the output is useful for real negotiation prep. Not a law firm, not legal advice.

---

## Reddit — Maker comment (first reply on your post)

Thanks for checking this out — I'm around all day for questions.

Quick tips for testing:
1. Use a real indemnity or liability cap from recent counterparty paper
2. Toggle buyer vs seller before running the audit
3. Compare output to your internal playbook fallback

Free NDA checker (no signup): https://attyflow.com/tools/nda-clause-review/

Happy to hear what's missing for your workflow.

---

## Posting schedule (PH day, UTC)

| Time (UTC) | Action |
|------------|--------|
| T-0 07:00 | PH goes live (if targeting 12:01 AM PT = 07:01 UTC) |
| T+0 07:15 | LinkedIn long post |
| T+0 07:30 | Reddit r/legaltech post |
| T+0 08:00 | Reply to every PH comment within 15 min |
| T+2 09:00 | LinkedIn short reshares from personal network |
| T+4 11:00 | Reddit maker comment updates / answer questions |
| T+8 15:00 | Share anonymized case study link in PH comments |
| End of day | Run `attyflow_ph_monitor.py --save` |

---

## Monitoring (launch day)

```bash
# Live dashboard every 5 minutes
sudo python3 /var/www/attyflow/tools/attyflow_ph_monitor.py --watch 300

# End-of-day report
sudo python3 /var/www/attyflow/tools/attyflow_ph_monitor.py --date $(date -u +%Y-%m-%d) --save
```

Reports saved to: `/var/www/attyflow/reports/ph-launch-YYYY-MM-DD.txt`
