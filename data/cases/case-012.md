---
id: case-012
label: INVALID
ambiguous: false
adversarial: false
split: dev
failure_modes: [notice_timing, outstanding_rent]
gold_clause: "The Tenant may break this Lease on 25 March 2025 (the \"Break Date\") by giving the Landlord not less than six months' prior written notice."
gold_conditions:
  - condition: notice_timing
    status: fail
    spans:
      - "not less than six months' prior written notice"
      - "served written notice on 1 November 2024, only four months and twenty-four days before the Break Date"
  - condition: notice_validity
    status: pass
    spans:
      - "notice was in writing and sent to the Landlord at the address for service of notices in the Lease"
  - condition: no_arrears
    status: fail
    spans:
      - "the December 2024 quarter's rent of £15,750 due on 25 December 2024 remained unpaid on the Break Date"
  - condition: vacant_possession
    status: pass
    spans:
      - "gave vacant possession of the Premises on the Break Date and returned all keys"
notes: "Double failure: notice served in November 2024 is less than six months before the 25 March 2025 break date, and a December quarter's rent was unpaid. Either alone would defeat the break."
---

## Lease

This Lease dated 25 March 2015 is between Trident Property Investments Limited (the "Landlord") and Summit Recruitment Limited (the "Tenant") for the second floor at Enterprise House, 22 King Street, Birmingham (the "Premises"). The term is ten years. Rent is payable quarterly in advance on the usual quarter days.

Clause 9 (Break option). The Tenant may break this Lease on 25 March 2025 (the "Break Date") by giving the Landlord not less than six months' prior written notice. The break is conditional on all rent and sums due having been paid up to the Break Date. Time is of the essence.

## Background Facts

The Tenant served written notice on 1 November 2024, only four months and twenty-four days before the Break Date. The notice was in writing and sent to the Landlord at the address for service of notices in the Lease. However, notice was required at least six months before the Break Date, so the last valid date was 25 September 2024. In addition, the December 2024 quarter's rent of £15,750 due on 25 December 2024 remained unpaid on the Break Date. The Tenant gave vacant possession of the Premises on the Break Date and returned all keys.
