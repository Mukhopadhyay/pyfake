from pydantic import BaseModel
from typing import Optional, Type, Dict, Any

class Dummy:

    def __init__(self, model: Type[BaseModel]):
        self.model: Type[BaseModel] = model
    
    def generate(self, num: Optional[int] = None) -> Dict[str, Any]:
        return {'value': 42}
