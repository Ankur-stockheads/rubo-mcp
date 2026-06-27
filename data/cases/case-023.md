---
id: case-023
label: VALID
ambiguous: false
adversarial: false
split: dev
failure_modes: []
gold_clause: "The Tenant may terminate this Lease on 24 June 2026 (the \"Break Date\") by giving the Landlord not less than six months' prior written notice."
gold_conditions:
  - condition: notice_timing
    status: pass
    spans:
      - "not less than six months' prior written notice"
      - "served written break notice on the Landlord on 20 November 2025, more than six months before the Break Date"
  - condition: notice_validity
    status: pass
    spans:
      - "notice was in writing and sent by special delivery to the Landlord's address for service of notices stated in the Lease"
  - condition: no_arrears
    status: pass
    spans:
      - "all rent and service charge instalments had been paid in full up to the Break Date with no outstanding amounts"
  - condition: vacant_possession
    status: pass
    spans:
      - "removed all its staff, office furniture and IT equipment and returned all sets of keys on the Break Date"
notes: "Clean valid exercise in the office sector with a six-month notice period. All four conditions clearly satisfied."
---

## Lease

This Lease dated 24 June 2016 is between Minster Real Estate Developments plc (the "Landlord") and Kestrel Law LLP (the "Tenant") for the second floor offices at Minster House, 7 Minster Gate, York (the "Premises"). The term is ten years.

Clause 15 (Tenant's break right). The Tenant may terminate this Lease on 24 June 2026 (the "Break Date") by giving the Landlord not less than six months' prior written notice. The break is conditional on the Tenant having paid all rents and service charges due under the Lease up to the Break Date and on giving vacant possession of the Premises on the Break Date.

## Background Facts

The Tenant served written break notice on the Landlord on 20 November 2025, more than six months before the Break Date. The notice was in writing and sent by special delivery to the Landlord's address for service of notices stated in the Lease. By the Break Date all rent and service charge instalments had been paid in full up to the Break Date with no outstanding amounts. The Tenant removed all its staff, office furniture and IT equipment and returned all sets of keys on the Break Date.
