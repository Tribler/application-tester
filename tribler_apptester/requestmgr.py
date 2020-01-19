from __future__ import absolute_import

import logging

import aiohttp


class HTTPRequestManager(object):
    """
    This class manages requests to the Tribler core.
    """

    def __init__(self, api_key):
        self._logger = logging.getLogger(self.__class__.__name__)
        self.headers = {'User-Agent': 'Tribler application tester', 'X-Api-Key': api_key}

    async def get_token_balance(self):
        """
        Perform a request to the core to get the token balance.
        """
        async with aiohttp.ClientSession() as client:
            response = await client.get("http://localhost:8085/wallets", headers=self.headers)
            json_response = response.json()

            if "MB" not in json_response["wallets"]:
                return 0
            return json_response["wallets"]["MB"]["balance"]["available"]

    async def get_downloads(self):
        """
        Perform a request to the core to get the downloads
        """
        async with aiohttp.ClientSession() as client:
            response = await client.get("http://localhost:8085/downloads", headers=self.headers)
            return await response.json()

    async def get_circuits_info(self):
        """
        Perform a request to the core to get circuits information
        """
        async with aiohttp.ClientSession() as client:
            response = await client.get("http://localhost:8085/ipv8/tunnel/circuits", headers=self.headers)
            return await response.json()

    async def get_overlay_statistics(self):
        """
        Perform a request to the core to get IPv8 overlay statistics
        """
        async with aiohttp.ClientSession() as client:
            response = await client.get("http://localhost:8085/ipv8/overlays", headers=self.headers)
            return await response.json()

    async def get_memory_history_core(self):
        """
        Perform a request to the core to get the memory usage history
        """
        async with aiohttp.ClientSession() as client:
            response = await client.get("http://localhost:8085/debug/memory/history", headers=self.headers)
            return await response.json()

    async def get_cpu_history_core(self):
        """
        Perform a request to the core to get the CPU usage history
        """
        async with aiohttp.ClientSession() as client:
            response = await client.get("http://localhost:8085/debug/cpu/history", headers=self.headers)
            return await response.json()

    async def get_state(self):
        """
        Get the current state of the Tribler instance
        """
        async with aiohttp.ClientSession() as client:
            response = await client.get("http://localhost:8085/state", headers=self.headers)
            return await response.json()

    async def is_tribler_started(self):
        """
        Return whether Tribler has started or not
        """
        try:
            json_response = await self.get_state()
            return json_response['state'] == 'STARTED'
        except:
            return False
