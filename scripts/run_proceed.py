from scheduler.utils import *
from multiprocessing import Process
import time

# def test():
#     print(3)
#     time.sleep(10)
#     print("await Done")
# def run_test():
#     p = Process(target=test)
#     p.start()
#     print("Sub task Done")
# # run_proceed()
# print("Done")

interval=60
while True:
    run_proceed()
    time.sleep(interval)
