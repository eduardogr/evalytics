# evalytics

## Architecture fo classes

handlers -> use cases -> repository (data access) -> domain (models and adapters) -> storage (outter layer. frameworks, external apis, ..., etc)
                      -> communications providers (notifications layer)

- main.py pass instances as arguments to handlers.
- handlers receive ALL instances but pass necessary instances to use cases that will NOT know which concrete implementations are using.
    - storages are an outter layer that keep our data repository abtracted of which concrete storage implementation we are using.
    - communications_channels are an outter layer that keep our communications provider abstracted of which channel implementation we are using.
- use cases logic just perform business logic in an agnostic way without knowledge about implementations, just interfaces and models of the domain.
- entities are supposed to not have dependencies and just represent domain of the application.
