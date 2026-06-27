---
id: case-010
label: INVALID
ambiguous: false
adversarial: false
split: eval
failure_modes: [outstanding_rent]
gold_clause: "The Tenant may break this Lease on 1 February 2026 (the \"Break Date\") by giving the Landlord not less than six months' prior written notice, provided that on the Break Date all rent and other sums payable under this Lease have been paid."
gold_conditions:
  - condition: notice_timing
    status: pass
    spans:
      - "not less than six months' prior written notice"
      - "served written break notice on the Landlord on 1 July 2025"
  - condition: notice_validity
    status: pass
    spans:
      - "notice was in writing and addressed to the Landlord at the address prescribed in the Lease"
  - condition: no_arrears
    status: fail
    spans:
      - "all rent and other sums payable under this Lease have been paid"
      - "a full quarter's rent of £22,500 fell due on 25 December 2025 and remained wholly unpaid on the Break Date"
  - condition: vacant_possession
    status: pass
    spans:
      - "gave vacant possession of the Premises on the Break Date"
notes: "Mid-quarter break date. A full quarter's rent fell due on 25 December 2025 before the 1 February 2026 break date and was wholly unpaid. No apportionment — the full sum was due and unpaid (cf. PCE Investors v Channel Four Television)."
---

## Lease

This Lease dated 1 February 2016 is between Silverstone Real Estate Limited (the "Landlord") and Apex Financial Services Limited (the "Tenant") for the fourth floor at Exchange Chambers, 45 Old Market Square, Nottingham (the "Premises"). The term is ten years. Rent is payable quarterly in advance on the usual quarter days.

Clause 16 (Tenant's break right). The Tenant may break this Lease on 1 February 2026 (the "Break Date") by giving the Landlord not less than six months' prior written notice, provided that on the Break Date all rent and other sums payable under this Lease have been paid. Time is of the essence.

## Background Facts

The Tenant served written break notice on the Landlord on 1 July 2025, well within the required notice period. The notice was in writing and addressed to the Landlord at the address prescribed in the Lease. However, the Break Date fell between two quarter days: a full quarter's rent of £22,500 fell due on 25 December 2025 and remained wholly unpaid on the Break Date of 1 February 2026. The Tenant had wrongly assumed that only the apportioned daily rent up to 1 February 2026 was required. The Tenant gave vacant possession of the Premises on the Break Date.
