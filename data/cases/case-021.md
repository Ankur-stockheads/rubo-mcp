---
id: case-021
label: INVALID
ambiguous: false
adversarial: false
split: dev
failure_modes: [notice_timing]
gold_clause: "The Tenant may break this Lease on 25 March 2025 (the \"Break Date\") by giving the Landlord not less than three months' prior written notice."
gold_conditions:
  - condition: notice_timing
    status: fail
    spans:
      - "not less than three months' prior written notice"
      - "served written notice on the Landlord on 10 April 2025, which was sixteen days after the Break Date had already passed"
  - condition: notice_validity
    status: pass
    spans:
      - "notice was in writing and addressed to the Landlord at the address for service specified in the Lease"
  - condition: no_arrears
    status: pass
    spans:
      - "All rent and other sums had been paid up to and including 25 March 2025 with no arrears"
  - condition: vacant_possession
    status: pass
    spans:
      - "the Premises had been vacated, cleared and keys returned by 25 March 2025"
notes: "Notice served after the break date had already passed. A notice that post-dates the break date cannot satisfy any required prior notice period and is entirely ineffective."
---

## Lease

This Lease dated 25 March 2016 is between Riverside Commercial Properties Limited (the "Landlord") and Forster & Sons Catering Supplies Limited (the "Tenant") for Unit 2B, Riverside Retail Park, Hull (the "Premises"). The term is nine years.

Clause 10 (Break option). The Tenant may break this Lease on 25 March 2025 (the "Break Date") by giving the Landlord not less than three months' prior written notice. Time is of the essence.

## Background Facts

The Tenant decided to exercise the break right but through an administrative oversight the break notice was not sent until after the break date. The Tenant served written notice on the Landlord on 10 April 2025, which was sixteen days after the Break Date had already passed. The notice was in writing and addressed to the Landlord at the address for service specified in the Lease. All rent and other sums had been paid up to and including 25 March 2025 with no arrears, and the Premises had been vacated, cleared and keys returned by 25 March 2025. However, because the notice was served after the Break Date had passed it was incapable of exercising a break right that could only be exercised by prior notice.
