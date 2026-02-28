from app.domain.user import User


class InMemoryUserRepository:

    def __init__(self):
        self.users = {}

    def save(self, user: User):
        self.users[user.email] = user
        return user

    def find_by_email(self, email: str):
        return self.users.get(email)