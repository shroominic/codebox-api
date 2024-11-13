# Part 3: Error Handling and Data Persistence

Let's enhance our stock analysis tool with proper error handling and data persistence. 

### First, let's create `src/error_handlers.py` with custom exceptions:

```python
from typing import Optional, List

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

### Now, let's update our `src/main.py` with error handling and data persistence:

```python
from codeboxapi import CodeBox
import asyncio
from pathlib import Path
import json
from datetime import datetime
from .error_handlers import DataFetchError, AnalysisError

class StockAnalyzer:
    def __init__(self, data_dir: str = "data"):
        self.codebox = CodeBox(api_key="local")
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.analysis_history_file = self.data_dir / "analysis_history.json"
        
    async def load_analysis_history(self) -> dict:
        if self.analysis_history_file.exists():
            return json.loads(self.analysis_history_file.read_text())
        return {}
        
    async def save_analysis_history(self, symbol: str, analysis_data: dict):
        history = await self.load_analysis_history()
        history[symbol] = {
            "timestamp": datetime.now().isoformat(),
            "data": analysis_data
        }
        self.analysis_history_file.write_text(json.dumps(history, indent=2))

    async def analyze_stock(self, symbol: str, period: str = '1y'):
        try:
            # Check if data exists and is recent
            history = await self.load_analysis_history()
            if symbol in history:
                last_analysis = datetime.fromisoformat(history[symbol]["timestamp"])
                if (datetime.now() - last_analysis).days < 1:
                    print(f"Using cached analysis for {symbol}")
                    return history[symbol]["data"]

            # Verify symbol exists
            verify_code = f"""
            import yfinance as yf
            try:
                ticker = yf.Ticker('{symbol}')
                info = ticker.info
                if not info:
                    raise ValueError(f"Invalid symbol: {symbol}")
                print("Symbol verified successfully")
            except Exception as e:
                print(f"Error: {str(e)}")
                raise
            """
            result = await self.codebox.aexec(verify_code)
            if "Error" in result.text:
                raise DataFetchError(symbol, result.text)

            # Perform analysis
            analysis_code = f"""
            try:
                data = fetch_stock_data('{symbol}', period='{period}')
                analysis_result = {{
                    'symbol': '{symbol}',
                    'period': '{period}',
                    'last_price': float(data['Close'].iloc[-1]),
                    'volume': int(data['Volume'].iloc[-1]),
                    'change_percent': float(data['Close'].pct_change().iloc[-1] * 100),
                }}
                print(json.dumps(analysis_result))
            except Exception as e:
                print(f"Analysis Error: {str(e)}")
                raise
            """
            result = await self.codebox.aexec(analysis_code)
            
            if "Analysis Error" in result.text:
                raise AnalysisError("Calculation", result.text)
                
            analysis_data = json.loads(result.text)
            await self.save_analysis_history(symbol, analysis_data)
            return analysis_data
            
        except Exception as e:
            if isinstance(e, (DataFetchError, AnalysisError)):
                raise
            raise AnalysisError("Unknown", str(e))

async def main():
    analyzer = StockAnalyzer()
    await analyzer.setup_environment()
    try:
        await analyzer.analyze_stock('AAPL')
    except (DataFetchError, AnalysisError) as e:
        print(f"Error during analysis: {str(e)}")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
```

This implementation follows error handling patterns shown in:

- [Error Handling](../examples/advanced.md#error-handling)


And file operations patterns from:

- [File Operations](../examples/getting_started.md#file-operations)


### Let's also create a utility function for data persistence in `src/utils.py`:

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