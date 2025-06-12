from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import google.generativeai as genai
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import AIMessage, HumanMessage
from langchain.prompts import PromptTemplate

GEMINI_API_KEY = "AIzaSyAyVTjO609XFmaMBsXRBOpXBbOHEQ4lS6Q"
os.environ["GOOGLE_API_KEY"] = GEMINI_API_KEY
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.0-flash')

# ✅ LangChain Memory & Prompt
memory = ConversationBufferWindowMemory(k=6, return_messages=True)
post_prompt = PromptTemplate.from_template(
    """You are a helpful social media assistant bot.
Your job is to:
- Generate engaging posts when asked.
- Summarize long content when needed.

Context from conversation:
{chat_history}

User request:
{input}

Your response:"""
)

# ✅ LangChain Wrapper
class GeminiChatWrapper:
    def __init__(self, model, memory, prompt_template):
        self.model = model
        self.memory = memory
        self.prompt_template = prompt_template

    def run(self, user_input):
        self.memory.chat_memory.add_user_message(user_input)
        history = self.memory.chat_memory.messages
        formatted_history = "\n".join([
            f"{'User' if isinstance(msg, HumanMessage) else 'Bot'}: {msg.content}"
            for msg in history
        ])
        final_prompt = self.prompt_template.format(
            chat_history=formatted_history,
            input=user_input
        )
        response = self.model.generate_content(final_prompt).text
        self.memory.chat_memory.add_ai_message(response)
        return response

chatbot = GeminiChatWrapper(model, memory, post_prompt)

# ✅ FastAPI App
app = FastAPI()

# ✅ CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Request model
class PromptRequest(BaseModel):
    prompt: str

@app.post("/generate")
def generate_post(request: PromptRequest):
    response = chatbot.run(request.prompt)
    return {"response": response}
