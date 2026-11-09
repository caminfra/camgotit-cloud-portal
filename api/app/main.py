"""Local-only, synthetic-data prototype.

Do not deploy this API to a publicly reachable environment until Entra JWT
validation, authorization, and production storage have been implemented.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import DateTime, ForeignKey, Integer, String, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

DEFAULT_DB = Path(__file__).resolve().parent.parent / "camgotit-dev.db"
DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{DEFAULT_DB}")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)

class Base(DeclarativeBase):
    pass

class Ticket(Base):
    __tablename__ = "tickets"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    customer: Mapped[str] = mapped_column(String(120))
    subject: Mapped[str] = mapped_column(String(220))
    priority: Mapped[str] = mapped_column(String(20), default="normal")
    status: Mapped[str] = mapped_column(String(30), default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Lead(Base):
    __tablename__ = "leads"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    source: Mapped[str] = mapped_column(String(40))
    locality: Mapped[str] = mapped_column(String(80))
    need: Mapped[str] = mapped_column(String(280))
    status: Mapped[str] = mapped_column(String(30), default="new")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Alert(Base):
    __tablename__ = "alerts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"))
    message: Mapped[str] = mapped_column(String(280))
    acknowledged: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

Base.metadata.create_all(engine)

app = FastAPI(title="CamGotIT Portal Prototype", version="0.1.0", description="LOCAL DEVELOPMENT ONLY. No authentication: do not expose to internet.")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"], allow_methods=["GET", "POST", "PATCH"], allow_headers=["Content-Type"])

def db():
    with SessionLocal() as session:
        yield session

class TicketNew(BaseModel):
    customer: str = Field(min_length=2, max_length=120)
    subject: str = Field(min_length=3, max_length=220)
    priority: Literal["normal", "urgent"] = "normal"

class TicketUpdate(BaseModel):
    status: Literal["new", "in_progress", "resolved", "closed"]

class LeadNew(BaseModel):
    source: Literal["manual", "nextdoor_manual", "referral", "website", "other"] = "manual"
    locality: str = Field(min_length=2, max_length=80)
    need: str = Field(min_length=5, max_length=280)

class Ack(BaseModel):
    acknowledged: bool = True

def ticket_out(item: Ticket) -> dict:
    return {"id":item.id,"customer":item.customer,"subject":item.subject,"priority":item.priority,"status":item.status,"created_at":item.created_at.isoformat()}

def lead_out(item: Lead) -> dict:
    return {"id":item.id,"source":item.source,"locality":item.locality,"need":item.need,"status":item.status,"created_at":item.created_at.isoformat()}

def alert_out(item: Alert) -> dict:
    return {"id":item.id,"ticket_id":item.ticket_id,"message":item.message,"acknowledged":bool(item.acknowledged),"created_at":item.created_at.isoformat()}

@app.get("/health")
def health():
    return {"status":"ok","environment":"local-development","production_ready":False}

@app.get("/api/summary")
def summary(session: Session = Depends(db)):
    return {
        "tickets": session.scalar(select(func.count()).select_from(Ticket)),
        "open_tickets":session.scalar(select(func.count()).select_from(Ticket).where(Ticket.status.not_in(["resolved","closed"]))),
        "leads":session.scalar(select(func.count()).select_from(Lead)),
        "unread_alerts":session.scalar(select(func.count()).select_from(Alert).where(Alert.acknowledged==0)),
    }

@app.get("/api/tickets")
def list_tickets(session: Session = Depends(db)):
    return [ticket_out(row) for row in session.scalars(select(Ticket).order_by(Ticket.id.desc())).all()]

@app.post("/api/tickets", status_code=201)
def create_ticket(payload: TicketNew, session: Session = Depends(db)):
    ticket = Ticket(**payload.model_dump());session.add(ticket);session.flush()
    session.add(Alert(ticket_id=ticket.id, message=f"New {ticket.priority} ticket #{ticket.id}: {ticket.subject}"))
    session.commit();session.refresh(ticket)
    return ticket_out(ticket)

@app.patch("/api/tickets/{ticket_id}")
def update_ticket(ticket_id: int, payload: TicketUpdate, session: Session = Depends(db)):
    ticket=session.get(Ticket,ticket_id)
    if ticket is None: raise HTTPException(404,"Ticket not found")
    ticket.status=payload.status;session.commit();session.refresh(ticket)
    return ticket_out(ticket)

@app.get("/api/leads")
def list_leads(session: Session = Depends(db)):
    return [lead_out(row) for row in session.scalars(select(Lead).order_by(Lead.id.desc())).all()]

@app.post("/api/leads", status_code=201)
def create_lead(payload: LeadNew, session: Session = Depends(db)):
    lead=Lead(**payload.model_dump());session.add(lead);session.commit();session.refresh(lead)
    return lead_out(lead)

@app.get("/api/leads/{lead_id}/reply-draft")
def draft_reply(lead_id: int, session: Session = Depends(db)):
    lead=session.get(Lead,lead_id)
    if lead is None: raise HTTPException(404,"Lead not found")
    # A deterministic review-only template, NOT an AI-generated message or automated post.
    return {"lead_id":lead_id,"requires_human_approval":True,"generated_by":"template-not-ai","text":f"Hi! CamGotIT IT Services helps with home tech issues in {lead.locality}. If you'd like, tell us a little more about the problem and we'll provide a free quote. camgotit.com"}

@app.get("/api/alerts")
def list_alerts(session: Session = Depends(db)):
    return [alert_out(row) for row in session.scalars(select(Alert).order_by(Alert.id.desc())).all()]

@app.post("/api/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: int, session: Session = Depends(db)):
    alert=session.get(Alert, alert_id)
    if alert is None: raise HTTPException(404,"Alert not found")
    alert.acknowledged=1;session.commit();session.refresh(alert)
    return alert_out(alert)
