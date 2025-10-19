from vertexai.preview.generative_models import GenerativeModel
import vertexai
import os

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")

# Vertex configuration
vertexai.init(project=PROJECT_ID, location=LOCATION)

model = GenerativeModel("gemini-2.5-pro")

async def ask_gemini(prompt: str):
    response = model.generate_content(prompt)
    return response.text
