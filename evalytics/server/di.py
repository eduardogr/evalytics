from dependency_injector import providers, containers
from .repositories import DataRepository
from .storages import GoogleStorage, InMemoryStorage


class DataStorage(containers.DeclarativeContainer):
    inmemory_persistence = providers.Singleton(DataRepository, InMemoryStorage)
    google_persistence = providers.Singleton(DataRepository, GoogleStorage)


class Module:
    containers = {
        'dev': {
            'repository': DataStorage.inmemory_persistence(),
        },
        'production': {
            'repository': DataStorage.google_persistence(),
        }
    }
