import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.member import Member
from app.services.member import create_member, get_members
from app.schemas.member import MemberCreate

# Setup test database
engine = create_engine('sqlite:///:memory:')
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables
Member.metadata.create_all(bind=engine)

@pytest.fixture(scope='function')
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def test_create_member(db_session):
    member_data = MemberCreate(name='John Doe', email='john.doe@example.com')
    member = create_member(db_session, member_data)
    assert member.id is not None
    assert member.name == 'John Doe'
    assert member.email == 'john.doe@example.com'

def test_get_members(db_session):
    member_data = MemberCreate(name='Jane Doe', email='jane.doe@example.com')
    create_member(db_session, member_data)
    members = get_members(db_session)
    assert len(members) == 1
    assert members[0].name == 'Jane Doe'
