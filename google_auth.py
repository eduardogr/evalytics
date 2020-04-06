from __future__ import print_function
from evalytics.server.google_api import GoogleAuth

def main():
    GoogleAuth.authenticate()
    print('File "token.pickle" should be generated')

if __name__ == '__main__':
    main()
