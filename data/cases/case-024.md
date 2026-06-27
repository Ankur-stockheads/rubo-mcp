---
id: case-024
label: INVALID
ambiguous: false
adversarial: false
split: dev
failure_modes: [notice_validity, vacant_possession]
gold_clause: "The Tenant may determine this Lease on 29 September 2026 (the \"Break Date\") by giving the Landlord not less than twelve months' prior written notice addressed to the Landlord at its registered office."
gold_conditions:
  - condition: notice_timing
    status: pass
    spans:
      - "not less than twelve months' prior written notice"
      - "served a break notice on 20 September 2025, more than twelve months before the Break Date"
  - condition: notice_validity
    status: fail
    spans:
      - "addressed to the Landlord at its registered office"
      - "notice was sent to the Landlord's property management agents at their offices in Exeter rather than to the Landlord's registered office"
  - condition: no_arrears
    status: pass
    spans:
      - "All rent had been paid to the Break Date with no arrears outstanding"
  - condition: vacant_possession
    status: fail
    spans:
      - "the Tenant's licensee, a concession stand operator, remained trading from a kiosk in the entrance lobby on the Break Date"
notes: "Double failure: notice sent to the wrong address (agents rather than the Landlord's registered office as required) and vacant possession not given because a licensee remained in occupation."
---

## Lease

This Lease dated 29 September 2014 is between Abbot's Gate Retail Developments plc (the "Landlord") and Victoria Square Retail Limited (the "Tenant") for the anchor retail unit at Abbot's Gate Shopping Centre, Exeter (the "Premises"). The term is twelve years.

Clause 18 (Tenant's break right). The Tenant may determine this Lease on 29 September 2026 (the "Break Date") by giving the Landlord not less than twelve months' prior written notice addressed to the Landlord at its registered office. The break is conditional on vacant possession of the Premises being given on the Break Date.

## Background Facts

The Tenant served a break notice on 20 September 2025, more than twelve months before the Break Date. However, the notice was sent to the Landlord's property management agents at their offices in Exeter rather than to the Landlord's registered office as required by the Lease. All rent had been paid to the Break Date with no arrears outstanding. On the Break Date the Tenant had vacated and cleared most of the retail unit; however, the Tenant's licensee, a concession stand operator, remained trading from a kiosk in the entrance lobby on the Break Date under an informal licence granted by the Tenant. The Tenant had failed to arrange for the licensee to vacate before the Break Date.
