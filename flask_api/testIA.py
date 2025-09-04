import requests, base64, json

data = {
    "tipo": "camiseta deportiva",
    "color": "negro y púrpura",
    "cuello": "cuello redondo",
    "mangas": "manga corta",
    "tela": "poliéster transpirable",
    "patron": "líneas sutiles",
    "width": 768,
    "height": 768
}

r = requests.post("http://localhost:5000/api/ia/generar", json=data, timeout=300)
print("status:", r.status_code)
print("snippet:", r.text[:200], "...\n")

j = r.json()
if j.get("ok"):
    with open("salida.jpg", "wb") as f:
        f.write(base64.b64decode(j["image_base64"]))
    print("Guardado -> salida.jpg")
else:
    print("Error:", json.dumps(j, ensure_ascii=False, indent=2))
