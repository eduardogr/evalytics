from dependency_injector import providers, containers
from .core import DataRepository, CommunicationsProvider
from .storages import GoogleStorage, InMemoryStorage
from .communications_channels import GmailChannel, StdOutputChannel


class DataStorage(containers.DeclarativeContainer):
    inmemory_storage = providers.Singleton(DataRepository, InMemoryStorage)
    google_storage = providers.Singleton(DataRepository, GoogleStorage)


class CommunicationsChannel(containers.DeclarativeContainer):
    std_output_channel = providers.Singleton(
        CommunicationsProvider, StdOutputChannel)
    gmail_channel = providers.Singleton(
        CommunicationsProvider, GmailChannel)


class Module:
    '''
    Here we specify concrete implementations
    for our core classes defined in core.py
    '''
    containers = {
        'dev': {
            'repository': DataStorage.inmemory_storage(),
            'comms_provider': CommunicationsChannel.std_output_channel(),
        },
        'prod': {
            'repository': DataStorage.google_storage(),
            'comms_provider': CommunicationsChannel.gmail_channel(),
        }
    }
