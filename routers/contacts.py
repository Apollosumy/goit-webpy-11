from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, timedelta
from database import get_db
from models import Contact
from schemas import ContactCreate, ContactResponse, ContactUpdate
from fastapi_jwt_auth import AuthJWT

router = APIRouter()



@router.get("/", response_model=List[ContactResponse])
def get_contacts(
    name: Optional[str] = Query(None),
    last_name: Optional[str] = Query(None),
    email: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    query = db.query(Contact)

    if name:
        query = query.filter(Contact.first_name.ilike(f"%{name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))

    return query.all()



@router.post("/", response_model=ContactResponse)
def create_contact(contact: ContactCreate, db: Session = Depends(get_db)):
    new_contact = Contact(**contact.dict())
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact



@router.get("/{contact_id}", response_model=ContactResponse)
def get_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact



@router.put("/{contact_id}", response_model=ContactResponse)
def update_contact(contact_id: int, contact_data: ContactUpdate, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    for key, value in contact_data.dict(exclude_unset=True).items():
        setattr(contact, key, value)

    db.commit()
    db.refresh(contact)
    return contact



@router.delete("/{contact_id}")
def delete_contact(contact_id: int, db: Session = Depends(get_db)):
    contact = db.query(Contact).filter(Contact.id == contact_id).first()
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")

    db.delete(contact)
    db.commit()
    return {"message": "Contact deleted successfully"}



@router.get("/birthdays/", response_model=List[ContactResponse])
def get_upcoming_birthdays(db: Session = Depends(get_db)):
    today = date.today()
    next_week = today + timedelta(days=7)

    contacts = db.query(Contact).filter(
        Contact.birthday >= today, Contact.birthday <= next_week
    ).all()

    return contacts


@router.get("/", response_model=List[ContactResponse])
def get_contacts(db: Session = Depends(get_db), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    user_id = Authorize.get_jwt_identity()
    return db.query(Contact).filter(Contact.owner_id == user_id).all()
