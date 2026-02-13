import os
import asyncio
from typing import List, Dict, Any

DB_POLL_INTERVAL = float(os.environ.get('POLL_INTERVAL', '30'))

try:
    # real fritzconnection imports
    from fritzconnection import FritzConnection
    REAL_AVAILABLE = True
except Exception:
    REAL_AVAILABLE = False

from app.fritz_mock import FritzMock
from databases import Database
from app.db import device_history

class FritzManager:
    def __init__(self, host=None, user=None, password=None):
        self.host = host or os.environ.get('FRITZ_HOST')
        self.user = user or os.environ.get('FRITZ_USER')
        self.password = password or os.environ.get('FRITZ_PASS')
        self._running = False
        self._task = None
        self.db = Database(os.environ.get('DATABASE_URL', 'sqlite+aiosqlite:///app/data/fritz_history.db'))
        if REAL_AVAILABLE and self.host and self.user and self.password:
            # placeholder for real connection, not fully implemented
            self._backend = FritzConnection(address=self.host, user=self.user, password=self.password)
        else:
            self._backend = FritzMock()

    async def start(self):
        await self.db.connect()
        self._running = True
        self._task = asyncio.create_task(self._poll_loop())

    async def stop(self):
        self._running = False
        if self._task:
            await self._task
        await self.db.disconnect()

    async def _poll_loop(self):
        while self._running:
            try:
                devices = await self.list_devices()
                for d in devices:
                    try:
                        # read fresh state
                        state = await self.read_device(d['ain'])
                        query = device_history.insert().values(
                            ain=state['ain'],
                            measured_temp=state.get('measured_temp'),
                            target_temp=state.get('target_temp'),
                            battery=state.get('battery'),
                            valve_state=state.get('valve_state')
                        )
                        await self.db.execute(query=query)
                    except Exception:
                        # ignore per-device errors
                        continue
            except Exception:
                # global poll errors ignored
                pass
            await asyncio.sleep(DB_POLL_INTERVAL)

    async def discover(self) -> List[Dict[str, Any]]:
        return await self._backend.discover()

    async def list_devices(self) -> List[Dict[str, Any]]:
        return await self._backend.list_devices()

    async def read_device(self, ain: str) -> Dict[str, Any]:
        return await self._backend.read(ain)

    async def set_target(self, ain: str, temp: float):
        return await self._backend.set_target(ain, temp)
