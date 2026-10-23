"""Inventory literal manifest edits without exporting unselected field values.

This is a coverage boundary, not Kubernetes schema validation or risk analysis.
Identity includes the supplied API version and literal namespace (no discovery,
defaulting, List expansion or API-version conversion is performed).
"""
from copy import deepcopy
import math

from review_artifacts import EvidenceError


def typed(value):
    """Compare JSON-compatible YAML with scalar types intact (True != 1)."""
    if value is None or type(value) in (str, bool, int):
        return (type(value).__name__, value)
    if type(value) is float and math.isfinite(value):
        return ("float", value)
    if isinstance(value, list):
        return ("list", tuple(typed(v) for v in value))
    if isinstance(value, dict) and all(type(k) is str for k in value):
        return ("dict", tuple(sorted((k, typed(v)) for k, v in value.items())))
    raise EvidenceError("Manifest inventory requires JSON-compatible YAML with string mapping keys and finite numbers")


def resource_index(docs):
    result = {}
    for position, doc in enumerate(docs):
        if doc is None:  # empty YAML documents/comments are not resources
            continue
        if not isinstance(doc, dict) or not isinstance(doc.get("metadata"), dict):
            raise EvidenceError("Every nonempty manifest document needs resource identity and metadata")
        meta = doc["metadata"]
        values = (doc.get("apiVersion"), doc.get("kind"), meta.get("name"))
        if not all(isinstance(v, str) and 0 < len(v) <= 253 and not any(ord(c) < 32 for c in v) for v in values):
            raise EvidenceError("Every resource needs bounded apiVersion, kind and metadata.name; expand List wrappers first")
        if values[1] == "List" or (values[1].endswith("List") and "items" in doc):
            raise EvidenceError("Expand Kubernetes List wrappers into separate resource documents first")
        namespace = meta.get("namespace")
        if "namespace" in meta and (not isinstance(namespace, str) or not namespace or len(namespace) > 253
                                   or any(ord(c) < 32 for c in namespace)):
            raise EvidenceError("An explicit namespace must be a bounded nonempty string")
        key = (values[0], values[1], namespace, values[2])
        if key in result:
            raise EvidenceError("Duplicate literal resource identities prevent a reliable coverage inventory")
        typed(doc)  # reject unsupported scalar/key types even in unselected resources
        result[key] = (position, doc)
    return result


def residual_categories(doc):
    """Remove only fields handled by the focused diff, then group the remainder.

    Returned subtrees stay inside this module. Never put them in reports/queries.
    Known empty parents are pruned only when removing a supported child empties
    them; arbitrary unselected null/empty distinctions remain observable.
    """
    node = deepcopy(doc)
    labels = node["metadata"].get("labels")
    if isinstance(labels, dict) and "helm.sh/chart" in labels:
        labels.pop("helm.sh/chart")  # separately checked chart identity/bookkeeping
        if not labels:
            node["metadata"].pop("labels")
    spec = node["spec"]
    template = spec["template"]
    pod = template["spec"]
    for container in pod["containers"]:
        container.pop("image", None)
        context = container.get("securityContext")
        if isinstance(context, dict) and "readOnlyRootFilesystem" in context:
            context.pop("readOnlyRootFilesystem")
            if not context:
                container.pop("securityContext")
        for name in ("readinessProbe", "livenessProbe", "startupProbe"):
            probe = container.get(name)
            http = probe.get("httpGet") if isinstance(probe, dict) else None
            if isinstance(http, dict) and any(k in http for k in ("path", "port")):
                http.pop("path", None)
                http.pop("port", None)
                if not http:
                    probe.pop("httpGet")
                    if not probe:
                        container.pop(name)
    return {
        "resource_metadata": node["metadata"],
        "deployment_settings": {k: v for k, v in spec.items() if k != "template"},
        "pod_metadata_and_template_fields": {k: v for k, v in template.items() if k != "spec"},
        "pod_settings_and_init_containers": {k: v for k, v in pod.items() if k != "containers"},
        "unselected_container_fields_or_order": pod["containers"],
        "other_resource_fields": {k: v for k, v in node.items() if k not in ("apiVersion", "kind", "metadata", "spec")},
    }


def inventory(before_docs, after_docs, before_selected, after_selected):
    old, new = resource_index(before_docs), resource_index(after_docs)
    entries = []
    for key in sorted(old.keys() | new.keys(), key=lambda k: tuple("" if v is None else v for v in k)):
        left, right = old.get(key), new.get(key)
        status = "added" if left is None else "removed" if right is None else (
            "unchanged" if typed(left[1]) == typed(right[1]) else "modified")
        selected = ((left is not None and left[0] == before_selected)
                    or (right is not None and right[0] == after_selected))
        categories = []
        if selected and left and right:
            a, b = residual_categories(left[1]), residual_categories(right[1])
            categories = [category for category in a if typed(a[category]) != typed(b[category])]
        elif selected:
            categories = ["resource_identity_or_presence"]
        outside = bool(categories) if selected else status != "unchanged"
        surfaces = []
        if left is None or right is None:
            surfaces = ["resource_presence"]
        else:
            if typed(left[1]["metadata"]) != typed(right[1]["metadata"]):
                surfaces.append("metadata")
            if typed({k: v for k, v in left[1].items() if k != "metadata"}) != typed(
                    {k: v for k, v in right[1].items() if k != "metadata"}):
                surfaces.append("resource_body")
        entries.append({"api_version": key[0], "kind": key[1], "namespace": key[2], "name": key[3],
                        "before_document_index": left[0] if left else None,
                        "after_document_index": right[0] if right else None,
                        "change": status, "selected_deployment": selected,
                        "outside_focused_scope": outside, "unreviewed_categories": categories,
                        "change_surfaces": surfaces})
    counts = {state: sum(e["change"] == state for e in entries) for state in ("added", "removed", "modified", "unchanged")}
    return {
        "schema_version": 1, "comparison": "literal_typed_manifest_content",
        "before_resource_count": len(old), "after_resource_count": len(new),
        "resource_changes": counts,
        "outside_scope_changed_resources": sum(e["outside_focused_scope"] for e in entries),
        "metadata_only_modified_resources": sum(e["change"] == "modified" and e["change_surfaces"] == ["metadata"] for e in entries),
        "resources": entries, "unselected_values_exported": False,
        "warning": "Inventory detects supplied content changes, not their risk or applicability. Unchanged resources may still need migration review. Identifiers are shown; unselected field values and keys are withheld. A null namespace means omitted, not an inferred default. API-version changes appear as removal plus addition. Lists must be expanded before upload. Sequence order can create content changes; resource document order, mapping order and YAML comments do not.",
    }
