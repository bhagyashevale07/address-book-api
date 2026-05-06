from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from geopy.distance import geodesic
import models
from database import engine, SessionLocal
from models import Address
from schemas import AddressCreate
import logging


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()


@app.get("/")
def home():
    return {"message": "API is working"}


# Database Dependency
def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()
@app.post("/addresses")
def add_address(
    address: AddressCreate,
    db: Session = Depends(get_db)
):
    logging.info("Creating new address")
    return create_address(db, address)

@app.get("/addresses")
def all_addresses(db: Session = Depends(get_db)):
    logging.info("Fetching all addresses")
    return get_addresses(db)        


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


# Nearby Search API
@app.get("/nearby")
def get_nearby_addresses(
    latitude: float,
    longitude: float,
    distance_km: float,
    db: Session = Depends(get_db)
):
    
    logging.info("Searching nearby addresses")

    addresses = get_addresses(db)

    nearby_addresses = []

    current_location = (latitude, longitude)

    for address in addresses:

        address_location = (
            address.latitude,
            address.longitude
        )

        distance = geodesic(
            current_location,
            address_location
        ).km

        if distance <= distance_km:

            nearby_addresses.append({
                "id": address.id,
                "name": address.name,
                "city": address.city,
                "distance_km": round(distance, 2)
            })


    return nearby_addresses