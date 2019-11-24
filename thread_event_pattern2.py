#!/usr/bin/python3
# Example code for a good/healthy Threaded wait pattern

import random
import threading
import time

progress = 0
sleeper = 0
result = None
result_available = threading.Event()

def background_calculation():
    print ( "Init bkgrnd()..." )
    global progress
    global sleeper
    for i in range(20):
        #sleeper = random() * 3
        sleeper = random.randint(1, 10)
        print ( "INSIDE bkgrnd method()", i, " - sleeping...", sleeper, "secs" )
        time.sleep( sleeper )
        progress = ( (i + 1) / 20 ) * 100

    # when the loop exits, the result is assigned, stored in a global variable & triggered
    global result
    result = 42
    result_available.set()

    # do some more work before exiting the thread

def main():
    thread = threading.Thread(target=background_calculation)
    thread.start()

    # wait here for the result to be available before continuing
    while not result_available.wait(timeout=5):
        print ( "OUTSODE bkgrnd method() - Thread waiter timed out @ 5 secs" )
        #print('\r{}% done...'.format(progress), '\r{}secs sleeping...'.format(sleeper), end='', flush=True)
        print('\t{}% done...'.format(progress) )

    print( "Outside main thread waita" )

    print('The result is', result)

if __name__ == '__main__':
    main()
