"""
CRUD operations for battle/match management.
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.models.battle import Match, MatchParticipant, ActionLog
from uuid import UUID
from datetime import datetime


def create_match(db: Session, creator_id: UUID):
    """Create a new battle/match."""
    db_match = Match(creator_id=creator_id, status="ongoing", start_time=datetime.utcnow())
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match


def get_match(db: Session, match_id: UUID):
    """Get a specific match by ID."""
    return db.query(Match).filter(Match.id == match_id).first()


def get_user_matches(db: Session, user_id: UUID, limit: int = 10):
    """Get recent matches for a user."""
    return db.query(Match).filter(Match.creator_id == user_id).order_by(desc(Match.start_time)).limit(limit).all()


def add_participant(db: Session, match_id: UUID, config_id: UUID, container_id: str, ip: str):
    """Add an agent participant to a match."""
    participant = MatchParticipant(
        match_id=match_id,
        agent_config_id=config_id,
        container_id=container_id,
        internal_ip=ip
    )
    db.add(participant)
    db.commit()
    db.refresh(participant)
    return participant


def get_match_participants(db: Session, match_id: UUID):
    """Get all participants in a match."""
    return db.query(MatchParticipant).filter(MatchParticipant.match_id == match_id).all()


def get_alive_participants(db: Session, match_id: UUID):
    """Get all agents still alive in a match."""
    return db.query(MatchParticipant).filter(
        MatchParticipant.match_id == match_id,
        MatchParticipant.is_alive == True
    ).all()


def eliminate_participant(db: Session, participant_id: UUID):
    """Mark a participant as eliminated."""
    participant = db.query(MatchParticipant).filter(MatchParticipant.id == participant_id).first()
    if participant:
        participant.is_alive = False
        participant.eliminated_at = datetime.utcnow()
        db.commit()
    return participant


def log_action(db: Session, participant_id: UUID, command: str, output: str, success: bool):
    """Log an action (command) performed by an agent."""
    log = ActionLog(
        participant_id=participant_id,
        command=command,
        output=output,
        was_successful=success
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_match_logs(db: Session, match_id: UUID, skip: int = 0, limit: int = 100):
    """Get action logs from a match with pagination."""
    participants = get_match_participants(db, match_id)
    participant_ids = [p.id for p in participants]
    
    return db.query(ActionLog).filter(
        ActionLog.participant_id.in_(participant_ids)
    ).order_by(desc(ActionLog.created_at)).offset(skip).limit(limit).all()


def update_match_winner(db: Session, match_id: UUID, winner_id: UUID):
    """Mark match as completed with a winner."""
    match = get_match(db, match_id)
    if match:
        match.winner_id = winner_id
        match.status = "completed"
        match.end_time = datetime.utcnow()
        db.commit()
    return match
