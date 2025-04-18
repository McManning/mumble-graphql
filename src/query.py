
import strawberry
from strawberry import ID
from mumble import get_mumble_servers
from schema_types import Server


@strawberry.type
class Query:
    @strawberry.field(description="Get a list of all servers.")
    def servers(self) -> list[Server]:
        return [Server(s) for s in get_mumble_servers()]
