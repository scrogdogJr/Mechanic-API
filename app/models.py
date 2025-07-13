from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, ForeignKey, Column, Table, select
from datetime import date
from typing import List

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)


ticket_mechanic = Table(
    'ticket_mechanic',
    Base.metadata,
    Column('service_ticket_id', ForeignKey('service_tickets.id')),
    Column('mechanic_id', ForeignKey('mechanics.id'))
)

class Customer(Base):
    __tablename__ = 'customers'
    id: Mapped[int] = mapped_column(primary_key=True) # Don't need mapped_column unless you have other conditions
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(360), nullable=False, unique=True)

    service_tickets: Mapped[List['ServiceTickets']] = db.relationship(back_populates='customer')

class ServiceTickets(Base):
    __tablename__ = 'service_tickets'
    id: Mapped[int] = mapped_column(primary_key=True)
    service_date: Mapped[date] = mapped_column(nullable=False)
    service_desc: Mapped[str] = mapped_column(String(360), nullable=False)
    VIN: Mapped[str] = mapped_column(String(255), nullable=False)
    customer_id: Mapped[int] = mapped_column(ForeignKey('customers.id'), nullable=False)

    customer: Mapped['Customer'] = db.relationship('Customer', back_populates='service_tickets')
    mechanics: Mapped[List['Mechanic']] = db.relationship(secondary=ticket_mechanic, back_populates='service_tickets')

class Mechanic(Base):
    __tablename__ = 'mechanics'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(360), nullable=False, unique=True)
    phone: Mapped[str] = mapped_column(String(15), nullable=False, unique=True)
    salary: Mapped[float] = mapped_column(nullable=False)

    service_tickets: Mapped[List['ServiceTickets']] = db.relationship(secondary=ticket_mechanic, back_populates='mechanics')