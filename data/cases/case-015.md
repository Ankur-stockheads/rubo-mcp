---
id: case-015
label: AMBIGUOUS
ambiguous: true
adversarial: false
split: dev
failure_modes: [outstanding_rent]
gold_clause: "The Tenant may determine this Lease on 25 March 2026 (the \"Break Date\") by giving not less than nine months' prior written notice, provided that all rent and sums due have been paid on the Break Date."
gold_conditions:
  - condition: notice_timing
    status: pass
    spans:
      - "not less than nine months' prior written notice"
      - "served written notice on the Landlord on 1 June 2025, more than nine months before the Break Date"
  - condition: notice_validity
    status: pass
    spans:
      - "notice was in writing and delivered to the Landlord at its registered address as required by the Lease"
  - condition: no_arrears
    status: uncertain
    spans:
      - "all rent and sums due have been paid on the Break Date"
      - "The Tenant disputes that the sum constitutes 'rent' within the meaning of the break condition, arguing it is a separate contractual obligation"
      - "whether the unpaid service charge sum counts as 'rent and sums due' for the purposes of the break condition is genuinely unclear on the face of the Lease"
  - condition: vacant_possession
    status: pass
    spans:
      - "gave vacant possession of the Premises on the Break Date and returned all keys"
notes: "Genuinely ambiguous no-arrears condition: a disputed service charge reconciliation amount may or may not constitute 'rent and sums due' within the break condition — the Lease does not define the phrase and both readings are arguable."
---

## Lease

This Lease dated 25 March 2017 is between Riviera Property Management plc (the "Landlord") and Cascade Engineering Limited (the "Tenant") for Unit 12, Riverside Industrial Park, Sheffield (the "Premises"). The term is nine years.

Clause 11 (Break option). The Tenant may determine this Lease on 25 March 2026 (the "Break Date") by giving not less than nine months' prior written notice, provided that all rent and sums due have been paid on the Break Date. The Lease does not define "sums due" for the purposes of the break condition.

## Background Facts

The Tenant served written notice on the Landlord on 1 June 2025, more than nine months before the Break Date. The notice was in writing and delivered to the Landlord at its registered address as required by the Lease. The Tenant gave vacant possession of the Premises on the Break Date and returned all keys. However, a service charge reconciliation for the year ending 31 December 2025 produced a balancing sum of £3,200 claimed by the Landlord. The Tenant disputes that the sum constitutes 'rent' within the meaning of the break condition, arguing it is a separate contractual obligation not falling within the phrase "rent and sums due" in the break clause. The Landlord contends it is plainly a sum due under the Lease. Because the Lease does not define the phrase, whether the unpaid service charge sum counts as 'rent and sums due' for the purposes of the break condition is genuinely unclear on the face of the Lease.
