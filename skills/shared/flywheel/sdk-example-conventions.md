---
type: Reference
title: Flywheel SDK Example Conventions
description: How to write Flywheel example code for other people — container IDs must match the 24-hex format, and identifiers go in variables at the top of the example so readers can swap them.
tags: [flywheel, sdk, examples, container-id]
timestamp: 2026-09-16T00:00:00Z
---

# Flywheel SDK Example Conventions

## Container IDs
When writing code that uses container IDs, make sure your example IDs follows 
the flywheel container UID format, described with the regex: `"^[0-9a-fA-F]{24}$"`
something simple could be: `000123456789abcdefABCDEF`

If an ID is only used a single time for a simple example, it can remain right in the call:

```
# Get a project:
project = fw.get_project("000123456789abcdefABCDEF")
```

If the example has some breathing room for extra lines, make the identifier strings their own
variable at the top of the example so that users can easily modify it for their own use case:


good:
```
project_id = "000123456789abcdefABCDEF"
subject_label="S00345"

p = fw.get_project(project_id)
subject = fw.subjects.find(f"label=subject_label")
if subject.parents.project == project_id:
    print("same project")
```

bad:
```
p = fw.get_project("000123456789abcdefABCDEF")
subject = fw.subjects.find("label=S00345")
if subject.parents.project == "000123456789abcdefABCDEF":
    print("same project")
```

