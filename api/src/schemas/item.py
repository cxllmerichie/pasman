from typing import Optional
from apidevtools.simpleorm import Schema, Relation
from datetime import datetime
from apidevtools.media import imgproc
from pydantic import Field
from apidevtools.utils import now_tz_naive

from . import field
from . import attachment
from ..const import images


class ItemBase(Schema):
    __tablename__ = 'item'
    __noupdate__ = ['created_at']

    icon: Optional[str | bytes] = Field(default=None)
    title: str = Field(default=..., min_length=1, max_length=20)
    description: Optional[str] = Field(default=None, max_length=50)
    expires_at: Optional[datetime] = Field(default=None)
    modified_at: datetime = Field(default=None)
    created_at: datetime = Field(default=None)
    is_favourite: bool = Field(default=False)

    async def into_db(self) -> Schema:
        self.title = self.title.capitalize()
        if not self.icon:
            text = self.title[0]
            if not (icon := await images.get(text)):
                icon = imgproc.default(text).bytes
                await images.set(text, icon)
            self.icon = icon
        else:  # icon will be passed as string, as bytes is not json serializable
            self.icon = imgproc.crop(eval(self.icon)).bytes
        if not self.created_at:
            self.created_at = now_tz_naive()
        return self

    async def from_db(self) -> Schema:
        self.icon = str(self.icon)
        return self


class ItemCreate(ItemBase):
    ...


class ItemCreateCrud(ItemBase):
    category_id: int = Field(default=...)


class Item(ItemCreateCrud):
    id: int = Field(default=...)

    fields: list[field.Field] = Field(default=[])
    attachments: list[attachment.Attachment] = Field(default=[])

    def relations(self) -> list[Relation]:
        return [
            Relation(Item, 'fields', field.Field, dict(item_id=self.id)),
            Relation(Item, 'attachments', attachment.Attachment, dict(item_id=self.id))
        ]
