def build_prompt_moteado(attr: dict) -> str:
    print("🎨 Entrando a build_prompt_moteado con:", attr)
    colores_en = ', '.join(attr.get('colores', ['gray', 'blue']))
    print("🎨 Colores en inglés:", colores_en)
    prompt = (
        f"Seamless speckled pattern, realistic textile texture, colors: {colores_en}, flat surface, diffuse lighting, high detail, sportswear quality"
    )
    print("🎨 Prompt final:", prompt)
    return prompt
