from pydantic import BaseModel

class SolicitudCambioContraseña(BaseModel):
    correo: str
    id_persona: int

class VerificarTokenReset(BaseModel):
    token: str
    nuevaContraseña: str
    id_persona: int