#!/usr/bin/env python3
"""Generate endpoint reference docs from Flywheel OpenAPI specs.

Outputs (per service), written into the skill's references/ dir:
  - references/endpoints_index_<service>.md   — one line per endpoint
  - references/endpoints/<service>_<tag>.md   — per-tag detail files

Usage (run from the repo root so --spec paths resolve):
    # Core API (fetched from docs site)
    python scripts/generate_endpoint_docs.py --service core

    # Local spec files
    python scripts/generate_endpoint_docs.py --service xfer --spec xferapi.json
    python scripts/generate_endpoint_docs.py --service snapshot --spec snapshotapi.json

    # Regenerate all
    python scripts/generate_endpoint_docs.py --all
"""

import argparse
import json
import re
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

OPENAPI_URL = "https://api-docs.flywheel.io/latest/tags/21.5.0/swagger/openapi.json"
SCRIPT_DIR = Path(__file__).parent
REFS_DIR = SCRIPT_DIR.parent / "references"
OUT_DIR = REFS_DIR / "endpoints"

HTTP_METHODS = ["get", "post", "put", "patch", "delete", "head"]

SERVICES = {
    "core": {"url": OPENAPI_URL, "spec": None, "label": "Flywheel Core API (/api/)"},
    "xfer": {"url": None, "spec": "xferapi.json", "label": "Flywheel Transfer API (/xfer/)"},
    "snapshot": {"url": None, "spec": "snapshotapi.json", "label": "Flywheel Snapshot API (/snapshot/)"},
}


def fetch_spec(url: str) -> dict:
    """Download and parse the OpenAPI JSON spec."""
    print(f"Fetching spec from {url} ...")
    with urllib.request.urlopen(url, timeout=60) as resp:  # noqa: S310
        return json.loads(resp.read())


def load_spec(path: str) -> dict:
    """Load the OpenAPI JSON spec from a local file."""
    print(f"Loading spec from {path} ...")
    with open(path) as f:
        return json.load(f)


def slugify(name: str) -> str:
    """Convert a name to a safe filename slug."""
    return re.sub(r"[^\w-]", "_", name.lower()).strip("_")


def resolve_ref(spec: dict, ref: str) -> dict:
    """Resolve a $ref string like '#/components/schemas/Foo' to its definition."""
    parts = ref.lstrip("#/").split("/")
    node = spec
    for part in parts:
        try:
            node = node[part]
        except (KeyError, TypeError):
            return {"type": ref.split("/")[-1]}
    return node


def describe_schema(spec: dict, schema: dict, depth: int = 0) -> str:
    """Produce a compact type description from a JSON Schema node."""
    if "$ref" in schema:
        schema = resolve_ref(spec, schema["$ref"])

    s_type = schema.get("type", "")
    s_fmt = schema.get("format", "")
    enum = schema.get("enum")

    if enum:
        choices = " | ".join(str(e) for e in enum[:8])
        suffix = " | ..." if len(enum) > 8 else ""
        return f"enum({choices}{suffix})"
    if s_type == "array":
        items = schema.get("items", {})
        return f"array[{describe_schema(spec, items, depth + 1)}]"
    if s_type == "object" and depth == 0:
        props = schema.get("properties", {})
        if props:
            pairs = ", ".join(f"{k}: {describe_schema(spec, v, depth + 1)}" for k, v in list(props.items())[:5])
            suffix = ", ..." if len(props) > 5 else ""
            return f"object({pairs}{suffix})"
        return "object"
    if s_fmt:
        return f"{s_type}({s_fmt})"
    return s_type or "any"


def format_parameters(spec: dict, parameters: list) -> str:
    """Format a list of OpenAPI parameter objects into a markdown table."""
    if not parameters:
        return ""

    rows = []
    for p in parameters:
        if "$ref" in p:
            p = resolve_ref(spec, p["$ref"])
        name = p.get("name", "?")
        location = p.get("in", "?")
        required = "yes" if p.get("required") else "no"
        schema = p.get("schema", {})
        type_str = describe_schema(spec, schema)
        description = p.get("description", "").replace("\n", " ").strip()[:120]
        rows.append(f"| `{name}` | {location} | {required} | `{type_str}` | {description} |")

    header = "| Name | In | Required | Type | Description |\n|---|---|---|---|---|"
    return header + "\n" + "\n".join(rows)


def format_request_body(spec: dict, request_body: dict) -> str:
    """Format a requestBody object into a compact markdown summary."""
    if not request_body:
        return ""

    content = request_body.get("content", {})
    parts = []
    for media_type, media_obj in content.items():
        schema = media_obj.get("schema", {})
        type_str = describe_schema(spec, schema)
        parts.append(f"`{media_type}`: {type_str}")

    required = " *(required)*" if request_body.get("required") else ""
    description = request_body.get("description", "").replace("\n", " ").strip()
    lines = [f"**Request Body**{required}"]
    if description:
        lines.append(description)
    lines.extend(parts)
    return "\n".join(lines)


def collect_endpoints(spec: dict) -> dict[str, list[dict]]:
    """Walk the spec paths and group endpoints by their first tag."""
    paths = spec.get("paths", {})
    by_tag: dict[str, list[dict]] = defaultdict(list)

    for path, path_item in paths.items():
        path_params = path_item.get("parameters", [])

        for method in HTTP_METHODS:
            operation = path_item.get(method)
            if not operation:
                continue

            tags = operation.get("tags") or ["untagged"]
            tag = tags[0]
            op_params = operation.get("parameters", [])

            by_tag[tag].append({
                "method": method.upper(),
                "path": path,
                "summary": operation.get("summary", "").strip(),
                "description": operation.get("description", "").strip(),
                "parameters": path_params + op_params,
                "request_body": operation.get("requestBody"),
                "operation_id": operation.get("operationId", ""),
                "deprecated": operation.get("deprecated", False),
            })

    return by_tag


def write_index(service: str, label: str, by_tag: dict[str, list[dict]]) -> None:
    """Write the compact endpoints_index_<service>.md."""
    index_file = REFS_DIR / f"endpoints_index_{service}.md"

    lines = [
        f"# {label} — Endpoints Index",
        "",
        f"One line per endpoint. For full parameter details, read `endpoints/{service}_<tag>.md`.",
        "",
        "| Method | Path | Tag | Summary |",
        "|---|---|---|---|",
    ]

    for tag in sorted(by_tag):
        for ep in sorted(by_tag[tag], key=lambda e: e["path"]):
            deprecated = " *(deprecated)*" if ep["deprecated"] else ""
            summary = ep["summary"] or (ep["description"][:80] if ep["description"] else "")
            lines.append(f"| `{ep['method']}` | `{ep['path']}` | {tag} | {summary}{deprecated} |")

    index_file.write_text("\n".join(lines) + "\n")
    print(f"Wrote {index_file.name}")


def write_tag_file(spec: dict, service: str, label: str, tag: str, endpoints: list[dict]) -> None:
    """Write a per-tag detail file named <service>_<tag>.md."""
    slug = slugify(tag)
    out_path = OUT_DIR / f"{service}_{slug}.md"

    lines = [
        f"# {label} — {tag}",
        "",
        f"Service: `{service}`  |  Tag: `{tag}`  |  Generated from OpenAPI spec.",
        "",
    ]

    for ep in sorted(endpoints, key=lambda e: (e["path"], e["method"])):
        deprecated_marker = " *(deprecated)*" if ep["deprecated"] else ""
        lines.append(f"## `{ep['method']} {ep['path']}`{deprecated_marker}")
        lines.append("")

        if ep["summary"]:
            lines.append(f"**{ep['summary']}**")
            lines.append("")

        if ep["description"] and ep["description"] != ep["summary"]:
            desc = ep["description"][:500]
            if len(ep["description"]) > 500:
                desc += " ..."
            lines.append(desc)
            lines.append("")

        params_md = format_parameters(spec, ep["parameters"])
        if params_md:
            lines.append("**Parameters**")
            lines.append("")
            lines.append(params_md)
            lines.append("")

        body_md = format_request_body(spec, ep["request_body"]) if ep["request_body"] else ""
        if body_md:
            lines.append(body_md)
            lines.append("")

        lines.append("---")
        lines.append("")

    out_path.write_text("\n".join(lines))
    print(f"  Wrote {out_path.name} ({len(endpoints)} endpoints)")


def process_service(service: str, spec_path: str | None, spec_url: str | None) -> None:
    """Load spec and generate index + tag files for one service."""
    label = SERVICES[service]["label"]

    if spec_path:
        # Resolve relative to the repo root (cwd) or absolute
        p = Path(spec_path)
        if not p.is_absolute():
            p = Path.cwd() / p
        spec = load_spec(str(p))
    elif spec_url:
        try:
            spec = fetch_spec(spec_url)
        except Exception as exc:
            print(f"ERROR fetching spec for {service}: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        print(f"ERROR: no spec URL or path configured for service '{service}'", file=sys.stderr)
        sys.exit(1)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\nParsing {service} endpoints...")
    by_tag = collect_endpoints(spec)
    total = sum(len(v) for v in by_tag.values())
    print(f"Found {total} endpoints across {len(by_tag)} tags")

    print(f"\nWriting index -> endpoints_index_{service}.md")
    write_index(service, label, by_tag)

    print(f"\nWriting tag files -> {OUT_DIR.name}/{service}_*.md")
    for tag in sorted(by_tag):
        write_tag_file(spec, service, label, tag, by_tag[tag])

    print(f"\nDone: {service} — {len(by_tag)} tag files + index.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--service", choices=list(SERVICES.keys()), help="Which service to generate docs for")
    parser.add_argument("--spec", help="Path to local openapi.json (overrides default for the service)")
    parser.add_argument("--all", action="store_true", help="Regenerate docs for all services")
    args = parser.parse_args()

    if not args.all and not args.service:
        parser.print_help()
        sys.exit(1)

    services_to_run = list(SERVICES.keys()) if args.all else [args.service]

    for svc in services_to_run:
        cfg = SERVICES[svc]
        # --spec override applies only when a single service is specified
        spec_path = args.spec if (args.service == svc and args.spec) else cfg["spec"]
        process_service(svc, spec_path=spec_path, spec_url=cfg["url"])


if __name__ == "__main__":
    main()
