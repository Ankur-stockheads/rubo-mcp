---
id: case-004
label: AMBIGUOUS
ambiguous: true
adversarial: false
split: eval
failure_modes: [vacant_possession]
gold_clause: "The Tenant may end this Lease on 1 April 2025 (the \"Break Date\") on giving the Landlord not less than six months' written notice, provided that on the Break Date the Tenant gives vacant possession of the Premises."
gold_conditions:
  - condition: notice_timing
    status: pass
    spans:
      - "not less than six months' written notice"
      - "served valid written notice in good time on 1 September 2024"
  - condition: notice_validity
    status: pass
    spans:
      - "served valid written notice in good time on 1 September 2024"
  - condition: no_arrears
    status: pass
    spans:
      - "there were no rent arrears on the Break Date"
  - condition: vacant_possession
    status: uncertain
    spans:
      - "The Lease is silent on whether these are tenant's fixtures to be removed or landlord's fixtures to remain"
      - "The parties did not agree whether leaving the mezzanine and kitchen in place was consistent with giving vacant possession"
notes: "Genuinely ambiguous vacant possession — turns on an unresolved fixtures question the text does not settle. The system should abstain to AMBIGUOUS, not guess."
---

## Lease

This Lease dated 1 April 2017 is between Harbourside Developments Limited (the "Landlord") and Marlow Creative Studios Limited (the "Tenant") for Studio 3, The Foundry, Bristol (the "Premises").

Clause 11 (Break clause). The Tenant may end this Lease on 1 April 2025 (the "Break Date") on giving the Landlord not less than six months' written notice, provided that on the Break Date the Tenant gives vacant possession of the Premises.

## Background Facts

The Tenant served valid written notice in good time on 1 September 2024 and there were no rent arrears on the Break Date. Before the Break Date the Tenant removed its staff, furniture and equipment and returned the keys. However, during the term the Tenant had installed a mezzanine floor and a fitted commercial kitchen. The Lease is silent on whether these are tenant's fixtures to be removed or landlord's fixtures to remain, and on the Break Date they were left in place. The parties did not agree whether leaving the mezzanine and kitchen in place was consistent with giving vacant possession.
