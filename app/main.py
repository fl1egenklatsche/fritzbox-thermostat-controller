import os
import asyncio
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from databases import Database
from sqlalchemy import create_engine
from app.db import metadata

# choose backend: real fritzconnection if available else mock
try:
    from app.fritz import FritzManager
    REAL_FRITZ = True
except Exception:
    from app.fritz_mock import FritzMock as FritzManager
    REAL_FRITZ = False

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DB_URL = os.environ.get('DATABASE_URL', 'sqlite+aiosqlite:///'+os.path.join(BASE_DIR,'data','fritz_history.db'))

app = FastAPI(title='FritzBox Thermostat Controller')
app.mount('/static', StaticFiles(directory=os.path.join(BASE_DIR, 'static')), name='static')
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, 'templates'))

database = Database(DB_URL)
engine = create_engine(DB_URL.replace('+aiosqlite',''))
metadata.create_all(engine)

manager = FritzManager()

@app.on_event('startup')
async def startup():
    await database.connect()
    # if manager has async start, run it
    if hasattr(manager, 'start'):
        maybe = manager.start()
        if asyncio.iscoroutine(maybe):
            asyncio.create_task(maybe)

@app.on_event('shutdown')
async def shutdown():
    await database.disconnect()
    if hasattr(manager, 'stop'):
        maybe = manager.stop()
        if asyncio.iscoroutine(maybe):
            await maybe

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    devices = await manager.list_devices()
    return templates.TemplateResponse('index.html', {'request': request, 'devices': devices, 'real': REAL_FRITZ})

@app.get('/api/devices')
async def api_devices():
    devices = await manager.list_devices()
    return JSONResponse(devices)

@app.post('/api/device/{ain}/set_temp')
async def api_set_temp(ain: str, payload: dict):
    temp = payload.get('temp')
    if temp is None:
        raise HTTPException(status_code=400, detail='temp required')
    try:
        await manager.set_target(ain, float(temp))
    except KeyError:
        raise HTTPException(status_code=404, detail='device not found')
    return JSONResponse({'status': 'ok'})

@app.get('/api/device/{ain}/history')
async def api_history(ain: str):
    query = "SELECT ain, measured_temp, target_temp, battery, valve_state, created_at FROM device_history WHERE ain = :ain ORDER BY created_at DESC LIMIT 500"
    rows = await database.fetch_all(query=query, values={'ain': ain})
    return JSONResponse([dict(r) for r in rows])
