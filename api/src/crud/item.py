from apidevtools.utils import INF, now_tz_naive

from .. import schemas
from ..const import db


async def create_item(category_id: int, item: schemas.ItemCreate) -> schemas.Item:
    item = schemas.ItemCreateCrud(**dict(item), category_id=category_id)
    db_item = await db.insert(item, schemas.Item)
    return db_item


async def get_item(item_id: int, schema: type = schemas.Item, depth: int = 0) -> schemas.Item | None:
    query, args = f'SELECT * FROM "item" WHERE "id" = $1;', (item_id, )
    db_item = await (await db.select(query, args, schema, rel_depth=depth)).first()
    return db_item


async def get_items(category_id: int, limit: int = INF, offset: int = 0, schema: type = schemas.Item, depth: int = 0) -> list[schemas.Item]:
    query, args = f'SELECT * FROM "item" WHERE "category_id" = $1 ORDER BY "is_favourite" DESC, "title", "description" LIMIT $2 OFFSET $3;', (category_id, limit, offset)
    db_items = await (await db.select(query, args, schema, rel_depth=depth)).all()
    return db_items


async def update_item(item_id: int, item: schemas.ItemCreate, depth: int = 0) -> schemas.Item:
    item.modified_at = now_tz_naive()
    db_item = await (await db.update(item, dict(id=item_id), schemas.Item, rel_depth=depth)).first()
    return db_item


async def delete_item(item_id: int) -> schemas.Item:
    db_item = await (await db.delete(dict(id=item_id), schemas.Item, 'item')).first()
    return db_item
