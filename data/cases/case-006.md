---
id: case-006
label: VALID
ambiguous: false
adversarial: false
split: eval
failure_modes: []
gold_clause: "The Tenant may determine this Lease on 29 September 2026 (the \"Break Date\") by giving the Landlord not less than twelve months' prior written notice."
gold_conditions:
  - condition: notice_timing
    status: pass
    spans:
      - "not less than twelve months' prior written notice"
      - "served written notice on the Landlord on 15 September 2025, more than twelve months before the Break Date"
  - condition: notice_validity
    status: pass
    spans:
      - "notice was in writing and delivered by hand to the Landlord's address for service of notices as stipulated in the Lease"
  - condition: no_arrears
    status: pass
    spans:
      - "all rent and service charge instalments had been paid in full up to the Break Date with no sums outstanding"
  - condition: vacant_possession
    status: pass
    spans:
      - "removed all furniture, equipment and staff from the Premises and returned the keys to the Landlord's managing agent on the Break Date"
notes: "Clean valid exercise with a twelve-month notice period. All four conditions clearly satisfied."
---

## Lease

This Lease is dated 29 September 2016 and is made between Avondale Property Group Limited (the "Landlord") and Mercer Consulting Services Limited (the "Tenant") in respect of the third floor offices at Sovereign House, 12 Queen Street, Bristol (the "Premises"). The term is ten years from and including 29 September 2016.

Clause 15 (Tenant's break right). The Tenant may determine this Lease on 29 September 2026 (the "Break Date") by giving the Landlord not less than twelve months' prior written notice. The notice must be in writing and addressed to the Landlord at its address for service of notices as stipulated in the Lease. It is a condition of the break that (a) all rent and service charges due have been paid in full up to the Break Date and (b) the Tenant gives vacant possession of the Premises on the Break Date.

## Background Facts

The Tenant served written notice on the Landlord on 15 September 2025, more than twelve months before the Break Date. The notice was in writing and delivered by hand to the Landlord's address for service of notices as stipulated in the Lease. By the Break Date all rent and service charge instalments had been paid in full up to the Break Date with no sums outstanding. The Tenant removed all furniture, equipment and staff from the Premises and returned the keys to the Landlord's managing agent on the Break Date.
