---
id: case-011
label: INVALID
ambiguous: false
adversarial: false
split: eval
failure_modes: [vacant_possession]
gold_clause: "The Tenant may end this Lease on 29 September 2025 (the \"Break Date\") by giving the Landlord not less than nine months' prior written notice, conditional on the Tenant giving vacant possession of the Premises on the Break Date."
gold_conditions:
  - condition: notice_timing
    status: pass
    spans:
      - "not less than nine months' prior written notice"
      - "served written notice on 20 November 2024, more than nine months before the Break Date"
  - condition: notice_validity
    status: pass
    spans:
      - "notice was in writing and delivered to the Landlord at the address stated in the Lease"
  - condition: no_arrears
    status: pass
    spans:
      - "No arrears of rent were outstanding on the Break Date"
  - condition: vacant_possession
    status: fail
    spans:
      - "conditional on the Tenant giving vacant possession of the Premises on the Break Date"
      - "a subtenant, Gamma Print Limited, remained in occupation of the rear mezzanine under a sublease that had not been surrendered"
notes: "Vacant possession failed because a subtenant remained in occupation. Physical clearance requires removal of all occupiers; an extant underlease prevents vacant possession."
---

## Lease

This Lease dated 29 September 2016 is between Holborn Property Holdings plc (the "Landlord") and Sterling Distribution Limited (the "Tenant") for Unit 9, Meridian Business Park, Leicester (the "Premises"). The term is nine years.

Clause 12 (Break option). The Tenant may end this Lease on 29 September 2025 (the "Break Date") by giving the Landlord not less than nine months' prior written notice, conditional on the Tenant giving vacant possession of the Premises on the Break Date. For the avoidance of doubt, vacant possession requires the Tenant to procure the removal of any undertenant or licensee.

## Background Facts

The Tenant served written notice on 20 November 2024, more than nine months before the Break Date. The notice was in writing and delivered to the Landlord at the address stated in the Lease. No arrears of rent were outstanding on the Break Date. However, at the time of the break a subtenant, Gamma Print Limited, remained in occupation of the rear mezzanine under a sublease that had not been surrendered. The Tenant had intended to agree a surrender with Gamma Print Limited but negotiations broke down. The Landlord was therefore unable to take vacant possession of the whole of the Premises on the Break Date.
