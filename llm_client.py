import os
from groq import Groq
from dotenv import load_dotenv
load_dotenv()   

class GroqClient:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables")

            cls._instance = super().__new__(cls)
            cls._instance.client = Groq(api_key=groq_api_key)
            cls._instance.model = "llama-3.3-70b-versatile"  
        return cls._instance

    def invoke(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
        )
        return response.choices[0].message.content.strip()


groq_client = GroqClient()
