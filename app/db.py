from sqlalchemy import MetaData, Table, Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

metadata = MetaData()

device_history = Table(
    'device_history', metadata,
    Column('id', Integer, primary_key=True),
    Column('ain', String, index=True),
    Column('measured_temp', Float),
    Column('target_temp', Float),
    Column('battery', Integer),
    Column('valve_state', Integer),
    Column('created_at', DateTime, server_default=func.now())
)
