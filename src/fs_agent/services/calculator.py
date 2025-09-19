from dataclasses import dataclass
from arithmetic_eval import eval_expr

@dataclass(slots=True)
class CalculatorService:
    """Safe arithmetic evaluation using arithmetic_eval."""
    def evaluate(self, expression: str) -> float:
        try:
            val = eval_expr(expression)
            return float(val)
        except Exception as e:
            raise ValueError(f"Invalid expression: {e}")
