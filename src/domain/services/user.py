from src.domain.models.user import User


class UserService:
    def create_user(self, telegram_id: str, username: str) -> User:
        return User(telegram_id=telegram_id, username=username)
