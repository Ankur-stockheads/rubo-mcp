---
id: case-013
label: VALID
ambiguous: false
adversarial: false
split: eval
failure_modes: []
gold_clause: "The Tenant may terminate this Lease on 24 June 2025 (the \"Break Date\") by giving the Landlord not less than six months' prior written notice."
gold_conditions:
  - condition: notice_timing
    status: pass
    spans:
      - "not less than six months' prior written notice"
      - "served written break notice on the Landlord on 3 December 2024, more than six months before the Break Date"
  - condition: notice_validity
    status: pass
    spans:
      - "notice was in writing and addressed to the Landlord at the address for service stated in the Lease"
  - condition: no_arrears
    status: pass
    spans:
      - "The break clause imposes no rent condition and the Tenant had in any event paid all rent to the Break Date with no sums outstanding"
  - condition: vacant_possession
    status: pass
    spans:
      - "The break clause imposes no vacant possession condition and the Tenant had vacated, removed all its contents and returned the keys on the Break Date"
notes: "Break conditional only on notice — no rent or VP conditions imposed by the Lease. Notice given in good time; all four conditions pass (no_arrears and vacant_possession pass both because no condition is imposed and because the facts show nothing outstanding or left behind)."
---

## Lease

This Lease dated 24 June 2015 is between Lakeside Commercial Investments Limited (the "Landlord") and Redwood Advisory Partners Limited (the "Tenant") for Suite 4A, Lakeside House, Reading (the "Premises"). The term is ten years.

Clause 10 (Break right). The Tenant may terminate this Lease on 24 June 2025 (the "Break Date") by giving the Landlord not less than six months' prior written notice. The break right is exercisable by notice only and is not conditional on payment of rent, provision of vacant possession, or any other condition beyond service of a valid notice in the required time.

## Background Facts

The Tenant served written break notice on the Landlord on 3 December 2024, more than six months before the Break Date. The notice was in writing and addressed to the Landlord at the address for service stated in the Lease. The break clause imposes no rent condition and the Tenant had in any event paid all rent to the Break Date with no sums outstanding. The break clause imposes no vacant possession condition and the Tenant had vacated, removed all its contents and returned the keys on the Break Date.
