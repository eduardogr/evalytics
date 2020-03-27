
from dependency_injector import providers, containers
from .adapters import FakeAdapter, GoogleSheetsAdapter


class Reader(containers.DeclarativeContainer):
    fake_reader = providers.Singleton(FakeAdapter)
    google_sheets_reader = providers.Singleton(GoogleSheetsAdapter)


class Module:
    containers = {
        'dev': {
            'reader': Reader.fake_reader(),
        },
        'production': {
            'reader': Reader.google_sheets_reader(),
        }
    }
