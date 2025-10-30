# flask_api/controlador/prompts_chompa/__init__.py
from .solido_acentos import build_prompt_solido_acentos, descripcion_solido_acentos_es
from .bloques_color import build_prompt_bloques_color, descripcion_bloques_color_es
from .mixto_degradado import build_prompt_mixto_degradado, descripcion_mixto_degradado_es
from .mixto_geometrico import build_prompt_mixto_geometrico, descripcion_mixto_geometrico_es
from .mixto_artistico import build_prompt_mixto_artistico, descripcion_mixto_artistico_es
from .mixto_textura import build_prompt_mixto_textura, descripcion_mixto_textura_es
from .mixto_personalizado import build_prompt_mixto_personalizado, descripcion_mixto_personalizado_es


def build_prompt_chompa_v1(attr: dict) -> str:
    """
    Genera el prompt según el camino seleccionado:
    - solid: Sólido con acentos
    - blocks: Bloques de color
    - mixto: Diseño mixto (sólido + sublimado IA)
    """
    camino = attr.get("caminoSeleccionado", "solid")
    
    if camino == "solid":
        return build_prompt_solido_acentos(attr)
    elif camino == "blocks":
        return build_prompt_bloques_color(attr)
    elif camino == "mixed":
        tipo_diseno = attr.get("tipoDisenoIA", "degraded")
        mapping = {
            "degraded": build_prompt_mixto_degradado,
            "geometric": build_prompt_mixto_geometrico,
            "artistic": build_prompt_mixto_artistico,
            "texture": build_prompt_mixto_textura,
            "personalized": build_prompt_mixto_personalizado,
        }
        builder = mapping.get(tipo_diseno, build_prompt_mixto_degradado)
        return builder(attr)
    else:
        return build_prompt_solido_acentos(attr)


def descripcion_chompa_es_v1(attr: dict) -> str:
    """
    Genera la descripción en español según el camino seleccionado
    """
    camino = attr.get("caminoSeleccionado", "solid")
    
    if camino == "solid":
        return descripcion_solido_acentos_es(attr)
    elif camino == "blocks":
        return descripcion_bloques_color_es(attr)
    elif camino == "mixed":
        tipo_diseno = attr.get("tipoDisenoIA", "degraded")
        mapping = {
            "degraded": descripcion_mixto_degradado_es,
            "geometric": descripcion_mixto_geometrico_es,
            "artistic": descripcion_mixto_artistico_es,
            "texture": descripcion_mixto_textura_es,
            "personalized": descripcion_mixto_personalizado_es,
        }
        builder = mapping.get(tipo_diseno, descripcion_mixto_degradado_es)
        return builder(attr)
    else:
        return descripcion_solido_acentos_es(attr)
