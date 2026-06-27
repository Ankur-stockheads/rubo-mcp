---
id: case-020
label: INVALID
ambiguous: false
adversarial: false
split: eval
failure_modes: [outstanding_rent]
gold_clause: "The Tenant may terminate this Lease on 29 September 2025 (the \"Break Date\") by giving the Landlord not less than six months' prior written notice, provided all rents due and payable under this Lease have been paid on or before the Break Date."
gold_conditions:
  - condition: notice_timing
    status: pass
    spans:
      - "not less than six months' prior written notice"
      - "served valid written notice on the Landlord on 15 March 2025, more than six months before the Break Date"
  - condition: notice_validity
    status: pass
    spans:
      - "addressed to the Landlord at the notice address in the Lease"
  - condition: no_arrears
    status: fail
    spans:
      - "all rents due and payable under this Lease have been paid on or before the Break Date"
      - "two months' worth of rent instalments, totalling £14,400, had not been paid and remained outstanding on the Break Date"
  - condition: vacant_possession
    status: pass
    spans:
      - "gave vacant possession on the Break Date and returned all keys"
notes: "Clear rent arrears: two months' rent instalments were unpaid on the break date. The condition requires all rents due and payable to have been paid on or before the Break Date."
---

## Lease

This Lease dated 29 September 2015 is between Clifton Property Developments plc (the "Landlord") and Urban Fitness Holdings Limited (the "Tenant") for the ground floor studio at Clifton Court, 33 Park Street, Bristol (the "Premises"). The term is ten years. Rent is payable monthly in advance on the first of each month.

Clause 12 (Tenant's break right). The Tenant may terminate this Lease on 29 September 2025 (the "Break Date") by giving the Landlord not less than six months' prior written notice, provided all rents due and payable under this Lease have been paid on or before the Break Date.

## Background Facts

The Tenant served valid written notice on the Landlord on 15 March 2025, more than six months before the Break Date. The notice was in writing and addressed to the Landlord at the notice address in the Lease. However, during a period of financial difficulty the Tenant had fallen into arrears: two months' worth of rent instalments, totalling £14,400, had not been paid and remained outstanding on the Break Date. The Tenant gave vacant possession on the Break Date and returned all keys.
