# flask_api/test_img.py
import os, json, base64, io, pathlib, argparse
from datetime import datetime
import requests
from PIL import Image

def save_b64_to_jpg(b64: str, outdir="outputs", prefix="salida"):
    pathlib.Path(outdir).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    path = pathlib.Path(outdir) / f"{prefix}_{ts}.jpg"
    raw = base64.b64decode(b64)
    img = Image.open(io.BytesIO(raw)).convert("RGB")
    img.save(path, format="JPEG", quality=95)
    return str(path)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", default=os.environ.get("BACKEND_URL", "http://localhost:5000"),
                        help="URL base del backend Flask")
    parser.add_argument("--width", type=int, default=768)
    parser.add_argument("--height", type=int, default=768)
    parser.add_argument("--steps", type=int, default=26)
    parser.add_argument("--cfg", type=float, default=7.0)
    parser.add_argument("--preset", choices=["purple_vneck", "green_round"], default="purple_vneck",
                        help="Elige un prompt predefinido")
    args = parser.parse_args()

    # ---------- PROMPTS ----------
    if args.preset == "purple_vneck":
        prompt = (
            "front view centered high-quality product mockup of a sports t-shirt only, "
            "white base with purple gradient panels and geometric diagonal strokes and paint splatter accents, "
            "purple v-neck collar trim, short sleeves with purple cuffs, "
            "polyester athletic fabric, realistic texture, soft studio lighting, "
            "clean seamless plain white background, soft shadow under the shirt, sharp focus, only the shirt"
        )
        negative_prompt = (
            "person, human, mannequin, torso, body, arms, hands, head, legs, skin, "
            "hanger, text, watermark, logo text, brand, blurry, lowres, artifacts, deformed, extra limbs"
        )
    else:  # "green_round" — tu prompt original en verde
        prompt = (
            "in center high quality mockup of a sports t-shirt only, white color, green abstract details, "
            "round green neck, short sleeves with green trim, small central logo, red and white flag on left sleeve, "
            "displayed alone, centered, plain white background, no human, no mannequin, only the shirt"
        )
        negative_prompt = (
            "person, arms, hands, head, mannequin, human, skin, face, body, extra limbs, blurry, model"
        )
    # -----------------------------

    url = f"{args.backend.rstrip('/')}/api/ia/generar"
    payload = {
        "prompt": prompt,
        "negative_prompt": negative_prompt,
        "width": args.width,
        "height": args.height,
        "steps": args.steps,
        "guidance_scale": args.cfg
    }

    print("-> POST", url)
    print("Payload:", json.dumps({k: v for k, v in payload.items() if k not in ["prompt","negative_prompt"]}, ensure_ascii=False))
    r = requests.post(url, json=payload, timeout=300)
    print("status:", r.status_code)
    print("snippet:", r.text[:180], "...\n")

    j = r.json()
    if j.get("ok"):
        path = save_b64_to_jpg(j["image_base64"])
        print(f"✅ Imagen guardada en: {path}")
        print(f"Proveedor: {j.get('meta', {}).get('provider')}")
    else:
        print("❌ Error:\n", json.dumps(j, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
