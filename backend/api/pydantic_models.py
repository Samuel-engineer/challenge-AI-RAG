from pydantic import BaseModel, Field, StrictStr
from enum import Enum
from datetime import datetime

class ModelName(str, Enum):
    """Liste des modèles IA disponibles."""
    MISTRAL_LARGE_LATEST = "mistral-large-latest"
    
class QueryInput(BaseModel):
    """Modèle pour gérer les requêtes utilisateur vers l'IA."""
    question: StrictStr = Field(..., title="Question posée à l'IA")
    session_id: str | None = Field(default=None, title="ID de la session utilisateur")
    model: ModelName = Field(default=ModelName.MISTRAL_LARGE_LATEST, title="Modèle d'IA utilisé")

class QueryResponse(BaseModel):
    """Modèle pour structurer la réponse de l'IA."""
    answer: StrictStr = Field(..., title="Réponse générée par l'IA")
    session_id: str = Field(..., title="ID de la session utilisateur")
    model: ModelName = Field(..., title="Modèle d'IA utilisé")

class DocumentInfo(BaseModel):
    """Informations sur un document stocké."""
    id: int = Field(..., gt=0, title="ID unique du document")
    filename: StrictStr = Field(..., title="Nom du fichier")
    upload_timestamp: datetime = Field(..., title="Horodatage de l'upload")

class DeleteFileRequest(BaseModel):
    """Requête pour supprimer un document via son ID."""
    file_id: int = Field(..., gt=0, title="ID du fichier à supprimer")
