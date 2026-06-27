---
id: case-019
label: VALID
ambiguous: false
adversarial: false
split: eval
failure_modes: []
gold_clause: "The Tenant may determine this Lease on 24 June 2026 (the \"Break Date\") by giving the Landlord not less than nine months' prior written notice."
gold_conditions:
  - condition: notice_timing
    status: pass
    spans:
      - "not less than nine months' prior written notice"
      - "served written break notice on 10 September 2025, more than nine months before the Break Date"
  - condition: notice_validity
    status: pass
    spans:
      - "notice was in writing and sent by first-class post to the Landlord's registered address as required by the Lease"
  - condition: no_arrears
    status: pass
    spans:
      - "had paid all rents and service charges in full to the Break Date, with no sums outstanding"
  - condition: vacant_possession
    status: pass
    spans:
      - "cleared the Premises of all staff, furniture and equipment and returned the keys to the Landlord on the Break Date"
notes: "Clean valid exercise with nine-month notice period. All four conditions clearly satisfied."
---

## Lease

This Lease dated 24 June 2016 is between Westbrook Commercial Property Limited (the "Landlord") and Zenith Legal Services LLP (the "Tenant") for the fifth floor at Tower Bridge House, 14 Lower Thames Street, London (the "Premises"). The term is ten years.

Clause 17 (Tenant's break right). The Tenant may determine this Lease on 24 June 2026 (the "Break Date") by giving the Landlord not less than nine months' prior written notice. The break is conditional on the Tenant having paid all rents, service charges and other sums due under the Lease up to the Break Date and on giving vacant possession of the Premises on the Break Date.

## Background Facts

The Tenant served written break notice on 10 September 2025, more than nine months before the Break Date. The notice was in writing and sent by first-class post to the Landlord's registered address as required by the Lease. By the Break Date the Tenant had paid all rents and service charges in full to the Break Date, with no sums outstanding. The Tenant cleared the Premises of all staff, furniture and equipment and returned the keys to the Landlord on the Break Date.
