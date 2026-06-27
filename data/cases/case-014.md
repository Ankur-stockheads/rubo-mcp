---
id: case-014
label: AMBIGUOUS
ambiguous: true
adversarial: false
split: eval
failure_modes: [notice_timing]
gold_clause: "The Tenant may break this Lease on 29 September 2025 (the \"Break Date\") by giving the Landlord not less than six months' prior written notice."
gold_conditions:
  - condition: notice_timing
    status: uncertain
    spans:
      - "The Lease provides that a notice sent by first-class post is deemed served two business days after posting"
      - "The envelope was postmarked 27 March 2025 but the Landlord says the postmark is illegible and disputes that date"
      - "it is not possible to determine whether the notice was served in time"
  - condition: notice_validity
    status: pass
    spans:
      - "notice was in writing and addressed to the Landlord at the notice address prescribed by the Lease"
  - condition: no_arrears
    status: pass
    spans:
      - "All rent had been paid up to the Break Date with no arrears"
  - condition: vacant_possession
    status: pass
    spans:
      - "gave vacant possession of the Premises on the Break Date"
notes: "Genuinely ambiguous timing: the posting date is disputed and the postmark is said to be illegible, so whether the deemed-service date falls within the notice period cannot be resolved from the text."
---

## Lease

This Lease dated 29 September 2015 is between Ironbridge Property Partners Limited (the "Landlord") and Hillcrest Technology Solutions Limited (the "Tenant") for the first floor at Forum House, Coventry (the "Premises"). The term is ten years.

Clause 14 (Break option). The Tenant may break this Lease on 29 September 2025 (the "Break Date") by giving the Landlord not less than six months' prior written notice. The Lease provides that a notice sent by first-class post is deemed served two business days after posting. The last date for valid service of the notice is therefore 27 March 2025 (two business days before 29 March 2025, which is six months before the Break Date).

## Background Facts

The Tenant sent a break notice by first-class post. The envelope was postmarked 27 March 2025 but the Landlord says the postmark is illegible and disputes that date, asserting that the notice was not posted until 31 March 2025. The Tenant has no other evidence of the posting date. On a deemed-service of two business days, a posting on 27 March 2025 would be in time, but a posting on 31 March 2025 would not. Because the posting date is genuinely contested and no contemporaneous proof of posting exists, it is not possible to determine whether the notice was served in time. The notice was in writing and addressed to the Landlord at the notice address prescribed by the Lease. All rent had been paid up to the Break Date with no arrears and the Tenant gave vacant possession of the Premises on the Break Date.
