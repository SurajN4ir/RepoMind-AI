"""Authentication bounded context: verifies caller identity, nothing else.

Authorization (who may act on a given resource) is a business rule owned by
the resource's own module — see Repository's owner_id checks — not this one.
"""
