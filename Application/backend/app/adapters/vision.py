from __future__ import annotations

import re
from dataclasses import dataclass, field

GENERIC_WORDS = {
    "img",
    "image",
    "photo",
    "picture",
    "pic",
    "jpeg",
    "jpg",
    "png",
    "webp",
    "gif",
    "screenshot",
    "download",
    "copy",
    "final",
    "scan",
    "upload",
    "whatsapp",
}

MAX_TAGS = 8
MAX_HINT = 120


@dataclass(frozen=True)
class VisionResult:
    provider: str
    tags: list[str] = field(default_factory=list)
    note: str = ""


class VisionProvider:
    """Provider-agnostic image understanding boundary.

    A production integration would call a licensed vision model here and return
    object or scene tags. The bundled implementation is a deterministic mock.
    """

    name = "abstract"

    def describe(self, *, filename: str, data: bytes, hint: str | None = None) -> VisionResult:
        raise NotImplementedError


def _tokens(text: str) -> list[str]:
    tokens = []
    for raw in re.findall(r"[a-z0-9]+", text.lower()):
        if len(raw) < 3 or raw.isdigit() or raw in GENERIC_WORDS:
            continue
        if raw not in tokens:
            tokens.append(raw)
    return tokens


class MockVisionProvider(VisionProvider):
    """Reads keywords from the file name and an optional customer hint.

    No image model is called and the pixels are never inspected, so the UI must
    present the result as a demo match. Keeping this behind the provider boundary
    means a real vision model can replace it without touching the API or UI.
    """

    name = "mock"

    def describe(self, *, filename: str, data: bytes, hint: str | None = None) -> VisionResult:
        stem = filename.rsplit("/", 1)[-1].rsplit(".", 1)[0]
        tags = _tokens(stem)
        if hint:
            for token in _tokens(hint[:MAX_HINT]):
                if token not in tags:
                    tags.append(token)
        return VisionResult(
            provider=self.name,
            tags=tags[:MAX_TAGS],
            note=(
                "Demo vision: keywords were read from the file name and hint. "
                "No image model is connected yet."
            ),
        )


_vision: VisionProvider = MockVisionProvider()


def get_vision() -> VisionProvider:
    return _vision


def set_vision(provider: VisionProvider) -> None:
    global _vision
    _vision = provider
