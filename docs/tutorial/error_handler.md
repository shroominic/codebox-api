# Part 3: Error Handling and Data Persistence

This tutorial shows how to implement proper error handling and data persistence in your stock analysis tool.

> [!NOTE]  
> Make sure you have completed Part 2 before continuing.

## Custom Exceptions

First, let's create our custom exceptions in `src/error_handlers.py`:

```bash
touch src/error_handlers.py
```
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
```



### Let's also create a utility function for data persistence in `src/utils.py`:

```bash
touch src/utils.py
```

**Code:**

```python
from pathlib import Path
import json
from typing import Dict, Any

async def save_json_data(file_path: Path, data: Dict[str, Any]):
    """Safely save JSON data with error handling"""
    try:
        temp_path = file_path.with_suffix('.tmp')
        temp_path.write_text(json.dumps(data, indent=2))
        temp_path.replace(file_path)
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise IOError(f"Failed to save data: {str(e)}")
```


### Now, let's update our `src/main.py` with error handling and data persistence:

**Code:**

```python
from codeboxapi import CodeBox
import asyncio
from pathlib import Path
from PIL import Image
import base64
from io import BytesIO
from datetime import datetime
from visualization import create_technical_analysis_plot
from error_handlers import DataFetchError, AnalysisError
from utils import save_json_data, load_json_data

class StockAnalyzer:
    def __init__(self, data_dir: str = "data"):
        self.codebox = CodeBox(api_key="local")
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.history_file = self.data_dir / "analysis_history.json"

    async def analyze_stock(self, symbol: str, period: str = '1y'):
        print("\nUsing error handlers from error_handlers.py...")
        try:
            # First try to load previous analysis
            print("\nTrying to load previous analysis using utils.py...")
            previous_data = await load_json_data(self.history_file)
            if previous_data.get("last_analysis", {}).get("symbol") == symbol:
                print(f"Found previous analysis for {symbol}")

            # Verify symbol exists
            verify_code = f"""
            import yfinance as yf
            try:
                ticker = yf.Ticker('{symbol}')
                if not ticker.info:
                    raise ValueError(f"Symbol not found: {symbol}")
            except Exception as e:
                raise DataFetchError('{symbol}', str(e))
            """
            await self.codebox.aexec(verify_code)
            
            with open('src/analysis.py', 'r') as file:
                analysis_code = file.read()
            
            # Setup analysis environment
            setup_code = f"""
            import yfinance as yf
            import pandas as pd
            import ta
            {analysis_code}
            try:
                df = yf.Ticker('{symbol}').history(period='{period}')
                if df.empty:
                    raise DataFetchError('{symbol}', 'No data available')
                df = calculate_technical_indicators(df)
            except Exception as e:
                raise AnalysisError('Data Processing', str(e))
            """
            await self.codebox.aexec(setup_code)
            
            # Obtener datos básicos del stock
            basic_info_code = f"""
            ticker = yf.Ticker('{symbol}')
            info = ticker.info
            last_price = info.get('regularMarketPrice', 0)
            volume = info.get('regularMarketVolume', 0)
            prev_close = info.get('previousClose', 0)
            change_percent = ((last_price - prev_close) / prev_close * 100) if prev_close else 0
            
            analysis_result = {{
                "symbol": '{symbol}',
                "last_price": last_price,
                "volume": volume,
                "change_percent": round(change_percent, 2)
            }}
            print(f"Analysis successful: {{analysis_result}}")
            """
            await self.codebox.aexec(basic_info_code)
            
            # Generate plot
            try:
                plot_code = await create_technical_analysis_plot(self.codebox, symbol, "df")
                temp_file = self.data_dir / "temp_analysis.py"
                temp_file.write_text(plot_code)
                
                with open(temp_file, 'rb') as f:
                    self.codebox.upload("analysis_code.py", f.read())
                
                output = await self.codebox.aexec("exec(open('analysis_code.py').read())")
                
                if output and hasattr(output, 'text'):
                    for line in output.text.split('\n'):
                        if line.startswith('IMAGE_BASE64|'):
                            base64_str = line.split('|')[1].strip()
                            img_data = base64.b64decode(base64_str)
                            img = Image.open(BytesIO(img_data))
                            img_path = self.data_dir / f'{symbol}_analysis.png'
                            img.save(str(img_path))
                            
                            # Save analysis metadata
                            print("\nSaving analysis using utils.py...")
                            analysis_data = {
                                "last_analysis": {
                                    "symbol": symbol,
                                    "timestamp": datetime.now().isoformat(),
                                    "image_path": str(img_path)
                                }
                            }
                            await save_json_data(self.history_file, analysis_data)
                            
                            print(f"✓ Analysis for {symbol} completed")
                return output
                
            except Exception as e:
                raise AnalysisError("Visualization", str(e))
                
        except DataFetchError as e:
            print(f"✗ DataFetchError from error_handlers.py: {str(e)}")
            raise
        except AnalysisError as e:
            print(f"✗ AnalysisError from error_handlers.py: {str(e)}")
            raise
        except IOError as e:
            print(f"✗ IOError from utils.py: {str(e)}")
            raise AnalysisError("IO", str(e))
        except Exception as e:
            raise AnalysisError("Unknown", str(e))

async def main():
    analyzer = StockAnalyzer()
    
    print("\n=== Testing Invalid Symbol ===")
    try:
        await analyzer.analyze_stock('INVALID')
    except DataFetchError as e:
        print(f"✗ Caught expected error: {str(e)}") 

    print("\n=== Testing Valid Symbol ===")
    try:
        result = await analyzer.analyze_stock('AAPL')
        if result:
            print("✓ Analysis completed successfully")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
```

This implementation demonstrates:

- Custom exception hierarchy
- Proper error handling and propagation
- Clear error messages
- Graceful handling of both valid and invalid cases

The code follows patterns shown in:

- [Error Handling](../examples/advanced.md#error-handling)


And file operations patterns from:

- [File Operations](../examples/getting_started.md#file-operations)


## Running the Example

Execute the script:
```bash
python src/main.py
```

### Result

```bash
=== Testing Invalid Symbol ===

Using error handlers from error_handlers.py...

Trying to load previous analysis using utils.py...
✓ Retrieved data from: data/analysis_history.json

=== Testing Valid Symbol ===

Using error handlers from error_handlers.py...

Trying to load previous analysis using utils.py...
✓ Retrieved data from: data/analysis_history.json
Found previous analysis for AAPL

Saving analysis using utils.py...
✓ Data saved to: data/analysis_history.json
✓ Analysis for AAPL completed
✓ Analysis completed successfully
```

**Now lets continue with Parallel Analysis and Docker usage**