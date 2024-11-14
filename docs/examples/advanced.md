# Advanced Examples

For detailed information about security and architecture, see:

- [Why Sandboxing is Important](../concepts/architecture.md#why-is-sandboxing-important)
- [Implementation Comparison](../concepts/implementations.md#implementation-comparison)

> [!NOTE] Update **main.py** with each example and run it with
>```bash
>python main.py
>```

## Example 1: Basic Usage with Custom Kernels

```python
from codeboxapi import CodeBox

def main():
    codebox = CodeBox()

    # Execute bash commands
    result = codebox.exec("ls -la", kernel="bash")
    print("Bash command result:", result.text)

    # Create and run Python scripts via bash
    result = codebox.exec('echo "print(\'Running from file\')" > script.py', kernel="bash")
    result = codebox.exec("python script.py", kernel="bash")
    print("Script result:", result.text)

if __name__ == "__main__":
    main()
```
### return
```bash
Bash command result: total 16
drwxr-xr-x  4 renzotincopa  staff  128 Nov 13 17:52 .
drwxr-xr-x  7 renzotincopa  staff  224 Nov 13 13:19 ..
-rw-r--r--  1 renzotincopa  staff   13 Nov 13 17:52 async_file.txt
-rw-r--r--  1 renzotincopa  staff   11 Nov 13 13:29 data.csv

Script result: Running from file
```

## Example 2: File Streaming with Chunks

```python
from codeboxapi import CodeBox

def main():
    codebox = CodeBox(verbose=True)
    
    code = """
import time
t0 = time.time()
for i in range(3):
    elapsed = time.time() - t0
    print(f"{elapsed:.5f}: {i}")
    time.sleep(1)
"""
    
    print("Starting streaming example...")

    result = codebox.exec(code)
    for chunk in result.chunks:
        print(chunk.content, end='')


if __name__ == "__main__":
    main()
```
### return
```bash
Starting streaming example...
0.00015: 0
1.00524: 1
2.01015: 2
```

## Example 3: Docker Parallel Processing

> Requirements:
> - Docker must be installed and running (start Docker Desktop or docker daemon)
> - Port 8069 must be available
> - User must have permissions to run Docker commands

```python
from codeboxapi import CodeBox
import asyncio

async def train_model(codebox: CodeBox, data_split: int) -> dict:
    # Install required packages
    await codebox.ainstall("pandas")
    await codebox.ainstall("scikit-learn")
    
    result = await codebox.aexec(f"""
        import pandas as pd
        from sklearn.model_selection import train_test_split
        from sklearn.linear_model import LinearRegression
        
        # Training simulation
        print(f'Training model with split {data_split}')
    """)
    return {"split": data_split, "output": result.text, "errors": result.errors}

async def main():
    try:
        # Run multiple instances in parallel
        codeboxes = [CodeBox(api_key="docker") for _ in range(4)]
        tasks = [train_model(codebox, i) for i, codebox in enumerate(codeboxes)]
        results = await asyncio.gather(*tasks)
        
        for result in results:
            print(f"Result from split {result['split']}:", result['output'])
            
    except Exception as e:
        print(f"Error during execution: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
```

### return
```bash
Result from split 0: Training model with split 0
Result from split 1: Training model with split 1
Result from split 2: Training model with split 2
Result from split 3: Training model with split 3
```

## Example 4: Error Handling

```python
from codeboxapi import CodeBox

def main():
    codebox = CodeBox()

    print("Example 1: Handling package import error")
    # Handle execution errors
    result = codebox.exec("import non_existent_package")
    if result.errors:
        print("Error occurred:", result.errors[0])

    print("\nExample 2: Handling runtime error")
    # Handle runtime errors with try/except
    result = codebox.exec("""
    try:
        1/0
    except Exception as e:
        print(f"Error: {str(e)}")
    """)
    print("Result:", result.text)

    print("\nExample 3: Handling syntax error")
    result = codebox.exec("print('Hello' print('World')")
    if result.errors:
        print("Syntax error:", result.errors[0])

if __name__ == "__main__":
    main()
```

### return
```bash
Example 1: Handling package import error
Error occurred: No module named 'non_existent_package'

Example 2: Handling runtime error
Result: Error: division by zero


Example 3: Handling syntax error
Syntax error: '(' was never closed (<ipython-input-1-8012c158bb8c>, line 1)
```

## Additional Resources

For more advanced usage patterns, see:

- [Components Overview](../concepts/components.md)
- [API Types Reference](../api/types.md)
- [Docker Implementation](../concepts/implementations.md#dockerbox)
- [Data Structures](../concepts/data_structures.md)
