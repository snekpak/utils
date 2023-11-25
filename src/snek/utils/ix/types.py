from dataclasses import dataclass


@dataclass
class Model:
  id: str
  object: str
  created: str
  onwed_by: int
