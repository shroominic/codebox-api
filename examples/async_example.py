from codeboxapi import CodeBox

codebox = CodeBox()


async def async_examples():
    # 1. Async Code Execution
    result = await codebox.aexec("print('Async Hello!')")
    print(result.text)

    # 2. Async File Operations
    await codebox.aupload("async_file.txt", b"Async content")

    downloaded = await codebox.adownload("async_file.txt")
    print("File content:", downloaded.get_content())

    # 3. All Sync Methods are also available Async
    await codebox.ainstall("requests")

    # 4. Async Streaming
    async for chunk in codebox.astream_exec("""
    for i in range(3):
        print(f"Async chunk {i}")
        import time
        time.sleep(1)
    """):
        print(chunk.content, end="")

    # 5. Async Streaming Download
    async for chunk in codebox.astream_download("async_file.txt"):
        assert isinstance(chunk, bytes)
        print(chunk.decode())


if __name__ == "__main__":
    import asyncio

    asyncio.run(async_examples())
