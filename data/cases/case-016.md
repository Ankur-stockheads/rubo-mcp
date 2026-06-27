---
id: case-016
label: VALID
ambiguous: false
adversarial: false
split: eval
failure_modes: []
gold_clause: "The Tenant may break this Lease on 1 October 2025 (the \"Break Date\") by giving the Landlord not less than six months' prior written notice."
gold_conditions:
  - condition: notice_timing
    status: pass
    spans:
      - "not less than six months' prior written notice"
      - "served written break notice on the Landlord on 25 March 2025, more than six months before the Break Date"
  - condition: notice_validity
    status: pass
    spans:
      - "notice was in writing and sent by recorded delivery to the Landlord's address specified in the Lease for the service of notices"
  - condition: no_arrears
    status: pass
    spans:
      - "all rent had been paid in full to the Break Date with no arrears or other sums outstanding"
  - condition: vacant_possession
    status: pass
    spans:
      - "had removed all racking, stock and personnel from the Unit and returned the keys before noon on the Break Date"
notes: "Clean valid exercise in the industrial/retail sector with a six-month notice period. All conditions satisfied."
---

## Lease

This Lease dated 1 October 2015 is between Pennant Industrial Estates Limited (the "Landlord") and Highfield Distribution Limited (the "Tenant") for Unit 7, Pennant Trade Park, Swindon (the "Premises"). The term is ten years. The Premises comprise a retail warehouse unit with ancillary offices.

Clause 14 (Break right). The Tenant may break this Lease on 1 October 2025 (the "Break Date") by giving the Landlord not less than six months' prior written notice. The break is conditional on the Tenant having paid all rents and other sums due under this Lease up to the Break Date and on giving vacant possession of the Premises on the Break Date.

## Background Facts

The Tenant served written break notice on the Landlord on 25 March 2025, more than six months before the Break Date. The notice was in writing and sent by recorded delivery to the Landlord's address specified in the Lease for the service of notices. By the Break Date all rent had been paid in full to the Break Date with no arrears or other sums outstanding. The Tenant had removed all racking, stock and personnel from the Unit and returned the keys before noon on the Break Date.
