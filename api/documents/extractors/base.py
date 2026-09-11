from dataclasses import dataclass, field


@dataclass
class ExtractionResult:
    fields: dict = field(default_factory=dict)
    confidence: float = 0.0
    entities: dict = field(default_factory=dict)
    authenticity_flags: list[str] = field(default_factory=list)
