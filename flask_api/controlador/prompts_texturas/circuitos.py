def build_prompt_circuitos(attr: dict) -> str:
    print("🎨 Entrando a build_prompt_circuitos con:", attr)
    colores_en = ', '.join(attr.get('colores', ['green', 'gray']))
    print("🎨 Colores en inglés:", colores_en)
    prompt = (
        f"Seamless circuit board pattern, modern texture, colors: {colores_en}, smooth textile, SciFi sportswear style"
    )
    print("🎨 Prompt final:", prompt)
    return prompt

