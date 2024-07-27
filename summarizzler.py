from bson import ObjectId
from fastapi import HTTPException
from groq import Groq
from pydantic import BaseModel
from pymongo import MongoClient
from pymongo.collection import ReturnDocument

from response import ResponseT, Code, Status


class SummarizzlerRequest(BaseModel):
    chat_room_id: str


class SummarizzlerService:
    """
    Summarizzler will try to summarize the whole convo when you trigger it.
    """
    BASE_PATH = "/summarizzler"

    def __init__(self, client: Groq, mongo: MongoClient):
        self.client = client
        self.mongo = mongo

    def summarize(self, chat_room_id: str) -> ResponseT:
        try:
            messages = self.mongo.get_database('test').get_collection('chatmessages').find({"chatRoomId": ObjectId(chat_room_id)})

            to_summarize = []
            to_summarize.append(
                {
                    "role": "system",
                    "content": "You are a summarizer assistant. Summarize a LLM convo within 2-8 word as a title with concise meaning. Output with just the final title without apostrophe."
                })

            for m in messages:
                lala = {"role": m.get('role'), "content": m.get('message')}
                print(lala)
                to_summarize.append(lala)

            chat_completion = self.client.chat.completions.create(
                messages=to_summarize,
                # The language model which will generate the completion.
                model="llama-3.1-8b-instant"
            )

            summary = chat_completion.choices[0].message.content

            document = self.mongo.get_database('test').get_collection('chatrooms').find_one_and_update(
                filter={"_id":ObjectId(chat_room_id)},
                update={'$set': {'summary': summary}},
                return_document=ReturnDocument.AFTER
            )

            if document:
                return ResponseT(
                    code=Code.ok,
                    status=Status.ok,
                    data="OK"
                )
            else:
                raise HTTPException(status_code=404, detail="Chat room not found")

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Bad request: {str(e)}")

