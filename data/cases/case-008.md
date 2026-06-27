---
id: case-008
label: INVALID
ambiguous: false
adversarial: false
split: eval
failure_modes: [notice_validity]
gold_clause: "The Tenant may terminate this Lease on 25 March 2026 (the \"Break Date\") by giving the Landlord not less than six months' prior written notice signed by the Tenant or its duly authorised solicitor."
gold_conditions:
  - condition: notice_timing
    status: pass
    spans:
      - "not less than six months' prior written notice"
      - "telephoned the Landlord's property manager on 10 September 2025"
  - condition: notice_validity
    status: fail
    spans:
      - "written notice signed by the Tenant or its duly authorised solicitor"
      - "telephoned the Landlord's property manager on 10 September 2025 to say that it wished to exercise the break"
      - "No written notice was ever served"
  - condition: no_arrears
    status: pass
    spans:
      - "All sums due under the Lease had been paid in full as at the Break Date"
  - condition: vacant_possession
    status: pass
    spans:
      - "vacated the Premises, removed its belongings and returned the keys on the Break Date"
notes: "Notice given orally by telephone only. The Lease required written notice signed by the Tenant or its solicitor; oral notice is ineffective as a matter of form."
---

## Lease

This Lease dated 25 March 2016 is between Docklands Commercial Estates Limited (the "Landlord") and Tidal Wave Media Limited (the "Tenant") for Unit 3, Harbour Point, Cardiff (the "Premises"). The term is ten years.

Clause 13 (Break right). The Tenant may terminate this Lease on 25 March 2026 (the "Break Date") by giving the Landlord not less than six months' prior written notice signed by the Tenant or its duly authorised solicitor. Notice given by any other method, including by telephone, email or verbally, shall not be effective to exercise the break. Time is of the essence.

## Background Facts

The Tenant wished to exercise the break right and telephoned the Landlord's property manager on 10 September 2025 to say that it wished to exercise the break. The Landlord's property manager said he would pass the message on. No written notice was ever served. All sums due under the Lease had been paid in full as at the Break Date and the Tenant vacated the Premises, removed its belongings and returned the keys on the Break Date.
