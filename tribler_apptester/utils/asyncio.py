from asyncio import sleep


async def looping_call(delay, interval, task, *args):
    await sleep(delay)
    while True:
        task(*args)
        await sleep(interval)
