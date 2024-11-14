# Part 4: Advanced Features and Visualization Enhancements

Let's implement advanced features including parallel processing for multiple stocks and enhanced visualizations.

> [!NOTE]
> For this part we are going to use Docker, so `api_key` on `main.py` and `parallel_analyzer.py` must be **"docker"**

> [!WARNING]
> Make sure Docker is running before executing the code. You can verify this with `docker info`

## Setting:

Lets create the files we are going to use:

```bash
touch src/parallel_analyzer.py src/advanced_visualization.py
```

### Let's update `src/parallel_analyzer.py`:


**Code:**

```python
from codeboxapi import CodeBox
import asyncio
from typing import List, Dict

class AnalysisError(Exception):
    def __init__(self, phase, message):
        self.phase = phase
        self.message = message
        super().__init__(f"{phase}: {message}")

class ParallelStockAnalyzer:
    def __init__(self, num_workers=2):
        print(f"✓ Iniciando {num_workers} workers")
        try:
            self.workers = [
                CodeBox(
                    api_key="docker",
                    factory_id="shroominic/codebox:latest"
                ) for _ in range(num_workers)
            ]
        except Exception as e:
            raise AnalysisError("Inicialización", str(e))

    async def setup_workers(self):
        max_retries = 3
        retry_delay = 2

        for attempt in range(max_retries):
            try:
                for i, worker in enumerate(self.workers):
                    print(f"✓ Configurando worker {i}")
                    await worker.ainstall("pandas")
                    await asyncio.sleep(1)
                    await worker.ainstall("yfinance")
                    await asyncio.sleep(1)
                    await worker.ainstall("ta")
                break
            except Exception as e:
                if attempt == max_retries - 1:
                    raise AnalysisError("Configuración", f"Error: {str(e)}")
                await asyncio.sleep(retry_delay)

        setup_code = """
        import yfinance as yf
        import pandas as pd
        import numpy as np
        import ta

        def analyze_stock(symbol: str, period: str) -> dict:
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)


            # Calculate technical indicators
            
            # Calculate technical indicators
            rsi = ta.momentum.RSIIndicator(data['Close']).rsi()
            macd = ta.trend.MACD(data['Close'])
            bb = ta.volatility.BollingerBands(data['Close'])

            result = {
                'symbol': symbol,
                'last_price': float(data['Close'].iloc[-1]),
                'volume': int(data['Volume'].iloc[-1]),
                'rsi': float(rsi.iloc[-1]),
                'macd': float(macd.macd().iloc[-1]),
                'bb_upper': float(bb.bollinger_hband().iloc[-1]),
                'bb_lower': float(bb.bollinger_lband().iloc[-1])
            }
            return result
        """
        setup_tasks = [worker.aexec(setup_code) for worker in self.workers]
        await asyncio.gather(*setup_tasks)

    async def analyze_stocks(self, symbols: List[str]) -> List[Dict]:
        print(f"\n=== Analizando símbolos: {symbols} ===")
        
        tasks = []
        for i, symbol in enumerate(symbols):
            worker = self.workers[i % len(self.workers)]
            worker_id = i % len(self.workers)
            print(f"✓ Asignando {symbol} al worker {worker_id}")
            code = f"""
try:
    result = analyze_stock('{symbol}', '1y')
    print(f"RESULTADO_STOCK|{symbol}|{{result}}")
    result
except Exception as e:
    print(f"❌ Error: {{str(e)}}")
    raise
"""
            tasks.append(worker.aexec(code))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        processed_results = []
        
        for symbol, r in zip(symbols, results):
            try:
                if isinstance(r, Exception):
                    print(f"❌ Error en {symbol}: {str(r)}")
                    continue
                
                if r and hasattr(r, 'text'):
                    for line in r.text.split('\n'):
                        if "RESULTADO_STOCK|" in line:
                            try:
                                _, symbol_from_result, result_str = line.split("|")
                                result_dict = eval(result_str)
                                if result_dict['symbol'] == symbol_from_result:
                                    processed_results.append(result_dict)
                                    print(f"✓ {symbol} procesado")
                                    break
                            except Exception as e:
                                print(f"❌ Error procesando {symbol}: {str(e)}")
            except Exception as e:
                print(f"❌ Error con {symbol}: {str(e)}")
        
        print(f"\n=== Resultados: {len(processed_results)}/{len(symbols)} ===")
        return processed_results
```

This implementation follows the Docker parallel processing pattern shown in:

- [Docker Parallel Processing](../examples/async.md#docker-parallel-processing)


### Now`src/advanced_visualization.py`:


**Code:**

```python
from codeboxapi import CodeBox
from typing import List, Dict
import asyncio

class DockerResourceError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

async def create_market_dashboard(codebox: CodeBox, analysis_results: List[Dict]):
    print("\n=== Generating Dashboard ===")
    
    try:
        setup_code = """
import pandas as pd
import matplotlib.pyplot as plt
plt.style.use('seaborn')
"""
        await codebox.aexec(setup_code)
        
        plot_code = f"""
df = pd.DataFrame({analysis_results})
plt.figure(figsize=(10, 5))
plt.bar(df['symbol'], df['last_price'])
plt.title('Precio por Símbolo')
plt.ylabel('Precio')
plt.savefig('market_dashboard.png')
plt.close()
"""
        result = await codebox.aexec(plot_code)
        print("✓ Dashboard generated: market_dashboard.png")
        return result
        
    except Exception as e:
        print(f"❌ Error in visualization: {str(e)}")
        raise
```

### Let's add docker resorser error to error_handlers.py:

**Code:**
```python
from typing import Optional

class StockAnalysisError(Exception):
    """Base exception for stock analysis errors"""
    pass

class DataFetchError(StockAnalysisError):
    def __init__(self, symbol: str, message: Optional[str] = None):
        self.symbol = symbol
        self.message = message or f"Failed to fetch data for symbol {symbol}"
        super().__init__(self.message)

class AnalysisError(StockAnalysisError):
    def __init__(self, error_type: str, details: str):
        self.error_type = error_type
        self.details = details
        super().__init__(f"{error_type}: {details}")

class DockerResourceError(StockAnalysisError):
    def __init__(self, message: Optional[str] = None):
        self.message = message or "Docker is running out of resources"
        super().__init__(self.message)
```

### Finally, let's update our main file that uses all these features:

**Code:**
```python
from parallel_analyzer import ParallelStockAnalyzer
from advanced_visualization import create_market_dashboard
from codeboxapi import CodeBox
from error_handlers import AnalysisError, DockerResourceError
import asyncio

async def setup_environment():
    try:
        analyzer = ParallelStockAnalyzer(num_workers=2)
        viz_box = CodeBox(
            api_key="docker",
            factory_id="shroominic/codebox:latest"
        )
        print("✓ Environment initialized")
        return analyzer, viz_box
    except Exception as e:
        print(f"❌ Error in configuration: {str(e)}")
        raise

async def install_dependencies(analyzer, viz_box):
    try:
        await analyzer.setup_workers()
        await viz_box.ainstall("pandas")
        await asyncio.sleep(1)
        await viz_box.ainstall("matplotlib")
        await asyncio.sleep(1)
        await viz_box.ainstall("seaborn")
        print("✓ Dependencies installed")
    except Exception as e:
        print(f"❌ Error in dependencies: {str(e)}")
        raise

async def main():
    print("\n=== Starting analysis process ===")
    analyzer = None
    viz_box = None
    
    try:
        print("\n--- Initial configuration ---")
        analyzer, viz_box = await setup_environment()
        await install_dependencies(analyzer, viz_box)
        
        symbols = ['AAPL', 'MSFT']
        print(f"\n--- Analyzing symbols: {symbols} ---")
        
        results = await analyzer.analyze_stocks(symbols)
        print("\n=== Final results ===")
        print(f"Number of results: {len(results)}")
        print(f"Content: {results}")
        
        if not results:
            raise AnalysisError("Analysis", "No results obtained")
        
        print("Creating dashboard...")
        try:
            await create_market_dashboard(viz_box, results)
            print("Analysis completed successfully")
        except DockerResourceError as e:
            print(f"DOCKER RESOURCE ERROR: {str(e)}")
            print("Suggestion: Try freeing up Docker resources or increasing Docker limits")
            raise
        
    except Exception as e:
        print(f"Detailed error: {str(e)}")
        raise
    finally:
        if analyzer:
            for worker in analyzer.workers:
                try:
                    pass
                except Exception as e:
                    print(f"Error closing worker: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
```

This implementation leverages the async functionality shown in:

- [Async Operations](../examples/async.md#basic-async-operations)

And follows the plotting patterns demonstrated in:

- [Plotting with Matplotlib](../examples/getting_started.md#plotting-with-matplotlib)


### Running the Project

After implementing all the components, ensure docker is running and you have the necessary permissions to create containers.

you can aither open docker desktop, or use:
```bash
docker run
```

Run the following command to check if docker is running:

```bash
docker info
```

For running the project, you can run the following command:

```bash
# Run the project
python -m src.main
```

This will execute the stock analysis with error handling and data persistence enabled.

### Result

```bash
=== Starting analysis process ===

--- Initial configuration ---
✓ Starting 2 workers
✓ Environment initialized
✓ Configuring worker 0
✓ Configuring worker 1
✓ Dependencies installed

--- Analyzing symbols: ['AAPL', 'MSFT'] ---

=== Analyzing symbols: ['AAPL', 'MSFT'] ===
✓ Assigning AAPL to worker 0
✓ Assigning MSFT to worker 1
✓ AAPL processed
✓ MSFT processed

=== Results: 2/2 ===

=== Final results ===
Number of results: 2
Content: [{'symbol': 'AAPL', 'last_price': 228.16690063476562, 'volume': 18166019, 'rsi': 52.12271959387232, 'macd': -0.7860965218539206, 'bb_upper': 237.43318064638424, 'bb_lower': 219.23226429990484}, {'symbol': 'MSFT', 'last_price': 424.18499755859375, 'volume': 12428920, 'rsi': 53.061782246735525, 'macd': 0.3959305431284861, 'bb_upper': 435.9261503363394, 'bb_lower': 406.8953523492075}]
Creating dashboard...

=== Generating Dashboard ===
✓ Dashboard generated: market_dashboard.png
Analysis completed successfully
```