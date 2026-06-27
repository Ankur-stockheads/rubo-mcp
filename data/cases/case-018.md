---
id: case-018
label: INVALID
ambiguous: false
adversarial: false
split: dev
failure_modes: [notice_validity]
gold_clause: "The Tenant may break this Lease on 25 December 2025 (the \"Break Date\") by giving the Landlord not less than six months' prior written notice stating the Break Date."
gold_conditions:
  - condition: notice_timing
    status: pass
    spans:
      - "not less than six months' prior written notice"
      - "served written notice on the Landlord on 10 June 2025, more than six months before the Break Date"
  - condition: notice_validity
    status: fail
    spans:
      - "stating the Break Date"
      - "The notice stated that the Tenant wished to exercise the break option on 25 March 2026, which is not the Break Date under the Lease"
  - condition: no_arrears
    status: pass
    spans:
      - "All rent had been paid to date with no arrears"
  - condition: vacant_possession
    status: pass
    spans:
      - "vacated the Premises and returned the keys on 25 December 2025"
notes: "Notice states the wrong break date (25 March 2026 instead of 25 December 2025). A break notice that mis-states the break date is invalid as it does not satisfy the requirement to state the Break Date correctly."
---

## Lease

This Lease dated 25 December 2015 is between Meridian Estates plc (the "Landlord") and Clearview Solutions Limited (the "Tenant") for Suite 9, Meridian Court, 2 Broad Street, Bristol (the "Premises"). The term is ten years.

Clause 10 (Break option). The Tenant may break this Lease on 25 December 2025 (the "Break Date") by giving the Landlord not less than six months' prior written notice stating the Break Date. The notice must be in writing and must identify the Break Date by reference to the correct date in the Lease.

## Background Facts

The Tenant served written notice on the Landlord on 10 June 2025, more than six months before the Break Date. The notice was in writing and addressed to the Landlord's registered office. However, the notice had been prepared using a template from a previous transaction: The notice stated that the Tenant wished to exercise the break option on 25 March 2026, which is not the Break Date under the Lease. The correct Break Date was 25 December 2025. All rent had been paid to date with no arrears. The Tenant, believing the notice to be valid, vacated the Premises and returned the keys on 25 December 2025.
