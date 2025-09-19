from dataclasses import dataclass, field
from typing import Optional
from asteval import Interpreter

@dataclass(slots=True)
class CalculatorService:
    """Safe arithmetic evaluation using asteval."""
    _interp: Optional[Interpreter] = field(init=False, repr=False, default=None)

    def __post_init__(self) -> None:
        # Disable numpy to keep evaluation simple and safe
        self._interp = Interpreter(use_numpy=False)

    def evaluate(self, expression: str) -> float:
        if self._interp is None:
            # Shouldn't happen, but keeps mypy/pyright happy
            self._interp = Interpreter(use_numpy=False)
        try:
            val = self._interp(expression)
            if not isinstance(val, (int, float)):
                raise ValueError("Expression did not evaluate to a number")
            return float(val)
        except Exception as e:
            raise ValueError(f"Invalid expression: {e}")
