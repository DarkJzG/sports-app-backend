# flask_api/controlador/control_ia_prendas.py
import base64, io, requests
from bson import ObjectId
import cloudinary.uploader
from flask import current_app

from flask_api.funciones.normalizar import _norm_cat

from flask_api.controlador.control_ficha_tecnica import (

    construir_ficha_tecnica_detallada)
from flask_api.modelo.modelo_ia_prendas import guardar_prenda
from flask_api.modelo.modelo_ficha_tecnica import guardar_ficha


from flask_api.componente.traducciones import (
    MAPEO_ATRIBUTOS_ES,
    TRADUCCION_BASICA_INVERSA)

NEGATIVE_PROMPT = (
    "person, people, human, man, woman, mannequin, dummy, model, arms, hands, "
    "fingers, faces, limbs, hanger, background scene, shoes, accessories, "
    "folded clothes, cropped, wrinkles, blur, shadows, watermark, text, logos"
)




PROMPTS_CATEGORIA = {
    "camiseta": {
        "base": "Centered front view, athletic slim-fit sports T-shirt",
        "tail": "professional studio lighting, product catalog photo, plain white background, isolated background, no wrinkles, sharp focus, no logos, no text, no limbs, just the T-shirt",
    },
    "pantalon": {
        "base": "Centered front view, sports jogger pants with elastic waistband and tapered fit",
        "tail": "professional studio lighting, product catalog photo, plain white background, isolated background, no wrinkles, sharp focus, no logos, no text, no limbs, just the pants",
    },
    "chompa": {
        "base": (
            "Centered front view, full hoodie jacket, symmetrical, "
            "athletic fit, floating isolated, product shot"
        ),
        "tail": (
            "flat lay photo, professional studio lighting, product catalog image, "
            "plain white background, no mannequin, no hanger, no models, "
            "sharp focus, sportswear fabric texture, no text, no logos, "
            "only the hoodie jacket"
        ),
    },
    "conjunto_interno": {
        "base": (
            "Centered front view, two-piece sportswear set, symmetrical, isolated"
            "and shorts, displayed side by side, symmetrical, isolated"
        ),
        "tail": (
            "flat lay photo, product catalog image, plain white background, "
            "floating, no mannequin, no hanger, no models, "
            "sharp focus, sportswear fabric texture, no text, no logos, "
            "only the T-shirt and shorts"
        ),
    },
    "conjunto_externo": {
        "base": (
            "Centered front view, two-piece sportswear set: hoodie jacket and jogger pants, "
            "displayed side by side, symmetrical, isolated"
        ),
        "tail": (
            "flat lay photo, product catalog image, plain white background, "
            "floating, no mannequin, no hanger, no models, "
            "sharp focus, sportswear fabric texture, no text, no logos, "
            "only the hoodie jacket and jogger pants"
        ),
    },
}


def traducir_atributos_es(atributos):
    traducidos = {}
    for clave, valor in atributos.items():
        if isinstance(valor, list):
            traducidos[clave] = [MAPEO_ATRIBUTOS_ES.get(v, v) for v in valor]
        else:
            traducidos[clave] = MAPEO_ATRIBUTOS_ES.get(valor, valor)
    return traducidos



def traducir_prompt_en_es(prompt_en: str) -> str:
    prompt_es = prompt_en
    for en, es in TRADUCCION_BASICA_INVERSA.items():
        prompt_es = prompt_es.replace(en, es)
    return prompt_es


def calcular_precio_final(categoria_id, atributos):
    db = current_app.mongo.db
    mano = None
    try:
        mano = db.mano_obra.find_one({"categoria_id": ObjectId(categoria_id)})
    except Exception:
        pass

    if not mano:
         mano = db.mano_obra.find_one({"categoria_id": str(categoria_id)})

    if not mano:
        return {"costo": 0, "precio": 0, "precio_mayor": 0}

    # costos base de mano de obra
    insumos = float(mano.get("insumosTotal", 0))
    mano_prenda = float(mano.get("mano_obra_prenda", 0))

    # tela (ej: 1.20 m × $1.50)
    metros_tela = 1.20
    precio_metro = 1.50
    costo_tela = metros_tela * precio_metro

    # sublimado/bordado si el diseño lo requiere
    costo_diseno = 0
    if atributos.get("diseno") in ["sublimado", "bordado"]:
        costo_diseno = 4.0

    # total de costos
    costo = insumos + mano_prenda + costo_tela + costo_diseno

    # precio final = costo + ganancia
    ganancia = 3.0
    precio_venta = costo + ganancia

    # precio al mayor (ej. 10% descuento)
    precio_mayor = precio_venta * 0.9

    return {
        "costo": round(costo, 2),
        "precio": round(precio_venta, 2),
        "precio_mayor": round(precio_mayor, 2)
    }


# --------------------------------------
# Costos
# --------------------------------------
def calcular_costo_prenda(categoria_prd, atributos):
    base_costos = {
        "camiseta": 5.0,
        "pantalon": 8.0,
        "chompa": 12.0,
        "conjunto_interno": 15.0,
        "conjunto_externo": 20.0,
    }
    costo = base_costos.get(categoria_prd, 10.0)

    tela = atributos.get("tela", "").lower()
    if tela == "poliéster":
        costo += 1
    elif tela == "algodón":
        costo += 2

    if atributos.get("diseno") in ["sublimado", "bordado"]:
        costo += 3

    return round(costo, 2)


# --------------------------------------
# PROMPT en inglés → traducido a español
# --------------------------------------
def generar_prompt(categoria_prd, atributos):
    cat = _norm_cat(categoria_prd)

    # Mapea nombres comunes (por si te llegan "Camiseta" con mayúscula)
    alias = {
        "camiseta": "camiseta",
        "pantalon": "pantalon",
        "pantalón": "pantalon",
        "chompa": "chompa",
        "conjunto interno": "conjunto_interno",
        "conjunto_externo": "conjunto_externo",
    }
    cat = alias.get(cat, cat)

    # Si tenemos prompt base para esa categoría, lo usamos
    if cat in PROMPTS_CATEGORIA:
        estilo = atributos.get("estilo", "")
        color1 = atributos.get("color1", "")
        color2 = atributos.get("color2", "")
        diseno = atributos.get("diseno", "")
        cuello_capucha = atributos.get("cuelloCapucha", "")
        cierre = atributos.get("cierre", "")
        bolsillos = atributos.get("bolsillos", [])
        manga = atributos.get("manga", "")
        tela = atributos.get("tela", "")
        genero = atributos.get("genero", "")

        estiloAvanzado = atributos.get("estiloAvanzado", "")
        ubicacion = atributos.get("ubicacion", "")
        detalles = atributos.get("detalles", [])
        acabado = atributos.get("acabado", "")

        base = PROMPTS_CATEGORIA[cat]["base"]
        tail = PROMPTS_CATEGORIA[cat]["tail"]

        # Arrancamos con el "base" y añadimos color/tela/estilo si existen
        partes_en = [base]

        # Color principal + tela + estilo (si existen)
        # Ej: "in blue polyester fabric, sports style"
        comp = []
        if color1:
            comp.append(f"in {color1}")
        if tela:
            comp.append(f"{tela} fabric")
        if estilo:
            comp.append(estilo)
        if comp:
            partes_en.append(", ".join(comp))

        # Diseño secundario/color2/ubicación (si aplica)
        if diseno and color2:
            # Ej: "featuring a red geometric design on chest only"
            partes_en.append(
                f"featuring a {color2} {diseno} design{(' on ' + ubicacion) if ubicacion else ''}"
            )
        elif color2:
            partes_en.append(f"with {color2} details")

        # Campos específicos que aportan a la forma
        if cuello_capucha:
            partes_en.append(cuello_capucha)
        if cierre:
            partes_en.append(cierre)
        if bolsillos:
            partes_en.append(bolsillos)
        if manga:
            partes_en.append(manga)
        if genero:
            partes_en.append(f"for {genero}")
        if estiloAvanzado:
            partes_en.append(estiloAvanzado)
        if detalles:
            partes_en.append(", ".join(detalles))
        if acabado:
            partes_en.append(acabado)
        if cat == "conjunto_interno":
            parteSuperior = atributos.get("parteSuperior", "")
            parteInferior = atributos.get("parteInferior", "")
            cintura = atributos.get("cintura", "")

            if parteSuperior:
                partes_en.append(f"top garment: {parteSuperior}")
            if parteInferior:
                partes_en.append(f"bottom garment: {parteInferior}")
            if cintura:
                partes_en.append(cintura)

        if cat == "conjunto_externo":
            capucha = atributos.get("capucha", "")
            cierre = atributos.get("cierre", "")
            bolsillos_chompa = atributos.get("bolsillosChompa", "")
            detalles_chompa = atributos.get("detallesChompa", [])

            ajuste_pantalon = atributos.get("ajustePantalon", "")
            cintura_pantalon = atributos.get("cinturaPantalon", "")
            bolsillos_pantalon = atributos.get("bolsillosPantalon", "")
            detalles_pantalon = atributos.get("detallesPantalon", [])

            if capucha:
                partes_en.append(capucha)
            if cierre:
                partes_en.append(cierre)
            if bolsillos_chompa:
                partes_en.append(bolsillos_chompa)
            if detalles_chompa:
                partes_en.append(", ".join(detalles_chompa))

            if ajuste_pantalon:
                partes_en.append(ajuste_pantalon)
            if cintura_pantalon:
                partes_en.append(cintura_pantalon)
            if bolsillos_pantalon:
                partes_en.append(bolsillos_pantalon)
            if detalles_pantalon:
                partes_en.append(", ".join(detalles_pantalon))



        # Cola de calidad fotográfica y limpieza
        partes_en.append(tail)

        prompt_en = ", ".join(partes_en)
        prompt_es = traducir_prompt_en_es(prompt_en)
        return prompt_es, prompt_en

    # 🔙 fallback actual (si la categoría no está mapeada)
    prompt_en = f"{categoria_prd} with attributes: {atributos}"
    prompt_es = traducir_prompt_en_es(prompt_en)
    return prompt_es, prompt_en



def generar_descripcion_es(categoria_prd, atributos_es):
    partes = [f"{categoria_prd.capitalize()} de {atributos_es.get('tela', '')} con estilo {atributos_es.get('estilo', '')}"]

    color1 = atributos_es.get("color1")
    color2 = atributos_es.get("color2")
    if color1 and color2:
        partes.append(f"de color {color1} con {color2}")
    elif color1:
        partes.append(f"de color {color1}")

    diseno = atributos_es.get("diseno")
    if diseno:
        partes.append(f"con un diseño de {diseno}")

    estiloAvanzado = atributos_es.get("estiloAvanzado")
    if estiloAvanzado:
        partes.append(estiloAvanzado)

    acabado = atributos_es.get("acabado")
    if acabado:
        partes.append(f"con acabado {acabado}")

    cuello_capucha = atributos_es.get("cuelloCapucha")
    if cuello_capucha:
        partes.append(f"con {cuello_capucha}")

    cierre = atributos_es.get("cierre")
    if cierre:
        partes.append(cierre)

    bolsillos = atributos_es.get("bolsillos")
    if bolsillos:
        partes.append(f"con {bolsillos}")

    if categoria_prd == "conjunto_interno":
        parteSuperior = atributos_es.get("parteSuperior")
        parteInferior = atributos_es.get("parteInferior")
        cintura = atributos_es.get("cintura")

        if parteSuperior:
            partes.append(f"prenda superior: {parteSuperior}")
        if parteInferior:
            partes.append(f"prenda inferior: {parteInferior}")
        if cintura:
            partes.append(f"con {cintura}")

    if categoria_prd == "conjunto_externo":
        capucha = atributos_es.get("capucha")
        cierre = atributos_es.get("cierre")
        bolsillos_chompa = atributos_es.get("bolsillosChompa")
        detalles_chompa = atributos_es.get("detallesChompa", [])

        ajuste_pantalon = atributos_es.get("ajustePantalon")
        cintura_pantalon = atributos_es.get("cinturaPantalon")
        bolsillos_pantalon = atributos_es.get("bolsillosPantalon")
        detalles_pantalon = atributos_es.get("detallesPantalon", [])

        if capucha:
            partes.append(f"chompa {capucha}")
        if cierre:
            partes.append(f"{cierre}")
        if bolsillos_chompa:
            partes.append(f"con {bolsillos_chompa}")
        if detalles_chompa:
            partes.append(f"con {', '.join(detalles_chompa)}")

        if ajuste_pantalon:
            partes.append(f"pantalón {ajuste_pantalon}")
        if cintura_pantalon:
            partes.append(f"con {cintura_pantalon}")
        if bolsillos_pantalon:
            partes.append(f"con {bolsillos_pantalon}")
        if detalles_pantalon:
            partes.append(f"con {', '.join(detalles_pantalon)}")


    return " ".join(partes)





# --------------------------------------
# Generar imágenes
# --------------------------------------
def generar_imagen(categoria_id, categoria_prd, atributos, user_id):
    STABLE_URL = current_app.config.get("STABLE_URL", "http://127.0.0.1:7860")
    prompt_es, prompt_en = generar_prompt(categoria_prd, atributos)

    # Traducción de atributos
    atributos_es = traducir_atributos_es(atributos)
    descripcion_es = generar_descripcion_es(categoria_prd, atributos_es)

    payload = {
        "prompt": prompt_en,
        "negative_prompt": NEGATIVE_PROMPT,
        "steps": 30,
        "sampler_name": "DPM++ 2M",
        "cfg_scale": 7,
        "width": 800,
        "height": 800,
        "batch_size": 1
    }

    current_app.logger.info(f"📡 POST {STABLE_URL}/sdapi/v1/txt2img")
    try:
        response = requests.post(f"{STABLE_URL}/sdapi/v1/txt2img", json=payload, timeout=120)
        response.raise_for_status()
        r = response.json()
        images = r.get("images", [])

        if not images:
            return {"error": "No se generaron imágenes"}

        # Subir primera a Cloudinary
        image_base64 = images[0]
        image_data = base64.b64decode(image_base64)
        image_file = io.BytesIO(image_data)
        upload_result = cloudinary.uploader.upload(image_file, folder="prendasIA")
        image_url = upload_result.get("secure_url")

        ficha_tecnica_detallada = construir_ficha_tecnica_detallada(
            categoria_prd, 
            atributos_es, 
            {"delantera": image_url}
        )

        precios = calcular_precio_final(categoria_id, atributos_es)


        ficha_doc = {
            "user_id": ObjectId(user_id),
            "prenda_id": None,  # lo actualizamos luego
            "categoria": categoria_prd,
            "modelo": ficha_tecnica_detallada.get("modelo"),
            "descripcion": ficha_tecnica_detallada.get("descripcion"),
            "caracteristicas": ficha_tecnica_detallada.get("caracteristicas", {}),
            "imagenes": ficha_tecnica_detallada.get("imagenes", {}),
            "piezas": ficha_tecnica_detallada.get("piezas", []),
            "insumos": ficha_tecnica_detallada.get("insumos", []),
            "logo": ficha_tecnica_detallada.get("logo", {}),
            "especificaciones": ficha_tecnica_detallada.get("especificaciones", []),
        }

        ficha_id = guardar_ficha(ficha_doc)

        doc = {
            "user_id": ObjectId(user_id),
            "categoria_prd": categoria_prd,
            "atributos": atributos_es,
            "prompt_es": prompt_es,
            "descripcion_es": descripcion_es,
            "prompt_en": prompt_en,
            "imageUrl": image_url,
            "ficha_tecnica_detallada": ficha_tecnica_detallada,  # opcional
            "ficha_id": ficha_id,
            "costo": precios["costo"],
            "precio_venta": precios["precio"],
            "precio_mayor": precios["precio_mayor"],
            "estado": "generado"
        }
        inserted_id = guardar_prenda(doc)

        current_app.mongo.db.fichas_tecnicas.update_one(
            {"_id": ObjectId(ficha_id)},
            {"$set": {"prenda_id": ObjectId(inserted_id)}}
        )
        return {
            "id": inserted_id,
            "ficha_id": ficha_id,
            "descripcion": descripcion_es,
            "imageUrl": image_url,
            "costo": precios["costo"],
            "precio_venta": precios["precio"],
            "precio_mayor": precios["precio_mayor"],
        }

    except Exception as e:
        return {"error": f"Error al generar imagen en Stable Diffusion: {str(e)}"}

