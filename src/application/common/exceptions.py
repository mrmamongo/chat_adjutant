class ApplicationException(Exception):
    pass


class ThreadNotPresentedException(Exception):
    def __init__(self, thread_id: str) -> None:
        self.thread_id = thread_id

    def __str__(self) -> str:
        return "Thread id %s is not presented in state" % self.thread_id
