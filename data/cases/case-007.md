---
id: case-007
label: INVALID
ambiguous: false
adversarial: false
split: eval
failure_modes: [notice_validity]
gold_clause: "The Tenant may break this Lease on 24 June 2025 (the \"Break Date\") by giving the Landlord not less than six months' prior written notice."
gold_conditions:
  - condition: notice_timing
    status: pass
    spans:
      - "not less than six months' prior written notice"
      - "served written notice on 15 November 2024, more than six months before the Break Date"
  - condition: notice_validity
    status: fail
    spans:
      - "reversion had been assigned by Hartfield Estates Limited to Cromwell Property Investments plc on 1 March 2024"
      - "The Tenant addressed its notice to Hartfield Estates Limited, unaware that the reversion had been assigned"
  - condition: no_arrears
    status: pass
    spans:
      - "All rent had been paid to the Break Date with no arrears"
  - condition: vacant_possession
    status: pass
    spans:
      - "gave vacant possession of the Premises on the Break Date, removing all effects and returning the keys"
notes: "Notice served on the wrong landlord — the reversion had been assigned and the Tenant served the original (former) landlord. Invalid notice as a matter of law."
---

## Lease

This Lease is dated 24 June 2015 and is made between Hartfield Estates Limited (the "Landlord") and Bluestone Digital Limited (the "Tenant") in respect of Suite 7, Phoenix House, Manchester (the "Premises"). The term is ten years from and including 24 June 2015.

Clause 11 (Tenant's break right). The Tenant may break this Lease on 24 June 2025 (the "Break Date") by giving the Landlord not less than six months' prior written notice. The notice must be in writing and addressed to the current landlord at the address most recently notified to the Tenant. Time is of the essence in relation to the notice period.

## Background Facts

In March 2024 the reversion had been assigned by Hartfield Estates Limited to Cromwell Property Investments plc on 1 March 2024. Cromwell Property Investments plc became the new landlord and notified the Tenant's solicitors of the assignment by letter dated 5 March 2024. The Tenant served written notice on 15 November 2024, more than six months before the Break Date. However, The Tenant addressed its notice to Hartfield Estates Limited, unaware that the reversion had been assigned, and served it at Hartfield Estates Limited's former registered office. Cromwell Property Investments plc received no notice. All rent had been paid to the Break Date with no arrears and the Tenant gave vacant possession of the Premises on the Break Date, removing all effects and returning the keys.
