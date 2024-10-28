import asyncio

from codeboxapi import CodeBox


async def main():
    await asyncio.gather(*(spawn_codebox() for _ in range(10)))


async def spawn_codebox():
    codebox = CodeBox(api_key="local")
    await codebox.arun("a = 'Hello World!'")
    a = await codebox.arun("a")
    assert a == "Hello World!"
    print("Success!")


if __name__ == "__main__":
    asyncio.run(main())
