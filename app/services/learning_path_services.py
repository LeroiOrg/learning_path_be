import json
from fastapi import HTTPException
from app.services.ai_services import ask_gemini
import re

async def process_file_logic(request, credits: int):
    """
    Lógica para procesar un archivo y obtener temas principales.
    """
    
    if credits < 1:
        raise HTTPException(
            status_code=402, detail="Créditos insuficientes para la acción"
        )
    
    full_prompt = (
        f"Eres un experto en la extracción de los 3 temas principales de los cuales se pueden generar una ruta de "
        f"aprendizaje de un archivo. El archivo tiene el siguiente nombre {request.fileName} y este es el contenido: {request.fileBase64}. Quiero que el formato de la respuesta sea una"
        f"lista con únicamente los 3 temas principales y nada más, es decir: [\"tema1\", \"tema2\", \"tema3\"] Si dentro del documento hay estas palabras: DROGAS, BOMBAS, TRATA DE PERSONAS, PORNOGRAFÍA "
        f"devuelve BLOQUEADO SOLO SI ENCUENTRAS ESAS PALABRAS, DE LO CONTRARIO RESPONDE con los temas principales del documento. "
    )

    themes = await ask_gemini(full_prompt)
    print("RESPUESTA DE LA IA", themes)
    match = re.search(r'```json(.*?)```', themes, re.DOTALL)
    if not match:
        raise HTTPException(status_code=400, detail="No se encontró bloque JSON en la respuesta de la IA")

    json_text = match.group(1).strip()

    try:
        themes = json.loads(json_text)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"JSON inválido extraído de la IA: {e}")

    response = {
        "themes": themes,
        "raw_response": themes 
    }
    credits -= 1
    return response


async def generate_roadmap_logic(request):
    """
    Lógica para generar la ruta de aprendizaje.
    """
    full_prompt = (
        f"Eres un experto en la creación de rutas de aprendizaje basadas en un tema específico. El tema principal es {request.topic}. "
        f"Quiero que el formato de la respuesta sea un diccionario anidado donde la clave sea el tema principal y los valores sean diccionarios de subtemas, "
        f"cada uno con su propia lista de subtemas adicionales. "
        f"Por ejemplo: '{{\"Subtema 1\": [\"Sub-subtema 1.1\", \"Sub-subtema 1.2\"], \"Subtema 2\": [\"Sub-subtema 2.1\", \"Sub-subtema 2.2\"]}}' con las comillas tal cual como te las di. "
        f"No me des información extra, solo quiero el diccionario anidado con los subtemas y sus sub-subtemas en orden de relevancia. MÁXIMO 6 SubtemaS, MÁXIMO 3 Sub-subtemas y MÍNIMO 1 Sub-subtema ."
        f"De lo que se genere , la longitud de cada subtema y sub-subtema debe ser MÁXIMO 55 caracteres."
    )

    response = await ask_gemini(full_prompt)
    print("RESPUESTA DE LA IA", response)
    parse_response = response.replace("json", "").replace("```", "")

    second_prompt = (
        f"Ahora con estos temas quiero que me devuelvas un diccionario donde la clave es cada uno de los temas, SUBTEMAS y SUB-SUBTEMAS, es decir, toda la informacion que encuentras en este diccionario: {parse_response} CON EL NOMBRE TAL CUAL COMO TE LO DOY y el valor será "
        f"el tiempo en parentecis que lleva aprender este tema junto con un resumen extenso de lo que trata el tema y un link REAL de internet y COMPLETAMENTE FUNCIONAL, que NO me redireccione a 404 para poder profundizar en el tema. Por ejemplo '{{\"Tema 1\": \"Tiempo para aprender, definción del tema y link de referencia\", \"Tema 2\": \"Tiempo para aprender, definción del tema y link de referencia\", \"Tema 3\": \"Tiempo para aprender, definción del tema y link de referencia\"}}' con las comillas tal cual como te las di."
        f"Dentro del título del TEMA, no quiero nada más que los título del tema sin NADA más. Además NO me des información extra al diccionario, y no quiero que dentro del texto me des elementos como saltos de línea"
    )

    second_response = await ask_gemini(second_prompt)
    parse_second_respone = second_response.replace("json", "").replace("```", "")

    return {"roadmap": parse_response, "extra_info": parse_second_respone}


async def generate_questions_logic(request):
    """
    Lógica para generar preguntas.
    """
    full_prompt = (
        f"Eres un experto en la creación de preguntas de verdadero o falso. Genera una lista de preguntas basadas en los siguientes temas e información: {request.topic}. "
        f"El formato de la respuesta debe ser exclusivamente una lista en formato JSON con objetos que contengan un 'enunciado' y una 'respuesta' booleana (true o false). "
        f"No incluyas ninguna otra información, explicaciones adicionales ni texto fuera del formato JSON. "
        f"\n\nEjemplo del formato de respuesta esperado:"
        f"[\n"
        f"  {{ \"enunciado\": \"Un DBMS es el software que permite la interacción con una base de datos.\", \"respuesta\": true }},\n"
        f"  {{ \"enunciado\": \"El modelo NoSQL es ideal únicamente para datos estructurados.\", \"respuesta\": false }},\n"
        f"  {{ \"enunciado\": \"SQL es el lenguaje estándar para interactuar con bases de datos NoSQL.\", \"respuesta\": false }}\n"
        f"]\n"
        f"Genera al menos 5 preguntas y un máximo de 10. Cada pregunta debe ser clara, concisa y directamente relacionada con el tema."
    )

    response = await ask_gemini(full_prompt)
    print("RESPUESTA DE LA IA", response)
    parse_response = response.replace("json", "").replace("```", "")

    return parse_response

async def related_topics_logic(request):
    """
    Lógica para obtener temas relacionados a un tema principal.
    """
    print("ESTO ES LO QUE LLEGA:", request)
    full_prompt = (
        f"Eres un experto en la generación de temas relacionados a un tema principal. "
        f"El tema principal es '{request.topic}'. Quiero que el formato de la respuesta sea una "
        f"lista JSON con únicamente MÁXIMO 6 temas relacionados y nada más, "
        f"es decir: [\"tema1\", \"tema2\", \"tema3\"]. "
        f"Cada tema debe tener una longitud máxima de 45 caracteres."
    )

    response = await ask_gemini(full_prompt)
    print("RESPUESTA DE LA IA", response)

    # limpiar ruido si viene con ```json ... ```
    clean_response = response.replace("json", "").replace("```", "").strip()

    try:
        topics = json.loads(clean_response)
    except Exception as e:
        print("Error parseando respuesta de la IA:", e)
        raise HTTPException(status_code=500, detail="Error procesando respuesta de IA")

    return {"related_topics": topics}

