
import json
from typing import Optional

from groq import Groq
from pydantic import BaseModel

from response import ResponseT, Code, Status


class Location(BaseModel):
    lat: float
    lng: float


class NicerRequest(BaseModel):
    """
    Request class for Happy.
    """
    thread_id: Optional[str] = ""
    message: str
    user_agent: str
    location: Location

    def dump_me(self):
        return {
            "thread_id": self.thread_id,
            "message": self.message,
            "user_agent": self.user_agent,
            "location": {
                "lat": self.location.lat,
                "lng": self.location.lng
            }
        }


class NicerService:
    prompt = "You are a helpful assistant who can create a better prompt for LLM to consume, given an initial request description."

    def __init__(self):
        self.client = Groq(
            api_key='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'
        )
        self.BASEPATH = "/nicer/_chat"

    def chat(self, content: str):
        chat_completion = self.client.chat.completions.create(
            messages=[
                # {
                #     "role": "system",
                #     "content":
                # },
                {
                    "role": "user",
                    "content": json.dumps(content),
                }
            ],
            model="llama-3.1-8b-instant",
        )

        message = chat_completion.choices[0].message.content
        print(message)

        return ResponseT(
            code=Code.ok,
            status=Status.ok,
            data=message
        )
