---
id: case-009
label: INVALID
ambiguous: false
adversarial: false
split: dev
failure_modes: [notice_timing]
gold_clause: "The Tenant may determine this Lease on 1 October 2025 (the \"Break Date\") by serving on the Landlord not less than six months' prior written notice."
gold_conditions:
  - condition: notice_timing
    status: fail
    spans:
      - "not less than six months' prior written notice"
      - "served written notice on the Landlord on 2 April 2025"
  - condition: notice_validity
    status: pass
    spans:
      - "served at the Landlord's address for notices by recorded delivery"
  - condition: no_arrears
    status: pass
    spans:
      - "There were no rent arrears on the Break Date"
  - condition: vacant_possession
    status: pass
    spans:
      - "gave vacant possession of the Premises on the Break Date and returned all keys"
notes: "One day late under the corresponding-day rule. Six months before 1 October 2025 is 1 April 2025; notice served on 2 April 2025 misses by one day. Time is of the essence."
---

## Lease

This Lease dated 1 October 2015 is between Pennine Valley Developments Limited (the "Landlord") and Northgate Healthcare Limited (the "Tenant") for the ground floor at 4 Canal Street, Leeds (the "Premises"). The term is ten years.

Clause 8 (Tenant's break option). The Tenant may determine this Lease on 1 October 2025 (the "Break Date") by serving on the Landlord not less than six months' prior written notice. Time is of the essence in relation to service of the break notice.

## Background Facts

The Tenant instructed its solicitors to serve the break notice. The notice was served at the Landlord's address for notices by recorded delivery. However, the solicitors miscounted the notice period: they served written notice on the Landlord on 2 April 2025, which was one day after the last date on which a valid six-month notice could have been served under the corresponding-day rule (that date being 1 April 2025). There were no rent arrears on the Break Date and the Tenant gave vacant possession of the Premises on the Break Date and returned all keys.
