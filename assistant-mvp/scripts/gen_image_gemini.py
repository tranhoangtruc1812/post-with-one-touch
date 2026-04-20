import os
from google import genai
from dotenv import load_dotenv

load_dotenv()




def gen_image_text(prompt):
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    response = client.models.generate_content(
        model="gemini-2.0-flash-lite", 
        contents=prompt
    )
    return response.text

if __name__ == "__main__":
    print(gen_image_text("Explain why the sky is blue in one sentence."))