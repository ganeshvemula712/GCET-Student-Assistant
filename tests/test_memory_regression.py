import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import Base
from backend.app.models.message import Message
from backend.app.services.memory import build_contextual_search_query


@pytest.fixture
def memory_db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    yield db
    db.close()


def test_regression_a_how_much_is_it(memory_db):
    conv_id = "reg-a"
    memory_db.add(Message(conversation_id=conv_id, role="user", content="What is the minimum attendance required at GCET?"))
    memory_db.add(Message(conversation_id=conv_id, role="assistant", content="The minimum attendance required at GCET is 75%."))
    memory_db.commit()

    eq, is_f = build_contextual_search_query("How much is it?", memory_db, conv_id)
    assert is_f is True
    assert "minimum attendance" in eq.lower()
    assert "for it at gcet" not in eq.lower()
    assert "for it?" not in eq.lower()


def test_regression_b_is_it_mandatory(memory_db):
    conv_id = "reg-b"
    memory_db.add(Message(conversation_id=conv_id, role="user", content="What is the minimum attendance required at GCET?"))
    memory_db.add(Message(conversation_id=conv_id, role="assistant", content="The minimum attendance required at GCET is 75%."))
    memory_db.commit()

    eq, is_f = build_contextual_search_query("Is it mandatory?", memory_db, conv_id)
    assert is_f is True
    assert "minimum attendance" in eq.lower()
    assert "for it at gcet" not in eq.lower()


def test_regression_c_what_about_it(memory_db):
    conv_id = "reg-c"
    memory_db.add(Message(conversation_id=conv_id, role="user", content="What is the minimum attendance required at GCET?"))
    memory_db.add(Message(conversation_id=conv_id, role="assistant", content="The minimum attendance required at GCET is 75%."))
    memory_db.commit()

    eq, is_f = build_contextual_search_query("What about IT?", memory_db, conv_id)
    assert is_f is True
    assert "for IT at GCET" in eq


def test_regression_d_what_about_it_branch(memory_db):
    conv_id = "reg-d"
    memory_db.add(Message(conversation_id=conv_id, role="user", content="What is the minimum attendance required at GCET?"))
    memory_db.add(Message(conversation_id=conv_id, role="assistant", content="The minimum attendance required at GCET is 75%."))
    memory_db.commit()

    eq, is_f = build_contextual_search_query("What about IT branch?", memory_db, conv_id)
    assert is_f is True
    assert "for IT at GCET" in eq


def test_regression_e_for_it(memory_db):
    conv_id = "reg-e"
    memory_db.add(Message(conversation_id=conv_id, role="user", content="What is the minimum attendance required at GCET?"))
    memory_db.add(Message(conversation_id=conv_id, role="assistant", content="The minimum attendance required at GCET is 75%."))
    memory_db.commit()

    eq, is_f = build_contextual_search_query("For IT?", memory_db, conv_id)
    assert is_f is True
    assert "for IT at GCET" in eq


def test_regression_f_what_about_cse(memory_db):
    conv_id = "reg-f"
    memory_db.add(Message(conversation_id=conv_id, role="user", content="What is the minimum attendance required at GCET?"))
    memory_db.add(Message(conversation_id=conv_id, role="assistant", content="The minimum attendance required at GCET is 75%."))
    memory_db.commit()

    eq, is_f = build_contextual_search_query("What about CSE?", memory_db, conv_id)
    assert is_f is True
    assert "for CSE at GCET" in eq


def test_regression_g_deep_learning_applications(memory_db):
    conv_id = "reg-g"
    memory_db.add(Message(conversation_id=conv_id, role="user", content="What is deep learning?"))
    memory_db.add(Message(conversation_id=conv_id, role="assistant", content="Deep learning is a subset of machine learning..."))
    memory_db.commit()

    eq, is_f = build_contextual_search_query("What are its applications?", memory_db, conv_id)
    assert is_f is True
    assert "applications of deep learning" in eq.lower()


def test_regression_h_topic_switch_python(memory_db):
    conv_id = "reg-h"
    memory_db.add(Message(conversation_id=conv_id, role="user", content="What is the minimum attendance required at GCET?"))
    memory_db.add(Message(conversation_id=conv_id, role="assistant", content="The minimum attendance required at GCET is 75%."))
    memory_db.commit()

    eq, is_f = build_contextual_search_query("What is Python?", memory_db, conv_id)
    assert is_f is False
    assert eq == "What is Python?"
