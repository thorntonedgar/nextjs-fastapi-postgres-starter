from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db_engine import get_db
from models import User, Message, Thread
import random

from seed import seed_user_if_needed

# Seed the database with a default user (if needed)
seed_user_if_needed()

app = FastAPI()

# Allow cross-origin requests from the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic model for creating a message
class MessageCreate(BaseModel):
    thread_id: int
    user_id: int
    content: str

    class Config:
        orm_mode = True

# Pydantic model for returning user and bot messages
class MessageResponse(BaseModel):
    user_message: MessageCreate
    bot_message: MessageCreate

# Pydantic model for returning messages in a thread
class MessageRead(BaseModel):
    id: int
    user_id: int
    content: str
    is_bot: bool

    class Config:
        orm_mode = True

# Function to generate a random bot response
def generate_bot_response(user_message: str) -> str:
    responses = [
        "Hello! How can I assist you today?",
        "That's interesting! Tell me more.",
        "I'm a bot, but I'm here to help!",
        "Could you please clarify that?",
        "Thank you for reaching out!",
        "42",
        "If you're reading this, it's too late.",
    ]
    return random.choice(responses)

# API endpoint to send a message and receive a bot response
@app.post("/messages/", response_model=MessageResponse)
async def send_message(message: MessageCreate, db: AsyncSession = Depends(get_db)):
    try:
        # Fetch the user who sent the message
        user = await db.execute(select(User).filter(User.id == message.user_id))
        user = user.scalar_one_or_none()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # Fetch the thread in which the message is sent
        thread = await db.execute(select(Thread).filter(Thread.id == message.thread_id))
        thread = thread.scalar_one_or_none()
        if thread is None:
            raise HTTPException(status_code=404, detail="Thread not found")

        # Create and store the user's message
        new_message = Message(
            user_id=message.user_id,
            thread_id=message.thread_id,
            content=message.content,
            is_bot=False
        )
        db.add(new_message)
        await db.commit()  # Commit the transaction

        # Generate and store the bot's response
        bot_response_content = generate_bot_response(message.content)
        bot_message = Message(
            user_id=message.user_id,  # Bot uses the same user_id
            thread_id=message.thread_id,
            content=bot_response_content,
            is_bot=True
        )
        db.add(bot_message)
        await db.commit()  # Commit the transaction

        # Prepare Pydantic responses
        user_message_pydantic = MessageCreate(
            thread_id=new_message.thread_id,
            user_id=new_message.user_id,
            content=new_message.content
        )
        bot_message_pydantic = MessageCreate(
            thread_id=bot_message.thread_id,
            user_id=bot_message.user_id,
            content=bot_message.content
        )

        # Return both user and bot messages
        return MessageResponse(user_message=user_message_pydantic, bot_message=bot_message_pydantic)

    except Exception as e:
        # Log any errors and return a 422 status
        return JSONResponse(
            status_code=422,
            content={"detail": str(e)}
        )

# API endpoint to fetch all messages in a thread
@app.get("/threads/{thread_id}/messages", response_model=list[MessageRead])
async def get_messages(thread_id: int, db: AsyncSession = Depends(get_db)):
    # Query all messages in the specified thread
    messages = await db.execute(select(Message).filter(Message.thread_id == thread_id).order_by(Message.id))
    messages_list = messages.scalars().all()

    if not messages_list:
        raise HTTPException(status_code=404, detail="No messages found for this thread")

    # Return the messages
    return [MessageRead(
        id=message.id,
        user_id=message.user_id,
        content=message.content,
        is_bot=message.is_bot
    ) for message in messages_list]

# API endpoint to get the current user (only one user exists)
class UserRead(BaseModel):
    id: int
    name: str

@app.get("/users/me", response_model=UserRead)
async def get_my_user(db: AsyncSession = Depends(get_db)):
    try:
        # Fetch the first user in the database
        result = await db.execute(select(User))
        user = result.scalars().first()

        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        # Return the user
        return UserRead(id=user.id, name=user.name)

    except Exception as e:
        # Handle any exceptions and return a 500 status
        raise HTTPException(status_code=500, detail=str(e))
