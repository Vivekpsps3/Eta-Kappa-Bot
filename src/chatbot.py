from dotenv import load_dotenv
import os
import requests

import google.generativeai as genai

class Gemini:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model_name = "gemini-2.0-flash-exp"
        self._configure_model()
        self._initialize_messages()

    def _configure_model(self):
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(self.model_name)

    def _initialize_messages(self):
        self.messages = [
            {
                'role': 'model',
                'parts': [
                    "You are a helpful Discord bot. You are here to help answer questions and provide information. Your name is Thinkerbot."
                ]
            }
        ]

    def request(self, text):
        response = self.model.generate_content(text)
        return response.text

    def chat(self, text):
        if len(self.messages) > 20:
            self._initialize_messages()
            addition = "The chat was cleared due to excessive length. \n"
        else:
            addition = (
                f"Convo continued.({len(self.messages)}). Chat will be cleared at 20.\n"
                if len(self.messages) > 15 else ""
            )

        self.messages.append({'role': 'user', 'parts': [text]})
        response = self.model.generate_content(self.messages)
        self.messages.append({'role': 'model', 'parts': [response.text]})
        return addition + response._result.candidates[0].content.parts[0].text

    def clear(self):
        self._initialize_messages()

class ChatVivek:
        def __init__(self):
            load_dotenv()
            self.api_key = os.getenv("CHAT_VIVEKP_API_KEY")
            self.endpoint = "https://chat.vivekpanchagnula.com/api/chat/completions"
            self.model_name = "hf.co/unsloth/gemma-3n-E4B-it-GGUF:Q8_K_XL"
            self._initialize_messages()

        def _initialize_messages(self):
            self.messages = [
                {
                    'role': 'system',
                    'content': "You are a helpful assistant."
                }
            ]

        def chat(self, text):
            if len(self.messages) > 20:
                self._initialize_messages()
                addition = "The chat was cleared due to excessive length. \n"
            else:
                addition = (
                    f"Convo continued.({len(self.messages)}). Chat will be cleared at 20.\n"
                    if len(self.messages) > 15 else ""
                )

            self.messages.append({'role': 'user', 'content': text})
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            data = {
                "model": self.model_name,
                "messages": self.messages
            }
            response = requests.post(self.endpoint, headers=headers, json=data)
            reply = response.json()['choices'][0]['message']['content']
            self.messages.append({'role': 'assistant', 'content': reply})
            return addition + reply

        def clear(self):
            self._initialize_messages()
        
if __name__ == "__main__":
    # gemini = Gemini()
    # print(gemini.request("What is the capital of Nigeria?"))

    chat_vivek = ChatVivek()
    print(chat_vivek.chat("What is the capital of Nigeria?"))