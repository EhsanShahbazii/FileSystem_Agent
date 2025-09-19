# src/fs_agent/services/calculator.py
from dataclasses import dataclass
from asteval import Interpreter

@dataclass(slots=True)
class CalculatorService:
    """Safe arithmetic evaluation using asteval."""
    def __post_init__(self):
        # Disable dangerous builtins
        self._interp = Interpreter(use_numpy=False)
    
    def evaluate(self, expression: str) -> float:
        try:
            val = self._interp(expression)
            if not isinstance(val, (int, float)):
                raise ValueError("Expression did not evaluate to a number")
            return float(val)
        except Exception as e:
            raise ValueError(f"Invalid expression: {e}")
