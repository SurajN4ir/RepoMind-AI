"""Application-level pipelines that compose domain modules into coherent workflows.

Each pipeline owns the coordination of one end-to-end business operation.
It sequences domain services, manages cross-cutting resources (e.g. temp
workspaces), translates domain exceptions, and returns a structured result.

Pipelines follow the strangler pattern: they supersede orchestration that
previously lived inside domain services without modifying those services.
"""
