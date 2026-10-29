from conftest import Member

# Inline service functions

def create_member(db, name, email):
    member = Member(name=name, email=email)
    db.add(member)
    db.commit()
    db.refresh(member)
    return member

def get_members(db):
    return db.query(Member).all()

def test_create_member(db):
    member = create_member(db, 'John Doe', 'john.doe@example.com')
    assert member.id is not None
    assert member.name == 'John Doe'
    assert member.email == 'john.doe@example.com'

def test_get_members(db):
    create_member(db, 'Jane Doe', 'jane.doe@example.com')
    members = get_members(db)
    assert len(members) == 2
    assert members[0].name == 'John Doe'
    assert members[1].name == 'Jane Doe'
