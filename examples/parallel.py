import asyncio

from codeboxapi import CodeBox


async def main():
    await asyncio.gather(*[spawn_codebox() for _ in range(10)])


async def spawn_codebox():
    async with CodeBox() as codebox:
        await codebox.arun("print('Hello World!')")


if __name__ == "__main__":
    asyncio.run(main())
