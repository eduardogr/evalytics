from __future__ import print_function
from evalytics.server.auth import GoogleAuth

def main():
    GoogleAuth.authenticate()
    print('\nFile "token.pickle" should be generated')

if __name__ == '__main__':
    main()
