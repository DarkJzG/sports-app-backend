from .moteado import build_prompt_moteado
from .lineas import build_prompt_lineas
from .circuitos import build_prompt_circuitos
from .olas import build_prompt_olas
from .personalizado import build_prompt_personalizado

def build_prompt_textura(attr: dict) -> str:
    print("🎨 Entrando a build_prompt_textura con:", attr
    )
    tipo = attr.get('tipo', 'moteado')
    builder_mapping = {
        'moteado': build_prompt_moteado,
        'lineas': build_prompt_lineas,
        'circuitos': build_prompt_circuitos,
        'olas': build_prompt_olas,
        'personalizado': build_prompt_personalizado
    }
    builder = builder_mapping.get(tipo, build_prompt_moteado)
    print("🎨 Builder seleccionado:", builder)
    return builder(attr)
