from threading import Timer

def recursive_hello():
    print("Hello!")
    t = Timer(2.0, recursive_hello)
    t.start()

enter = Timer(2.0, recursive_hello)
enter.start()
