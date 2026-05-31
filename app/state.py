from database.models.couscous import User


class State:
    def __init__(self):
        self.user: User | None = None
        self.active_feed_url: str | None = None
        self.loading: bool = False
