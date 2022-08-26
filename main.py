from http.client import responses
from operator import and_
from typing import List
import databases
import sqlalchemy
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from time import time_ns, ctime

# sqlite
database_location = './test.db'
DATABASE_URL = "sqlite:///" + database_location
database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()

consumption = sqlalchemy.Table(
    "consumption",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("boardId", sqlalchemy.String),
    sqlalchemy.Column("circuitId", sqlalchemy.Integer),
    sqlalchemy.Column("time", sqlalchemy.BigInteger),
    sqlalchemy.Column("duration", sqlalchemy.Integer),
    sqlalchemy.Column("liters", sqlalchemy.Float),
    sqlalchemy.Column("tempC", sqlalchemy.Float),
    sqlalchemy.Column("tempM", sqlalchemy.Float),
    sqlalchemy.Column("litersF", sqlalchemy.Float),
    sqlalchemy.Column("tempF", sqlalchemy.Float)
)

engine = sqlalchemy.create_engine(
    DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(engine)


class CircuitIn(BaseModel):
    circuitId: int
    timeStart: int
    timeEnd: int
    liters: float
    litersF: float


class ReportIn(BaseModel):
    boardId: str
    millisBoard: int
    tempC: float
    tempM: float
    tempF: float
    mainLiters: float
    circuits: list[CircuitIn]


class Consumption(BaseModel):
    id: int
    boardId: str
    circuitId: int
    time: int
    duration: int
    liters: float
    litersF: float
    tempC: float
    tempM: float
    tempF: float


app = FastAPI(title="REST API using FastAPI & sqlite")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.add_middleware(GZipMiddleware)


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.get("/ping", status_code=status.HTTP_200_OK)
def ping():
    return {"ping": "He's alive!"}


@app.post("/", status_code=status.HTTP_201_CREATED)
async def create_consumptions(report: ReportIn):
    millisEpoch = time_ns() // 1000000
    timeEpoch = ctime(millisEpoch // 1000)
    createdCircuits = 0
    for circuit in report.circuits:
        if circuit.timeEnd-circuit.timeStart > 0 and circuit.liters > 0:
            query = consumption.insert().values(
                boardId=report.boardId,
                circuitId=circuit.circuitId,
                time=millisEpoch-(report.millisBoard-circuit.timeStart),
                duration=circuit.timeEnd-circuit.timeStart,
                liters=circuit.liters,
                litersF=circuit.litersF,
                tempC=report.tempC,
                tempM=report.tempM,
                tempF=report.tempF
            )
            _ = await database.execute(query)
            createdCircuits += 1
    return {"timeEpoch": timeEpoch, "createdEntries": createdCircuits}


@app.get("/all", response_model=List[Consumption], status_code=status.HTTP_200_OK)
async def read_consumptions(skip: int = 0, take: int = 20):
    query = consumption.select().offset(skip).limit(take)
    return await database.fetch_all(query)


@app.get("/b/{boardId}/", response_model=List[Consumption], status_code=status.HTTP_200_OK)
async def read_consumptions_board(boardId: str):
    query = consumption.select().where(consumption.c.boardId == boardId)
    return await database.fetch_all(query)


@app.get("/b/{boardId}/c/{circuidId}/", response_model=List[Consumption], status_code=status.HTTP_200_OK)
async def read_consumptions_board_circuit(boardId: str, circuidId: int):
    query = consumption.select().where(and_(consumption.c.boardId == boardId, consumption.c.circuitId == circuidId))
    return await database.fetch_all(query)
