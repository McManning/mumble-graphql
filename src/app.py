# autopep8: off
import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager
from apscheduler.schedulers.background import BackgroundScheduler

parent_dir = Path(__file__).resolve().parent
if str(parent_dir) not in sys.path:
    sys.path.insert(0, str(parent_dir))


import asyncio
import strawberry
from fastapi import FastAPI

from strawberry.fastapi import GraphQLRouter

from mumble import mumble_heartbeat
from query import Query
from mutation import Mutation
from subscription import Subscription

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    subscription=Subscription
)

graphql_app = GraphQLRouter(schema)

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler = BackgroundScheduler()
    scheduler.add_job(mumble_heartbeat, "interval", seconds = 30)
    scheduler.start()
    yield

app = FastAPI(lifespan=lifespan)
app.include_router(graphql_app, prefix="/graphql")
