from sqlalchemy import String, ForeignKey, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from datetime import datetime



class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(30))

    def __repr__(self) -> str:
        return f"User(id={self.id!r}, name={self.name!r}"




class Thread(Base):
    __tablename__ = "thread"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))  # Optional: You can use this for thread title or leave it out.
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())

    # Relationship to messages
    messages: Mapped[list["Message"]] = relationship("Message", back_populates="thread")

    def __repr__(self) -> str:
        return f"Thread(id={self.id!r}, name={self.name!r}, created_at={self.created_at!r})"


class Message(Base):
    __tablename__ = "message"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    thread_id: Mapped[int] = mapped_column(ForeignKey("thread.id"))
    content: Mapped[str] = mapped_column(Text)  # Message content
    is_bot: Mapped[bool] = mapped_column(default=False)  # Flag to differentiate user and bot messages
    timestamp: Mapped[datetime] = mapped_column(default=datetime.now())

    # Relationships
    user: Mapped["User"] = relationship("User")
    thread: Mapped["Thread"] = relationship("Thread", back_populates="messages")

    def __repr__(self) -> str:
        return f"Message(id={self.id!r}, user_id={self.user_id!r}, thread_id={self.thread_id!r}, content={self.content!r}, is_bot={self.is_bot!r}, timestamp={self.timestamp!r})"
