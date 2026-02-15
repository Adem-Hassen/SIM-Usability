from pydantic import BaseModel,Field
from typing import List, Optional

class UiPage(BaseModel):

    name:str
    code : str
    accessiblity_tree=List[dict] = Field(default_factory=list)
    screenshots :Optional[bytes] = None



    
