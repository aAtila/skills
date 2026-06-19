# Output Template

## Truth Hierarchy

When contradictions arise, resolve against this priority stack:

1. **Brand guidelines / style guide** — Canonical baseline, always wins
2. **Core services or product documentation** — Authoritative for operational claims
3. **Neither exists** → Flag all variants for manual verification

---

## Report Structure

Group findings by claim type. Begin with 🔴 Critical, then 🟡 High, then 🟢 Medium.

### Finding Template

```
### [Claim Type]: [Brief descriptor]

**Priority:** 🔴/🟡/🟢  
**Confidence:** ⚠️/❓/📝

**Locations:**
- `[page/URL/file path]`: "[exact claim text]"
- `[page/URL/file path]`: "[conflicting claim text]"

**Truth Check:**
- Brand guidelines say: [value or "not addressed"]
- Core documentation say: [value or "not addressed"]

**Recommendation:** [Standardize to X / Flag for verification / Defer to [source]]
```

---

## Completion Checklist

Before finalizing report:

- [ ] All pages/routes in scope processed
- [ ] Every claim type cross-referenced
- [ ] Critical-priority items at top of report
- [ ] Ambiguous cases marked for human review
- [ ] No findings rely on uncertain interpretation

---

## Example Finding

### Team Size: Conflicting employee counts

**Priority:** 🟢 Medium  
**Confidence:** ⚠️ Definite

**Locations:**
- `/about-us`: "Our team of 50 dedicated professionals"
- `/careers`: "Join our growing team of 35 specialists"

**Truth Check:**
- Brand guidelines say: not addressed
- Core documentation say: not addressed

**Recommendation:** Flag for verification — confirm actual headcount with HR
