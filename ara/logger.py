from dataclasses import dataclass, field
import time

@dataclass
class InMemoryLogger:
    events: list[str] = field(default_factory=list)

    def log(self, msg: str) -> None:
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        self.events.append(f"[{ts}] {msg}")

    def dump(self) -> list[str]:
        return list(self.events)