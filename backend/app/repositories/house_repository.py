"""House repository — plain DB access, no business rules."""
from sqlalchemy.orm import Session

from app.models.house import House


def get_by_id(db: Session, house_id: int) -> House | None:
    return db.query(House).filter(House.id == house_id).first()


def get_by_house_code(db: Session, house_code: str) -> House | None:
    return db.query(House).filter(House.house_code == house_code).first()


def get_or_create(db: Session, house_code: str, block: str) -> House:
    house = get_by_house_code(db, house_code)
    if house:
        return house
    house = House(house_code=house_code, block=block)
    db.add(house)
    db.flush()
    return house
