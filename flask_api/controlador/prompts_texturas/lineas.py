def build_prompt_lineas(attr: dict) -> str:
    print("🎨 Entrando a build_prompt_lineas con:", attr)
    colores_en = ', '.join(attr.get('colores', ['black', 'white']))
    direc = attr.get('direccion', 'horizontal')
    print("🎨 Colores en inglés:", colores_en)
    print("🎨 Dirección:", direc)
    prompt = (
        f"Seamless striped pattern ({direc}), sharp textile, colors: {colores_en}, no folds, high-resolution, sportswear fabric"
    )
    print("🎨 Prompt final:", prompt)
    return prompt
