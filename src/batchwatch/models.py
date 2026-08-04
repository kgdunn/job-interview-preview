"""Graph model.

Site -[:RAN]-> Batch -[:HAS_READING]-> Reading

Readings that made it through QC review are additionally linked from the batch
with :HAS_QC_READING. Not every batch has a QC pass done on it - the QC team
works through a queue and lags behind production by a few days.
"""

from neomodel import (
    DateTimeProperty,
    FloatProperty,
    RelationshipFrom,
    RelationshipTo,
    StringProperty,
    StructuredNode,
)


class Reading(StructuredNode):
    taken_at = DateTimeProperty(required=True)
    variable = StringProperty(required=True, index=True)
    value = FloatProperty()
    unit = StringProperty()

    batch = RelationshipFrom("Batch", "HAS_READING")

    def __repr__(self) -> str:
        return f"<Reading {self.variable}={self.value} {self.unit}>"


class Batch(StructuredNode):
    batch_id = StringProperty(required=True)
    product = StringProperty(required=True, index=True)
    started_at = DateTimeProperty(required=True)
    ended_at = DateTimeProperty()
    target_ph = FloatProperty()
    final_yield_kg = FloatProperty()

    site = RelationshipFrom("Site", "RAN")
    readings = RelationshipTo("Reading", "HAS_READING")
    qc_readings = RelationshipTo("Reading", "HAS_QC_READING")

    def __repr__(self) -> str:
        return f"<Batch {self.batch_id} {self.product}>"


class Site(StructuredNode):
    code = StringProperty(required=True, unique_index=True)
    name = StringProperty(required=True)
    country = StringProperty()

    batches = RelationshipTo("Batch", "RAN")

    def __repr__(self) -> str:
        return f"<Site {self.code}>"
