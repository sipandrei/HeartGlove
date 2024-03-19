import asyncio
from time import sleep

async def count():
  print("async")
  await asyncio.sleep(5)
  print("done")

async def main():
    await asyncio.gather(count())


while True:
  print(1)
  asyncio.run(main())
  print(2)
  sleep(.5)
