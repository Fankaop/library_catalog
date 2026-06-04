from datetime import datetime
import uuid

from sqlalchemy import JSON, Boolean, Integer, String, Text, func
from sqlalchemy.orm import Mapped,mapped_column
from sqlalchemy.dialects.postgresql import UUID
from ...core.database import Base

class Book(Base):
    """

    Модель книги.
    Представляет книгу в библиотеке с основной информацией:
    - название
    - автор
    - год издания
    - жанр
    - количество страниц
    Также поддерживает:
    - ISBN (уникальный идентификатор)
    - дополнительные данные (JSON)
    - временные метки создания и обновления

    """

    __tablename__ = 'books'
    
    book_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        index=True,
    )

    title: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
        index=True
    )

    author: Mapped[str] = mapped_column(
        String(300),
        index=True,
        nullable=False,
    )

    year: Mapped[int] = mapped_column(
        Integer,
        index=True,
        nullable=False,
    )

    genre: Mapped[str] = mapped_column(
        String(100),
        index=True,
        nullable=False,
    )

    pages: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    available: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        index=True,
        nullable=False,
    )

    isbn: Mapped[str | None] = mapped_column(
        String(20),
        unique=True,
        nullable=True,
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    extra: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(default=func.now())

    updated_at: Mapped[datetime] = mapped_column(
        default=func.now(),
        onupdate=func.now(),
    )

    def __repr__(self) -> str:
        return f'<Book(id={self.book_id}, title={self.title})>'