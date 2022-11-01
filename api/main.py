from fastapi import FastAPI, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database.models.couscous import User, Feed
from database.service.database import get_session

app = FastAPI(
    title='CousCous RSS Reader API',
    description="""
        Interact with Postgres database for CousCous frontend
    """,
)

origins = [
    "http://localhost",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


@app.get("/health")
async def pong():
    return {"ping": "pong!"}


@app.get("/", status_code=status.HTTP_200_OK)
async def home():
    "Mostra o endereço para a documentação"
    return {"message": "Use a rota /docs para ver a documentação."}


@app.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
async def add_user(user: User, session: AsyncSession = Depends(get_session)):
    new_user = User(name=user.name, password=user.password)
    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)
    return new_user


@app.get("/feeds", response_model=list[Feed], status_code=status.HTTP_200_OK)
async def all_feeds(session: AsyncSession = Depends(get_session)):
    "Retorna a lista com todos os itens da TPU."
    result = await session.execute(select(Feed))
    all_feeds = result.scalars().all()
    return [Feed(title=feed.title) for feed in all_feeds]


@app.post("/feeds")
async def add_feed(feed: Feed, session: AsyncSession = Depends(get_session)):
    new_feed = Feed(url=feed.url, title=feed.title)
    session.add(new_feed)
    await session.commit()
    await session.refresh(new_feed)
    return new_feed
