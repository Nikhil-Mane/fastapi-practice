import asyncpg

async def store_job_result(pool, job_id, result):
    async with pool.acquire() as conn:
        await conn.execute('''
            INSERT INTO job_results(job_id, result) VALUES($1, $2)
        ''', job_id, result)

async def get_job_result(pool, job_id):
    async with pool.acquire() as conn:
        return await conn.fetchrow('''
            SELECT * FROM job_results WHERE job_id = $1
        ''', job_id) 