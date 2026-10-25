"""A UBL 2.3 document from placements, ordered and checked by the OASIS schemas.

The writer knows UBL's syntax and nothing about any model: the mapping file says where each value goes, and the
OASIS schemas say the order of an aggregate's members, which members are required, how many may repeat, and which
attributes a basic component takes. From those it

- builds one element per step and instance (sdc-mapper's placements), the document element merged by name;
- orders every aggregate's members as its UBL type's sequence does;
- adds a required aggregate whose members are all optional (a TaxCategory's TaxScheme) when the record has nothing
  for it, since UBL requires the element and not a value;
- removes an aggregate that lacks a required basic component (an AllowanceCharge with no Amount), and says which
  values went with it and why, rather than write a document that does not conform;
- validates the result against the OASIS schema for the document, and refuses it if it does not conform.

Element names are written with UBL's prefixes: `cac:` and `cbc:` for the common aggregate and basic components, no
prefix for the document element.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

from lxml import etree

from sdc_mapper import JOIN, MappingError

XSD = Path(__file__).with_name("xsd")
CAC = "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2"
CBC = "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2"
EXT = "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2"
PREFIXES = {"cac": CAC, "cbc": CBC, "ext": EXT}
UBL_VERSION = "2.3"


def document_namespace(name: str) -> str:
    return f"urn:oasis:names:specification:ubl:schema:xsd:{name}-2"


@lru_cache(maxsize=None)
def schema_for(document: str):
    import xmlschema
    path = XSD / "maindoc" / f"UBL-{document}-{UBL_VERSION}.xsd"
    if not path.exists():
        raise MappingError(f"this mapper does not carry the UBL {UBL_VERSION} {document} schema")
    return xmlschema.XMLSchema(str(path))


def clark(name: str, document: str) -> str:
    if ":" in name:
        prefix, local = name.split(":", 1)
        if prefix not in PREFIXES:
            raise MappingError(f"{name}: UBL has no prefix {prefix!r}")
        return f"{{{PREFIXES[prefix]}}}{local}"
    return f"{{{document_namespace(document)}}}{name}"


@dataclass
class Node:
    name: str
    key: tuple
    text: str | None = None
    attrs: dict[str, str] = field(default_factory=dict)
    children: list["Node"] = field(default_factory=list)
    positions: set[int] = field(default_factory=set)        # values whose own text (or attribute) is on this element

    def subtree_positions(self) -> set[int]:
        out = set(self.positions)
        for c in self.children:
            out |= c.subtree_positions()
        return out


class _Type:
    """What the writer needs of a UBL element declaration."""

    def __init__(self, decl):
        self.decl = decl
        t = decl.type
        self.simple = t.has_simple_content() or t.is_simple()
        self.attributes = set(getattr(t, "attributes", {}) or {})
        self.members: list = [] if self.simple else list(t.content.iter_elements())
        self.order = {m.name: i for i, m in enumerate(self.members)}

    def member(self, qname):
        for m in self.members:
            if m.name == qname:
                return m
        return None


@lru_cache(maxsize=None)
def _type(decl) -> _Type:
    return _Type(decl)


def _fillable(decl, seen=()) -> bool:
    """An aggregate UBL can carry empty: every required member is itself an aggregate it can carry empty."""
    t = _type(decl)
    if t.simple or decl.name in seen:
        return False
    return all(_fillable(m, seen + (decl.name,)) for m in t.members if m.min_occurs >= 1)


class Builder:
    def __init__(self, document: str, order: dict[str, int] | None = None):
        self.document = document
        self.order = order or {}             # declared cluster order (Mapping.cluster_order)
        self.root: Node | None = None
        self.index: dict[tuple, Node] = {}
        self.pruned: dict[int, str] = {}      # value position -> why its element was removed

    def ensure(self, steps) -> Node:
        if not steps:
            raise MappingError("a placement with no target element")
        name, _ = steps[0]
        if self.root is None:
            if ":" in name:
                raise MappingError(f"the document element must be a UBL document ({self.document}), not {name}")
            self.root = Node(name, ())
        elif self.root.name != name:
            raise MappingError(f"one document, one document element: {self.root.name} and {name}")
        node = self.root
        for name, key in steps[1:]:
            if key == JOIN:          # the element of that name the parent already has, or a new one
                found = [c for c in node.children if c.name == name]
                if len(found) > 1:
                    raise MappingError(f"'={name}' under {node.name}: {len(found)} elements of that name, so which "
                                       "one is not settled")
                if found:
                    node = found[0]
                    continue
            k = (id(node), name, key)
            child = self.index.get(k)
            if child is None:
                child = Node(name, key)
                node.children.append(child)
                self.index[k] = child
            node = child
        return node

    def find(self, steps) -> Node | None:
        if self.root is None or not steps or self.root.name != steps[0][0]:
            return None
        node = self.root
        for name, key in steps[1:]:
            node = self.index.get((id(node), name, key))
            if node is None:
                return None
        return node

    @staticmethod
    def _where(steps, attribute=None) -> str:
        return "/".join(n for n, _ in steps) + (f"/@{attribute}" if attribute else "")

    def put(self, steps, attribute: str | None, text: str, position: int | None = None):
        node = self.ensure(steps)
        if attribute:
            if attribute in node.attrs and node.attrs[attribute] != text:
                raise MappingError(f"two values for {self._where(steps, attribute)}")
            node.attrs[attribute] = text
        else:
            if node.text is not None and node.text != text:
                raise MappingError(f"two values for {self._where(steps)}: give one of them its own element ('+')")
            node.text = text
        if position is not None:
            node.positions.add(position)
        return node

    # ------------------------------------------------------------ against the schema
    def finish(self) -> etree._Element:
        if self.root is None:
            raise MappingError("nothing to write: no value of the record reached the document")
        schema = schema_for(self.document)
        decl = schema.elements.get(self.root.name)
        if decl is None:
            raise MappingError(f"{self.root.name} is not the document element of UBL {UBL_VERSION} {self.document}")
        version = Node("cbc:UBLVersionID", (), text=UBL_VERSION)
        self.root.children.insert(0, version)
        ok, why = self._check(self.root, decl)
        if not ok:
            raise MappingError(f"the {self.document} cannot be written: {why}")
        el = self._element(self.root)
        errors = list(schema.iter_errors(el))
        if errors:
            raise MappingError(f"the {self.document} does not conform to UBL {UBL_VERSION}: {errors[0].reason} "
                               f"at {errors[0].path}")
        return el

    def _check(self, node: Node, decl) -> tuple[bool, str]:
        t = _type(decl)
        if t.simple:
            if node.children:
                raise MappingError(f"{node.name} is a basic component: it holds a value, not {node.children[0].name}")
            bad = set(node.attrs) - t.attributes
            if bad:
                raise MappingError(f"{node.name} takes no attribute {sorted(bad)[0]} in UBL {UBL_VERSION}")
            return (node.text is not None, f"{node.name} has no value")
        if node.text is not None:
            raise MappingError(f"{node.name} is an aggregate: it holds components, not a value")
        if node.attrs:
            raise MappingError(f"{node.name} is an aggregate and takes no attributes")
        kept = []
        for child in node.children:
            cdecl = t.member(clark(child.name, self.document))
            if cdecl is None:
                raise MappingError(f"{child.name} is not a member of {node.name} in UBL {UBL_VERSION}")
            ok, why = self._check(child, cdecl)
            if ok:
                kept.append((child, cdecl))
            else:
                for p in child.subtree_positions():
                    self.pruned.setdefault(p, why)
        counts: dict[str, int] = {}
        for child, cdecl in kept:
            counts[cdecl.name] = counts.get(cdecl.name, 0) + 1
            if cdecl.max_occurs is not None and counts[cdecl.name] > cdecl.max_occurs:
                raise MappingError(f"UBL {UBL_VERSION} allows {cdecl.max_occurs} {child.name} in {node.name}; the "
                                   "mapping places more")
        for m in t.members:
            if m.min_occurs >= 1 and not counts.get(m.name):
                short = self._short(m.name)
                if _fillable(m):
                    kept.append((self._fill(short, m), m))
                else:
                    return False, f"UBL requires {short} in {node.name}, and the record has no value for it"
        if not kept:
            return False, f"{node.name} has nothing in it"
        # by the UBL type's sequence; repeats by the declared order of the clusters that made them, else the record's
        kept.sort(key=lambda kc: (t.order[kc[1].name], self._rank(kc[0].key)))
        node.children = [c for c, _ in kept]
        return True, ""

    def _rank(self, key: tuple) -> tuple:
        return tuple(self.order[part[0]] for part in key
                     if isinstance(part, tuple) and len(part) == 2 and part[0] in self.order)

    def _short(self, qname: str) -> str:
        ns, local = qname[1:].split("}", 1)
        for prefix, uri in PREFIXES.items():
            if uri == ns:
                return f"{prefix}:{local}"
        return local

    def _fill(self, name: str, decl) -> Node:
        node = Node(name, ("fill",))
        for m in _type(decl).members:
            if m.min_occurs >= 1:
                node.children.append(self._fill(self._short(m.name), m))
        return node

    def _element(self, node: Node, parent=None):
        tag = clark(node.name, self.document)
        if parent is None:
            nsmap = {None: document_namespace(self.document), "cac": CAC, "cbc": CBC}
            el = etree.Element(tag, nsmap=nsmap)
        else:
            el = etree.SubElement(parent, tag)
        if node.text is not None:
            el.text = node.text
        for k, v in node.attrs.items():
            el.set(k, v)
        for c in node.children:
            self._element(c, el)
        return el

    def where(self, position: int) -> Node | None:
        """The element holding a value, after the schema check (None when it was removed)."""
        def walk(n):
            if position in n.positions:
                return n
            for c in n.children:
                found = walk(c)
                if found:
                    return found
            return None
        return walk(self.root) if self.root else None
