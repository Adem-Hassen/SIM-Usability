from pydantic import BaseModel,Field
from typing import List, Optional,Dict

class UiPage(BaseModel):

    name:str
    code : str
    accessiblity_tree=List[dict] = Field(default_factory=list)
    screenshots :Optional[bytes] = None



    
class AgentTrace(BaseModel):
    agent_id:str
    page_name:str
    actions:List[dict]
    errors:List[str]


class CodeFixeProposal(BaseModel):

    agent_id:str
    page_name:str
    target_element:str
    fixed_code: str


class WorkspaceState(BaseModel):

    ui_code:Dict[str,str]
    proposed_fixes=List[CodeFixeProposal]
    applied_fixes=List[dict]



