from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates
import asyncio
from .fritz import FritzManager

app = FastAPI(title='FritzBox Thermostat Controller')
app.mount('/static', StaticFiles(directory='static'), name='static')
templates = Jinja2Templates(directory='templates')

# single manager instance
manager = FritzManager('192.168.178.1')

@app.on_event('startup')
async def startup_event():
    await manager.start()

@app.on_event('shutdown')
async def shutdown_event():
    await manager.stop()

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse('index.html', {'request': request})

@app.get('/api/devices')
async def devices():
    return JSONResponse(await manager.list_devices())

@app.post('/api/device/{ain}/set_temp')
async def set_temp(ain: str, payload: dict):
    temp = payload.get('temperature')
    await manager.set_temperature(ain, temp)
    return {'status':'ok'}

@app.get('/api/device/{ain}/history')
async def history(ain: str):
    return JSONResponse(await manager.get_history(ain))
