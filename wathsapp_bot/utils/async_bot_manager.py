import asyncio
from threading import Thread

# Очередь задач
async_queue = asyncio.Queue()
global_loop = None


# Фоновый обработчик задач
async def background_loop():
    while True:
        coro = await async_queue.get()
        try:
            await coro
        except Exception as e:
            print(f"❌ Ошибка в асинхронной задаче: {e}")
        finally:
            async_queue.task_done()


# Запустить event loop в фоновом потоке
def start_async_loop():
    global global_loop
    global_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(global_loop)
    global_loop.create_task(background_loop())
    global_loop.run_forever()


# Безопасно положить корутину в очередь
def run_async(coro):
    if global_loop is None:
        raise RuntimeError("Async loop not started")

    async def safe_put():
        await async_queue.put(coro)

    asyncio.run_coroutine_threadsafe(safe_put(), global_loop)



