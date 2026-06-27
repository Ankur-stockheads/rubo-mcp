---
id: case-002
label: VALID
ambiguous: false
adversarial: false
split: eval
failure_modes: []
gold_clause: "The Tenant may break this Lease on 25 December 2024 (the \"Break Date\") on giving the Landlord not less than six months' prior written notice."
gold_conditions:
  - condition: notice_timing
    status: pass
    spans:
      - "not less than six months' prior written notice"
      - "served written break notice on the Landlord on 1 May 2024, more than six months before the Break Date"
  - condition: notice_validity
    status: pass
    spans:
      - "sent to the Landlord at the address given in the Lease for service of notices"
  - condition: no_arrears
    status: pass
    spans:
      - "had paid the rents reserved by the Lease up to the Break Date and had no arrears"
  - condition: vacant_possession
    status: pass
    spans:
      - "removed all of its furniture and equipment, left no one in occupation, and returned all keys"
notes: "Textbook valid exercise — every condition precedent clearly satisfied."
---

## Lease

This Lease is dated 25 December 2014 between Northgate Property Holdings Limited (the "Landlord") and Pennine Software Limited (the "Tenant") for the second floor offices at 18 Wellington Street, Sheffield (the "Premises"). The contractual term is ten years.

Clause 9 (Break option). The Tenant may break this Lease on 25 December 2024 (the "Break Date") on giving the Landlord not less than six months' prior written notice. The break is conditional on the Tenant (i) having paid the rents reserved by the Lease up to the Break Date and (ii) giving vacant possession of the Premises on the Break Date.

## Background Facts

The Tenant served written break notice on the Landlord on 1 May 2024, more than six months before the Break Date. The notice was in writing and sent to the Landlord at the address given in the Lease for service of notices. By the Break Date the Tenant had paid the rents reserved by the Lease up to the Break Date and had no arrears. The Tenant vacated the Premises before the Break Date, removed all of its furniture and equipment, left no one in occupation, and returned all keys to the Landlord.
