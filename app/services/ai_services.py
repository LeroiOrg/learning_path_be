"""from vertexai.preview.generative_models import GenerativeModel
import vertexai
import os

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")

# Vertex configuration
vertexai.init(project=PROJECT_ID, location=LOCATION)

model = GenerativeModel("gemini-2.5-flash-lite")

async def ask_gemini(prompt: str):
    response = model.generate_content(prompt)
    return response.text
"""

from vertexai.preview.generative_models import GenerativeModel
import vertexai
import os

API_KEY = os.getenv("GOOGLE_API_KEY")
PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")

vertexai.init(api_key=API_KEY, project=PROJECT_ID, location=LOCATION)

async def ask_gemini(prompt: str, model: str = "gemini-2.5-flash"):
    model_instance = GenerativeModel(model)
    response = model_instance.generate_content(
        [prompt],
        generation_config={
            "temperature": 0.3,
            "max_output_tokens": 10000,
            "response_mime_type": "application/json"
        }
    )
    print("ESTA ES LA RESPUESTAAAAA", response)
    return response.text.strip()
