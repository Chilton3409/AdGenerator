# services.py
import os
import logging

from google import genai
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')
api = genai.Client(api_key=GEMINI_API_KEY)
class AdvertisingAssistantService:
    def __init__(self):
        
        self.api = api
        self.model = "gemini-2.5-flash"
    def generate_advertisement(self, prompt):
        try:
            refactored_prompt =  self.refactor_prompt(prompt)
            advertisement =  self.get_gemini_ai_insights(meta_ai_text=f"generate a new text-based advertisement based on: {refactored_prompt}. Only text no images.")
            return advertisement
        except Exception as e:
            logging.exception(msg=e)
            
    def refactor_prompt(self, prompt: str) -> str:
        try:
            refactored_prompt = self.get_gemini_ai_insights(meta_ai_text=f"refactor this prompt from the user for advertisement generation: {prompt}")
            return refactored_prompt
        except Exception as e:
            logging.exception(msg=e)
            
    def get_gemini_ai_insights(self, meta_ai_text):
        try:
            response = self.api.models.generate_content(
                model=self.model,
                contents=meta_ai_text
            )
            if response and response.text:
                return response.text
        except Exception as e:
            logging.exception(msg=e)