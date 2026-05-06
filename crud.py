from sqlalchemy.orm import Session
from models import Address
from schemas import AddressCreate


# Create Address
def create_address(db: Session, address: AddressCreate):
    db_address = Address(**address.model_dump())

    db.add(db_address)
    db.commit()
    db.refresh(db_address)

    return db_address


# Get All Addresses
def get_addresses(db: Session):
    return db.query(Address).all()


# Get Single Address
def get_address(db: Session, address_id: int):
    return db.query(Address).filter(Address.id == address_id).first()


# Update Address
def update_address(db: Session, address_id: int, address: AddressCreate):
    db_address = get_address(db, address_id)

    if db_address:
        db_address.name = address.name
        db_address.city = address.city
        db_address.latitude = address.latitude
        db_address.longitude = address.longitude

        db.commit()
        db.refresh(db_address)

    return db_address


# Delete Address
def delete_address(db: Session, address_id: int):
    db_address = get_address(db, address_id)

    if db_address:
        db.delete(db_address)
        db.commit()

    return db_address