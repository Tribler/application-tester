from asyncio import sleep, ensure_future


async def looping_call(delay, interval, task, *args):
    await sleep(delay)
    while True:
        ensure_future(task(*args))
        await sleep(interval)
