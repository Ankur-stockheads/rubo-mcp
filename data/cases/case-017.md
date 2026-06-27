---
id: case-017
label: INVALID
ambiguous: false
adversarial: false
split: eval
failure_modes: [vacant_possession]
gold_clause: "The Tenant may terminate this Lease on 29 September 2025 (the \"Break Date\") by giving the Landlord not less than six months' prior written notice, provided that vacant possession of the Premises is given on the Break Date."
gold_conditions:
  - condition: notice_timing
    status: pass
    spans:
      - "not less than six months' prior written notice"
      - "served written notice on the Landlord on 20 March 2025, more than six months before the Break Date"
  - condition: notice_validity
    status: pass
    spans:
      - "notice was in writing and addressed to the Landlord at the Landlord's address for service"
  - condition: no_arrears
    status: pass
    spans:
      - "There were no arrears of rent or other sums due on the Break Date"
  - condition: vacant_possession
    status: fail
    spans:
      - "provided that vacant possession of the Premises is given on the Break Date"
      - "a substantial quantity of laboratory equipment, including three freestanding centrifuges and two large refrigeration units, had been left behind in the ground-floor laboratory"
notes: "Vacant possession failed because chattels were left in the Premises. Freestanding equipment is not a landlord's fixture and its presence prevented the Landlord taking unimpeded possession."
---

## Lease

This Lease dated 29 September 2015 is between Greengate Science Park Developments Limited (the "Landlord") and BioTech Innovations Limited (the "Tenant") for Building C, Greengate Science Park, Cambridge (the "Premises"). The term is ten years.

Clause 13 (Tenant's break right). The Tenant may terminate this Lease on 29 September 2025 (the "Break Date") by giving the Landlord not less than six months' prior written notice, provided that vacant possession of the Premises is given on the Break Date. Vacant possession requires removal of all persons, chattels and effects from the Premises.

## Background Facts

The Tenant served written notice on the Landlord on 20 March 2025, more than six months before the Break Date. The notice was in writing and addressed to the Landlord at the Landlord's address for service. There were no arrears of rent or other sums due on the Break Date. The Tenant arranged for its staff to vacate and returned most equipment to storage. However, a substantial quantity of laboratory equipment, including three freestanding centrifuges and two large refrigeration units, had been left behind in the ground-floor laboratory. The Tenant had intended to collect these items the following week but had not done so by the Break Date. The Landlord was therefore unable to use the ground-floor laboratory area.
