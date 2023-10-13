from typing import List, Dict, Any, Union

class Predicate:
    def __init__(self, path: List[str], operator: str, value: Any, valueType: str = None):
        self.path = path
        self.operator = operator
        self.value = value
        self.valueType = valueType

    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "operator": self.operator,
            f"{self.valueType.value}": self.value
        }

class Filter:
    def __init__(self, operator: str, predicates: List[Union["Filter", Predicate]]):
        self.operator = operator
        self.predicates = predicates

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operator": self.operator,
            "operands": [p.to_dict() if isinstance(p, Filter) else {
                "path": p.path,
                "operator": p.operator,
                f"{p.valueType.value}": p.value
            } for p in self.predicates]
        }

def and_(*predicates: Predicate) -> Filter:
    return Filter("And", list(predicates))

def or_(*predicates: Predicate) -> Filter:
    return Filter("Or", list(predicates))

# Example usage
# filter = and_(
#     Predicate(["round"], "Equal", "Double Jeopardy!"),
#     Predicate(["points"], "LessThan", 600)
# )

# nested_filter = and_(
#     Predicate(["answer"], "Like", "*nest*"),
#     or_(
#         Predicate(["points"], "GreaterThan", 700),
#         Predicate(["points"], "LessThan", 300)
#     )
# )

# print(filter.to_dict())
# print(nested_filter.to_dict())