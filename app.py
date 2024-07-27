import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, Depends, status
from groq import Groq
from pydantic import BaseModel
from pymongo import MongoClient

from nicer import NicerRequest, NicerService
from response import ResponseT
from summarizzler import SummarizzlerService, SummarizzlerRequest

app = FastAPI()
load_dotenv()

mongo = MongoClient(
    'mongodb+srv://mahesainsan:Bswl13cqZKsmMgnS@aiwan-db.dq43bti.mongodb.net/?retryWrites=true&w=majority&appName=aiwan-db')
nicer = NicerService()
summarizzler = SummarizzlerService(client=Groq(api_key=os.getenv('GROQ_API_KEY')), mongo=mongo)


def _get_nicer_service():
    return nicer


def _get_summarizzler_service():
    return summarizzler


@app.post(summarizzler.BASE_PATH, status_code=status.HTTP_200_OK)
def nicer_chat(request: SummarizzlerRequest,
               summarizzler_service: SummarizzlerService = Depends(_get_summarizzler_service)) -> ResponseT:
    return summarizzler_service.summarize(chat_room_id=request.chat_room_id)


@app.post(nicer.BASEPATH, status_code=status.HTTP_200_OK)
def nicer_chat(request: NicerRequest,
               nicer_service: NicerService = Depends(_get_nicer_service)) -> ResponseT:
    return nicer_service.chat(request.dump_me())
