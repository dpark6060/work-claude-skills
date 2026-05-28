# Gear Structure

## Flywheel Decoupling

Decouple gear logic from Flywheel. Keeps `main.py` testable — no client, context, or config needed.

### The Core Principle

`run.py` owns all Flywheel interactions. `main.py` receives only the data it needs to do its job.

**Config parsing**: Parse the full gear config in `run.py`. Pass individual values to `main.py` — not the config object.

```python
# Good — run.py extracts what main.py needs
subject_label = gear_context.config.get("subject_label")
threshold = gear_context.config.get("threshold", 0.5)
result = main(subject_label=subject_label, threshold=threshold)

# Bad — main.py is now coupled to gear config shape
result = main(config=gear_context.config)
```

**Flywheel SDK client**: Pass only if `main.py` needs SDK calls. Otherwise omit.

**Metadata / QC results**: If only writing QC at end, return data from `main.py`, call `add_qc_result()` in `run.py`.

```python
# Good — main.py returns data, run.py writes it
qc_data = main(input_file=input_path, threshold=threshold)
gear_context.config.metadata.add_qc_result(**qc_data)

# If metadata needed mid-run or return gets unwieldy: pass config.metadata, not full config
result = main(input_file=input_path, metadata=gear_context.config.metadata)
```

### When Flywheel Coupling Is Acceptable

Some gears are inherently Flywheel-heavy: they traverse containers, resolve subject/session relationships, or act as orchestrators.

**Acceptable coupling:**
- Passing `fw` (the SDK client) when `main.py` needs to query or modify containers
- Passing container IDs when the gear's core logic involves container relationships
- Passing `config.metadata` when metadata must be written incrementally

**Over-engineering to avoid:**
- Passing enormous data structures just to avoid passing `fw` — just pass `fw`
- Complex return types to avoid passing metadata — pass `config.metadata` instead
