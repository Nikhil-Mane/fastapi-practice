import asyncio

async def worker_loop(job_queue):
    while True:
        job = await job_queue.get()
        # TODO: Process the job
        job_queue.task_done() 