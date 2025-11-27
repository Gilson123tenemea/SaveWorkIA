from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException
from app.modelos.empresa_modelo import Empresa
from app.modelos.zona_modelo import Zona
from app.modelos.camara_modelo import Camara

def obtener_zonas_y_camaras_por_empresa(db: Session, empresa_id: int):
    # Validar empresa
    empresa = db.query(Empresa).filter(
        Empresa.id_Empresa == empresa_id,
        Empresa.borrado == True
    ).first()

    if not empresa:
        raise HTTPException(status_code=404, detail="Empresa no encontrada o inactiva")

    # Cargar zonas activas
    zonas = db.query(Zona).options(
        joinedload(Zona.camaras)
    ).filter(
        Zona.id_empresa_zona == empresa_id,
        Zona.borrado == True
    ).all()

    resultado = {
        "empresa_id": empresa.id_Empresa,
        "empresa_nombre": empresa.nombreEmpresa,
        "total_zonas": len(zonas),
        "total_camaras": 0,
        "zonas": []
    }

    total_camaras = 0

    for zona in zonas:
        camaras_activas = [
            cam for cam in zona.camaras if cam.borrado == True
        ]

        zonas_data = {
            "id_zona": zona.id_Zona,
            "nombreZona": zona.nombreZona,
            "camaras": [
                {
                    "id_camara": cam.id_camara,
                    "codigo": cam.codigo,
                    "estado": cam.estado,
                    "tipo": cam.tipo,
                    "ipAddress": cam.ipAddress
                }
                for cam in camaras_activas
            ]
        }

        total_camaras += len(camaras_activas)
        resultado["zonas"].append(zonas_data)

    resultado["total_camaras"] = total_camaras

    return resultado
