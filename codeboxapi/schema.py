from pydantic import BaseModel


class CodeBoxStatus(BaseModel):
    status: str
    
    def __str__(self):
        return self.status
    
    def __repr__(self):
        return f"Status({self.status})"


class CodeBoxOutput(BaseModel):
    type: str
    content: str
    
    def __str__(self):
        return self.content
    
    def __repr__(self):
        return f"{self.type}({self.content})"
