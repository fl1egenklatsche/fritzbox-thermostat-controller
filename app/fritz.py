import asyncio
from fritzconnection import FritzConnection
from fritzconnection.lib.fritzhosts import FritzHosts
from fritzconnection.core.exceptions import FritzConnectionException
import time

class FritzManager:
    def __init__(self, box_ip, username=None, password=None, poll_interval=300):
        self.box_ip = box_ip
        self.username = username
        self.password = password
        self.poll_interval = poll_interval
        self._fc = None
        self._devices = {}
        self._task = None
        self._running = False
        self._history = {}

    async def start(self):
        loop = asyncio.get_event_loop()
        try:
            self._fc = FritzConnection(address=self.box_ip, user=self.username, password=self.password)
        except FritzConnectionException:
            self._fc = None
        self._running = True
        self._task = loop.create_task(self._poll_loop())

    async def stop(self):
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass

    async def _poll_loop(self):
        while self._running:
            try:
                await self._discover()
            except Exception:
                pass
            await asyncio.sleep(self.poll_interval)

    async def _discover(self):
        if not self._fc:
            try:
                self._fc = FritzConnection(address=self.box_ip, user=self.username, password=self.password)
            except Exception:
                return
        # use device list from TR-064 services
        # simplified: use fritzhosts to list devices and filter by DECT
        try:
            fh = FritzHosts(self._fc)
            hosts = fh.get_hosts_info()
            # naive parsing: find devices with 'dect' in name
            for h in hosts:
                name = h.get('host')
                ain = h.get('ain') or h.get('mac')
                if not ain:
                    continue
                if 'DECT' in str(name).upper() or 'thermostat' in str(name).lower() or 'heizung' in str(name).lower():
                    # placeholder telemetry
                    self._devices[ain] = {
                        'name': name,
                        'ain': ain,
                        'temp': None,
                        'battery': None,
                        'last_seen': time.time()
                    }
                    self._history.setdefault(ain, []).append({'ts': time.time(), 'temp': None})
        except Exception:
            return

    async def list_devices(self):
        return list(self._devices.values())

    async def set_temperature(self, ain, temperature):
        # placeholder: actual implementation requires TR-064 action calls to the DECT thermostat service
        # store in history
        self._history.setdefault(ain, []).append({'ts': time.time(), 'temp_set': temperature})
        return True

    async def get_history(self, ain):
        return self._history.get(ain, [])
