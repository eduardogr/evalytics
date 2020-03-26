# evalytics

## Architecture fo classes

handlers -> use cases -> adapters (api usage) -> entities (models and mappers)

- main.py pass instances as arguments to handlers.
- handlers receive ALL instances but pass necessary instances to use cases that will NOT know which adapter are using.
- use cases logic just perform business logic in an agnostic way without knowledge about adapters implementation
- entities are supposed to not have dependencies and just represent domain of the application