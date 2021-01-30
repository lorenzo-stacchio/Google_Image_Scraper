import time
from alive_progress import alive_bar


def compute():
    for i in range(1000):
        time.sleep(.1)  # process items
        yield  # insert this and you're done!

if __name__ == '__main__':
    with alive_bar(1000) as bar:
        for i in compute():
            bar()