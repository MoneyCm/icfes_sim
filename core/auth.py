import bcrypt
import os
import streamlit as st
from db.session import SessionLocal
from db.models import User

class AuthManager:
    @staticmethod
    def hash_password(password: str) -> str:
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode(), salt).decode()

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed_password.encode())

    @staticmethod
    def login(username, password):
        db = SessionLocal()
        try:
            user = db.query(User).filter(User.username == username).first()
            if user and AuthManager.verify_password(password, user.password_hash):
                st.session_state["logged_in"] = True
                st.session_state["user_id"] = user.id
                st.session_state["username"] = user.username
                return True
        finally:
            db.close()
        return False

    @staticmethod
    def logout():
        st.session_state["logged_in"] = False
        st.session_state["user_id"] = None
        st.session_state["username"] = None
        st.rerun()

    @staticmethod
    def check_auth():
        return st.session_state.get("logged_in", False)
