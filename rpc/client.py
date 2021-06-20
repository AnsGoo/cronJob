from typing import Generator
import zerorpc
import contextlib
from zerorpc.core import Client

@contextlib.contextmanager
def get_client(url: str) -> Generator:
    client = zerorpc.Client()
    client.connect(url)
    yield client
    client.close()
    return