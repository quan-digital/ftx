import asyncio as asyncio


class AsyncFifoQueue(asyncio.Queue):
    """
    FIFO Queue that counts the dropped items
    """
    def __init__(self, *args, **kwargs):
        self._queue = None
        self.items_dropped = 0
        super().__init__(*args, **kwargs)

    async def put(self, item) -> None:
        if self.full():
            self.items_dropped += 1
            self._queue.pop()
        await super().put(item)

    def put_nowait(self, item) -> None:
        if self.full():
            self.items_dropped += 1
            self._queue.pop()
        super().put_nowait(item)
