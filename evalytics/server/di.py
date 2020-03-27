
from dependency_injector import providers, containers
from .repositories import FakeRepository, GoogleSheetsRepository


class Reader(containers.DeclarativeContainer):
    fake_reader = providers.Singleton(FakeRepository)
    google_sheets_reader = providers.Singleton(GoogleSheetsRepository)


class Module:
    containers = {
        'dev': {
            'reader': Reader.fake_reader(),
        },
        'production': {
            'reader': Reader.google_sheets_reader(),
        }
    }
