# flask_api/controlador/prompts/__init__.py
from .degradado import build_prompt_degradado, descripcion_degradado_es
from .geometrico import build_prompt_geometrico, descripcion_geometrico_es
from .abstracto import build_prompt_abstracto, descripcion_abstracto_es
from .rayas import build_prompt_rayas, descripcion_rayas_es
from .camuflaje import build_prompt_camuflaje, descripcion_camuflaje_es
from .dos_tonos import build_prompt_dos_tonos, descripcion_dos_tonos_es
from .solido import build_prompt_solido, descripcion_solido_es
from .personalizado import build_prompt_personalizado, descripcion_personalizado_es

def build_prompt_v3(attr: dict) -> str:
    diseno = attr.get("diseno", "solid")
    mapping = {
        "degraded": build_prompt_degradado,
        "geometric": build_prompt_geometrico,
        "abstract": build_prompt_abstracto,
        "stripes": build_prompt_rayas,
        "camouflage": build_prompt_camuflaje,
        "two_tones": build_prompt_dos_tonos,
        "solid": build_prompt_solido,
        "full_design": build_prompt_personalizado,
    }
    builder = mapping.get(diseno, build_prompt_solido)
    return builder(attr)


def descripcion_es_v3(attr: dict) -> str:
    diseno = attr.get("diseno", "solid").lower()
    mapping = {
        "geometric": descripcion_geometrico_es,
        "degraded": descripcion_degradado_es,
        "abstract": descripcion_abstracto_es,
        "stripes": descripcion_rayas_es,
        "camouflage": descripcion_camuflaje_es,
        "two_tones": descripcion_dos_tonos_es,
        "solid": descripcion_solido_es,
        "full_design": descripcion_personalizado_es,
            }
    builder = mapping.get(diseno, descripcion_degradado_es)
    return builder(attr)