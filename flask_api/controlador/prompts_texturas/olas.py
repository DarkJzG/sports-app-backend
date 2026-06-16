def build_prompt_olas(attr: dict) -> str:
    print("🎨 Entrando a build_prompt_olas con:", attr)
    colores_en = ', '.join(attr.get('colores', ['blue', 'white']))
    print("🎨 Colores en inglés:", colores_en)
    prompt = (
        f"Wave/flowing pattern, seamless, gentle textile, colors: {colores_en}, ocean-inspired sports fabric texture"
    )
    print("🎨 Prompt final:", prompt)
    return prompt
