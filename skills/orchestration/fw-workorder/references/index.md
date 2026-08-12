# Procedures

* [fw-workorder Delivery](delivery.md) - How to fan out code work to pm agents per repo, push and open draft MRs, then update tickets and log time — phases 5 through 8.
* [fw-workorder Intake](intake.md) - How to parse an inbound request into a work order — reading the source, resolving the client and epics, resolving repos, and reconciling dirty working trees before the gate.

# References

* [Depth and Estimate Rubrics](depth-and-estimate.md) - How fw-workorder decides how much machinery to throw at each repo's change, and how the logged time is derived from that depth tier.
* [fw-workorder Skill Routing](skill-routing.md) - Binding dispatch table mapping every fw-workorder phase to the skill or agent that owns it, plus the rule for what to do when a capability is missing.
* [Gear Index](gear-index.md) - The gear-name-to-local-repo index — why directory names can't be used, the JSON contract, dual-remote and forge detection, and how to handle a lookup miss.
