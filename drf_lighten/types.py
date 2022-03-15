from typing import Dict, List, Tuple, Union

DictField = Dict[str, "Structure"]
Field = Union[str, DictField]
Structure = Union[List[Field], Tuple[Field]]
