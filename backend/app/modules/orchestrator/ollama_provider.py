"""Ollama response-generation provider adapter for the ResponseGenerator protocol."""

import httpx
import structlog

from app.modules.context_builder.models import LLMContext
from app.modules.orchestrator.exceptions import ResponseGenerationError
from app.modules.orchestrator.models import ResponseIntent, ResponsePlan, ToolOutput

logger = structlog.get_logger(__name__)

_INTENT_PROMPTS: dict[ResponseIntent, str] = {
    ResponseIntent.ANSWER: (
        "Answer the question concisely using the provided code context.\n"
        "Reference file paths and citation markers like [citation:1] inline.\n"
        "If the context does not contain enough information, say so.\n\n"
        "{context}\n\nQuestion: {query}"
    ),
    ResponseIntent.EXPLAIN: (
        "Explain how the relevant code works step by step.\n"
        "Reference each file by path and use citation markers like [citation:1].\n"
        "Assume the reader understands programming but is unfamiliar with this codebase.\n\n"
        "{context}\n\nExplain: {query}"
    ),
    ResponseIntent.TRACE: (
        "Trace the execution flow through the relevant files.\n"
        "List the call path and entry points.\n"
        "Reference each file by path and use citation markers like [citation:1].\n\n"
        "{context}\n\nTrace: {query}"
    ),
    ResponseIntent.COMPARE: (
        "Compare the relevant implementations.\n"
        "Use ``` code blocks to show differences.\n"
        "Reference each file by path and use citation markers like [citation:1].\n\n"
        "{context}\n\nCompare: {query}"
    ),
    ResponseIntent.GENERATE: (
        "Generate code that matches the existing repository conventions.\n"
        "1. List which files influenced your generation with [citation:N] markers.\n"
        "2. State the conventions you inferred from those files "
        "(naming, imports, structure, error handling, documentation style).\n"
        "3. Use ``` code blocks for generated code.\n"
        "4. Clearly distinguish generated code from retrieved code.\n"
        "5. Never claim generated code exists in the repository.\n"
        "6. If the provided examples are insufficient to infer conventions, "
        "state it explicitly and make a best-effort implementation.\n\n"
        "{context}\n\nRequest: {query}"
    ),
    ResponseIntent.SUMMARY: (
        "Summarize the key findings from the provided code context.\n"
        "Reference file paths and citation markers like [citation:1] inline.\n"
        "Focus on the most important architectural patterns.\n\n"
        "{context}\n\nSummarize: {query}"
    ),
    ResponseIntent.REFACTOR: (
        "Suggest improvements to the code in the provided context.\n"
        "Show before-and-after examples using ``` code blocks.\n"
        "Reference each file by path and use citation markers like [citation:1].\n\n"
        "{context}\n\nRequest: {query}"
    ),
}


class OllamaResponseGenerator:
    """Calls Ollama's ``/api/generate`` to produce response text from evidence context.

    Uses a single-shot, non-streaming generation request.  Replace with a
    streaming-aware provider once token-level streaming reaches the domain.
    """

    def __init__(
        self,
        model_name: str = "llama3.2",
        *,
        base_url: str = "http://localhost:11434",
        timeout_seconds: float = 60.0,
        system_prompt: str | None = None,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self.model_name = model_name
        self._base_url = base_url.rstrip("/")
        self._timeout_seconds = timeout_seconds
        self._system_prompt = system_prompt
        self._client = client

    async def generate(
        self,
        context: LLMContext,
        plan: ResponsePlan,
        tool_outputs: tuple[ToolOutput, ...],
    ) -> str:
        """Build a prompt from the evidence context and call Ollama."""
        prompt = self._build_prompt(context, plan, tool_outputs)
        system_prompt = self._system_prompt or self._build_system_prompt(plan)
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "options": {
                "temperature": plan.temperature,
            },
        }
        logger.debug(
            "ollama_generation_request_started",
            model=self.model_name,
            intent=plan.intent.value,
        )
        try:
            if self._client is not None:
                response = await self._client.post(f"{self._base_url}/api/generate", json=payload)
            else:
                async with httpx.AsyncClient(timeout=self._timeout_seconds) as client:
                    response = await client.post(f"{self._base_url}/api/generate", json=payload)
            response.raise_for_status()
        except httpx.TimeoutException as exc:
            raise ResponseGenerationError("Ollama generation request timed out.") from exc
        except httpx.HTTPError as exc:
            raise ResponseGenerationError("Ollama generation request failed.") from exc

        try:
            body = response.json()
            text = body["response"]
        except (KeyError, TypeError, ValueError) as exc:
            raise ResponseGenerationError(
                "Ollama response did not contain generated text."
            ) from exc

        if not isinstance(text, str) or not text.strip():
            raise ResponseGenerationError("Ollama returned empty response text.")

        logger.info(
            "ollama_generation_request_completed",
            model=self.model_name,
            response_length=len(text),
        )
        return text

    def _build_system_prompt(self, plan: ResponsePlan) -> str:
        intent = plan.intent
        if intent is ResponseIntent.GENERATE:
            return (
                "You are a repository-aware code generation assistant. "
                "Generate code that matches the existing repository's conventions. "
                "Always cite which files influenced your generation. "
                "Never claim generated code exists in the repository."
            )
        if intent is ResponseIntent.TRACE:
            return (
                "You are a code analysis assistant. "
                "Trace execution flows accurately based on the provided context."
            )
        return (
            "You are a helpful code assistant for the RepoMind project. "
            "Answer concisely based on the provided code context."
        )

    def _build_prompt(
        self,
        context: LLMContext,
        plan: ResponsePlan,
        tool_outputs: tuple[ToolOutput, ...],
    ) -> str:
        """Construct the user-facing prompt from evidence context and intent."""
        template = _INTENT_PROMPTS.get(plan.intent)
        if template is None:
            template = _INTENT_PROMPTS[ResponseIntent.ANSWER]
        lines: list[str] = []
        if context.repository_structure:
            lines.append(context.repository_structure)
        if context.convention_examples:
            lines.append(context.convention_examples)
        if context.conversation_history:
            lines.append(f"Previous conversation:\n{context.conversation_history}")
            lines.append("---")
        lines.append(
            template.format(query=context.query.text, context=context.formatted_text),
        )
        if tool_outputs:
            lines.extend(
                [
                    "",
                    "Tool Results:",
                    *(f"  [{output.tool_name}] {output.data}" for output in tool_outputs),
                ]
            )
        return "\n".join(lines)
