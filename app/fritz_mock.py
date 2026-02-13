import asyncio
import random
from typing import Dict, Any

# Simple mock adapter for TR-064 DECT Thermostats when no box available
class FritzMock:
    def __init__(self):
        self.devices = {
            '087610123456': {
                'ain': '087610123456',
                'name': 'Wohnzimmer Heizkoerper',
                'measured_temp': 21.5,
                'target_temp': 22.0,
                'battery': 95,
                'valve_state': 30,
            }
        }

    async def discover(self):
        await asyncio.sleep(0.1)
        return list(self.devices.values())

    async def list_devices(self):
        return list(self.devices.values())

    async def read(self, ain: str) -> Dict[str, Any]:
        d = self.devices.get(ain)
        if not d:
            raise KeyError('device not found')
        # simulate slight changes
        d['measured_temp'] += random.uniform(-0.1, 0.1)
        d['valve_state'] = max(0, min(100, d['valve_state'] + random.randint(-2,2)))
        return d

    async def set_target(self, ain: str, temp: float):
        d = self.devices.get(ain)
        if not d:
            raise KeyError('device not found')
        d['target_temp'] = float(temp)
        return True
