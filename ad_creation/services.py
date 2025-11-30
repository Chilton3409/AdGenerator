# services.py
import os
import logging
from meta_ai_api import MetaAI
meta_ai_api_key = os.environ.get("META_AI_TOKEN")
api = MetaAI(meta_ai_api_key)
class AdvertisingAssistantService:
    def __init__(self):
        
        self.api = api
        
    def generate_advertisement(self, prompt):
        try:
            refactored_prompt =  self.refactor_prompt(prompt)
            advertisement =  self.get_meta_ai_insights(meta_ai_text=f"generate a new text-based advertisement based on: {refactored_prompt}. Only text no images.")
            return advertisement
        except Exception as e:
            logging.exception(msg=e)
            
    def refactor_prompt(self, prompt: str) -> str:
        try:
            refactored_prompt = self.get_meta_ai_insights(meta_ai_text=f"refactor this prompt from the user for advertisement generation: {prompt}")
            return refactored_prompt
        except Exception as e:
            logging.exception(msg=e)
            
    def get_meta_ai_insights(self, meta_ai_text):
        try:
            response = self.api.prompt(message=meta_ai_text, new_conversation=False)
            return response['message']
        except Exception as e:
            logging.exception(msg=e)