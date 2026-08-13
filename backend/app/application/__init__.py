"""Application composition layer between transport and domain modules.

The application layer coordinates domain modules, owns orchestration
workflows, translates domain exceptions, and provides a stable boundary
for the API transport. It never contains domain business logic.
"""
