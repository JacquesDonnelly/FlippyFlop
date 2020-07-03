import time


def throttle(func):
    def inner(self, *args, **kwargs):
        time_since = time.time() - self.time_of_last_hit
        if abs(time_since) > 1:
            _result = func(self, *args, **kwargs)
            self.time_of_last_hit = time.time()
            print(f"hitting sheets via {func.__name__}")
        else:
            time.sleep(0.1)
            _result = inner(self, *args, **kwargs)

        return _result

    return inner
