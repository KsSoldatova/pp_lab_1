from utils import run, remove_main

from time import sleep
import os

if __name__ == '__main__':
    run('rose')
    path_rose = os.path.join('dataset', 'rose')
    remove_main(path_rose)
    sleep(20)
    print('\n\n')
    run('tulip')
    path_tulip = os.path.join('dataset', 'tulip')
    remove_main(path_tulip)
    print('the end')
