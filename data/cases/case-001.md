---
id: case-001
label: INVALID
ambiguous: false
adversarial: false
split: eval
failure_modes: [notice_timing]
gold_clause: "The Tenant may terminate this Lease on 24 June 2025 (the \"Break Date\") by giving the Landlord not less than six months' prior written notice."
gold_conditions:
  - condition: notice_timing
    status: fail
    spans:
      - "not less than six months' prior written notice"
      - "served written notice on the Landlord on 5 March 2025"
  - condition: notice_validity
    status: pass
    spans:
      - "addressed to the Landlord at its registered office"
  - condition: no_arrears
    status: pass
    spans:
      - "All rent and other sums due under the Lease have been paid up to and including the Break Date"
  - condition: vacant_possession
    status: pass
    spans:
      - "the Tenant removed all its goods and personnel and returned the keys"
notes: "Classic missed-deadline. Six months' notice expiring on the 24 June 2025 Break Date had to be served by 24 December 2024; notice on 5 March 2025 is far too late. Time is of the essence."
---

## Lease

This Lease is dated 24 June 2015 and is made between Greenfield Estates Limited (the "Landlord") and Aldgate Tea Company Limited (the "Tenant") in respect of Unit 4, Cromwell Business Park, Leeds (the "Premises"). The term is ten years from and including 24 June 2015.

Clause 12 (Tenant's break right). The Tenant may terminate this Lease on 24 June 2025 (the "Break Date") by giving the Landlord not less than six months' prior written notice. Any such notice must be in writing and addressed to the Landlord at its registered office. It is a condition of the Tenant's right to break that, on the Break Date, (a) the Tenant has paid all rent and other sums due under the Lease and (b) the Tenant gives vacant possession of the Premises. Time is of the essence in relation to the notice period.

## Background Facts

The Tenant decided in early 2025 to exercise the break. The Tenant served written notice on the Landlord on 5 March 2025, addressed to the Landlord at its registered office. All rent and other sums due under the Lease have been paid up to and including the Break Date. On the Break Date the Tenant removed all its goods and personnel and returned the keys to the Landlord's managing agent.
