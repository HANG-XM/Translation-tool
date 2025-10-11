import time
import threading
from contextlib import contextmanager

@contextmanager
def timer():
    start = time.time()
    yield
    end = time.time()
    return end - start

def run_concurrently(func, num_threads=10):
    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=func)
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()