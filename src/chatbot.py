with open("gemini.env", "r") as f:
    gemini_api_key = f.read().strip()

model_name = "gemini-2.0-flash-exp"

class gemini():
    def __init__(self):
        import google.generativeai as genai
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel(model_name)
        messages = [
                    {'role':'model',
                    'parts': ["You are a helpful Discord bot. You are here to help answer questions and provide information. Your name is Thinkerbot."]}
                    ]
        self.messages = messages
        self.model = model

    def request(self, text):
        response = self.model.generate_content(text)
        response = response.text
        return response
    
    def chat(self, text):
        #length check
        if len(self.messages) > 20:
            self.messages = [
                        {'role':'model',
                        'parts': ["You are a helpful Discord bot. You are here to help answer questions and provide information. Your name is Thinkerbot."]}
                        ]
            addition = "The chat was cleared due to excessive length. \n"
        else:
            if len(self.messages) > 15:
                addition = "Convo continued.("+str(len(self.messages))+"). Chat will be cleared at 20.\n"
            else:
                addition = ""
        self.messages.append({'role':'user', 'parts':[text]})
        response = self.model.generate_content(self.messages)
        self.messages.append({'role':'model', 'parts':[response.text]})
        response = addition + response._result.candidates[0].content.parts[0].text
        return response
    
    def clear(self):
        self.messages = [
                    {'role':'model',
                    'parts': ["You are a helpful Discord bot. You are here to help answer questions and provide information. Your name is Thinkerbot."]}
                    ]

if __name__ == "__main__":
    gemini = gemini()
    print(gemini.request("What is the capital of Nigeria?"))