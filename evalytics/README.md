# evalytics

## Architecture fo classes

handlers -> use cases -> repository (data access) -> domain (models and adapters) -> storage (outter layer. frameworks, external apis, ..., etc)

- main.py pass instances as arguments to handlers.
- handlers receive ALL instances but pass necessary instances to use cases that will NOT know which concrete implementations are using.
- use cases logic just perform business logic in an agnostic way without knowledge about implementations, just interfaces and models of the domain.
- entities are supposed to not have dependencies and just represent domain of the application.
- storages are an outter layer that keep repositories abtracted of which implementation is being used.