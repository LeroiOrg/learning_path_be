import os
import vertexai
import openai
from google.auth import default, transport

PROJECT_ID = os.getenv("PROJECT_ID")
LOCATION = os.getenv("LOCATION")

vertexai.init(project=PROJECT_ID, location=LOCATION)

credentials, _ = default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
auth_request = transport.requests.Request()
credentials.refresh(auth_request)

client = openai.OpenAI(
    base_url=f"https://{LOCATION}-aiplatform.googleapis.com/v1beta1/projects/{PROJECT_ID}/locations/{LOCATION}/endpoints/openapi",
    api_key=credentials.token,
)

async def ask_gemini(prompt: str):
    response = client.chat.completions.create(
        model="google/gemini-2.0-flash-001",
        messages=[{"role": "user", "content": prompt}],
    )
    return response.choices[0].message.content
