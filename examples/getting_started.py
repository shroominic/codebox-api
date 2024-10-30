from codeboxapi import CodeBox

# Initialize CodeBox
codebox = CodeBox(api_key="local")  # or get your API key at https://codeboxapi.com

# Basic Examples
# -------------

# 1. Simple Code Execution
result = codebox.exec("print('Hello World!')")
print(result.text)  # Output: Hello World!

# 2. File Operations
# Upload a file
codebox.upload("example.txt", b"Hello from CodeBox!")

# Download a file
downloaded = codebox.download("example.txt")
content = downloaded.get_content()  # Returns b"Hello from CodeBox!"

# List files
files = codebox.list_files()  # Returns list[RemoteFile]

# 3. Package Management
# Install packages
codebox.install("pandas")

# List installed packages
packages = codebox.list_packages()

# 4. Variable Management
# Execute code that creates variables
codebox.exec("""
x = 42
data = [1, 2, 3]
name = "Alice"
""")

# Show all variables
variables = codebox.show_variables()
print(variables)  # Shows dict with all variables and their values

# 5. Plotting with Matplotlib
plot_code = """
import matplotlib.pyplot as plt
plt.figure(figsize=(10, 5))
plt.plot([1, 2, 3, 4], [1, 4, 2, 3])
plt.title('My Plot')
plt.show()
"""
result = codebox.exec(plot_code)
# result.images will contain the plot as bytes

# 6. Streaming Output
# Useful for long-running operations
for chunk in codebox.stream_exec("""
for i in range(5):
    print(f"Processing item {i}")
    import time
    time.sleep(1)
"""):
    print(chunk.content, end="")

# 7. Bash Commands
# Execute bash commands
codebox.exec("ls -la", kernel="bash")
codebox.exec("pwd", kernel="bash")

# Create and run Python scripts via bash
codebox.exec("echo \"print('Running from file')\" > script.py", kernel="bash")
codebox.exec("python script.py", kernel="bash")

# 8. Error Handling
result = codebox.exec("1/0")
if result.errors:
    print("Error occurred:", result.errors[0])
