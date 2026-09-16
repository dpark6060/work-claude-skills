# Flywheel

* [Flywheel Instance Access](instance-access.md) - Which instances can be inspected live, where the credentials live, how to use them without handling raw keys, and the read-only proxy trick when no key exists.
* [Flywheel SDK Use and Investigation](sdk-investigation.md) - Baseline rules for using the Flywheel SDK (trust the library, use real models) and the hard-won procedure for investigating an unfamiliar or obscure SDK call — version check, grep endpoint paths, distrust declared types, probe enums via 422s.
* [Flywheel SDK Finder / Filter Behaviors](finder-behaviors.md) - Confirmed quoting and filter rules for fw.<containers>.find() — when to quote, never quote parent filters, booleans on parents always return nothing, groups use _id.
* [Flywheel SDK Example Conventions](sdk-example-conventions.md) - How to write Flywheel example code for other people — container IDs must match the 24-hex format, and identifiers go in variables at the top of the example so readers can swap them.
