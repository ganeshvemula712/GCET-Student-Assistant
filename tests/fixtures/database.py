from backend.app.models.user import User
from backend.app.models.conversation import Conversation


def create_student(db):

    user = User(
        name="Ganesh",
        email="ganesh@test.com",
        password_hash="hashed-password",
        role="student",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def create_admin(db):

    admin = User(
        name="Admin",
        email="admin@test.com",
        password_hash="hashed-password",
        role="admin",
    )

    db.add(admin)
    db.commit()
    db.refresh(admin)

    return admin


def create_conversation(
    db,
    user,
):

    conversation = Conversation(
        conversation_id="conversation-001",
        title="Attendance Query",
        user_id=user.id,
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation