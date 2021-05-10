def example_func(*args,**kwargs):
    return {"res":"Test data",
            "args_received": args,
            "kwargs_received":kwargs}


def example_error():
    raise AssertionError
