import json
from typing import Optional

from fastapi import HTTPException
from groq import Groq
from pydantic import BaseModel
from pymongo import MongoClient

from response import ResponseT, Code, Status


class Location(BaseModel):
    lat: float
    lng: float


class NicerRequest(BaseModel):
    chat_room_id: Optional[str] = ""
    message: str
    user_agent: str
    location: Location


class NicerService:
    """
    Nicer will make your prompt nicer.
    """
    instruction = "You are an intelligent assistant whose task is to make user's prompt better to be consumed better by LLMs. Reply conscisely with directly the improved prompt."

    BASE_PATH = "/nicer"

    def __init__(self, client: Groq, mongo: MongoClient):
        self.client = client
        self.mongo = mongo

    def nice(self, request: NicerRequest):
        try:
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": self.instruction
                    },
                    {
                        "role": "user",
                        "content": json.dumps({
                            "message": request.message,
                            "location": {
                                "lat": request.location.lat,
                                "lng": request.location.lng
                            }
                        })
                    }
                ],
                model="llama-3.1-70b-versatile",
            )

            message = chat_completion.choices[0].message.content
            print(message)

            return ResponseT(
                code=Code.ok,
                status=Status.ok,
                data=message
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Bad request: {str(e)}")
