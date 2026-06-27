---
id: case-003
label: INVALID
ambiguous: false
adversarial: false
split: eval
failure_modes: [vacant_possession]
gold_clause: "The Tenant may determine this Lease on 29 September 2024 (the \"Break Date\") by giving not less than nine months' prior written notice to the Landlord."
gold_conditions:
  - condition: notice_timing
    status: pass
    spans:
      - "not less than nine months' prior written notice"
      - "gave written notice to the Landlord on 1 December 2023, more than nine months before the Break Date"
  - condition: notice_validity
    status: pass
    spans:
      - "at the Landlord's notice address"
  - condition: no_arrears
    status: pass
    spans:
      - "There were no arrears of rent on the Break Date"
  - condition: vacant_possession
    status: fail
    spans:
      - "a substantial quantity of heavy steel racking remained bolted to the floor and the Tenant's contractors were still on site"
      - "The Landlord was not able to take unimpeded possession of the Premises on the Break Date"
notes: "Vacant possession defeated by chattels and people left on site (cf. NYK Logistics v Ibrend; Capitol Park Leeds v Global Radio). Physical clearance, not condition, is the test."
---

## Lease

This Lease dated 29 September 2016 is between Calder Industrial Estates Limited (the "Landlord") and Riverside Logistics Limited (the "Tenant") for Warehouse B, Calder Vale Trading Estate, Wakefield (the "Premises").

Clause 14 (Tenant's option to determine). The Tenant may determine this Lease on 29 September 2024 (the "Break Date") by giving not less than nine months' prior written notice to the Landlord. The Tenant's right to determine is conditional upon the Tenant giving vacant possession of the whole of the Premises to the Landlord on the Break Date and upon there being no arrears of rent on the Break Date.

## Background Facts

The Tenant gave written notice to the Landlord on 1 December 2023, more than nine months before the Break Date, at the Landlord's notice address. There were no arrears of rent on the Break Date. However, on the Break Date the Tenant had not finished clearing the warehouse: a substantial quantity of heavy steel racking remained bolted to the floor and the Tenant's contractors were still on site carrying out strip-out works, with the Tenant's security guard controlling access. The Landlord was not able to take unimpeded possession of the Premises on the Break Date.
