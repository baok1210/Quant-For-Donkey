"""
TradingView Indicator Converter - Chuyển Pine Script sang Python (Pandas)
"""
import re
from typing import Dict, List

class PineScriptConverter:
    """Chuyển đổi Pine Script sang Python"""
    
    def __init__(self):
        self.pine_to_python_map = {
            'ta.rsi': 'talib.RSI' if 'talib' in globals() else 'self._calculate_rsi',
            'ta.atr': 'talib.ATR' if 'talib' in globals() else 'self._calculate_atr',
            'ta.sma': 'self._calculate_sma',
            'ta.ema': 'self._calculate_ema',
            'ta.macd': 'self._calculate_macd',
            'ta.bb': 'self._calculate_bollinger_bands'
        }

    def convert_to_python(self, pine_script: str) -> str:
        """
        Chuyển đổi Pine Script sang Python function
        """
        # Extract indicator name
        name_match = re.search(r'indicator\("([^"]+)"', pine_script)
        indicator_name = name_match.group(1) if name_match else "UnknownIndicator"
        
        # Extract inputs
        inputs = self._extract_inputs(pine_script)
        
        # Convert Pine functions to Python
        python_code = self._convert_functions(pine_script)
        
        # Create Python function template
        func_template = f"""
def {indicator_name.replace(' ', '_').replace('-', '_').lower()}(df, {', '.join([f'{inp["name"]}={inp["default"]}' for inp in inputs])}):
    '''
    {indicator_name} indicator converted from Pine Script
    Parameters:
    {chr(10).join([f'    {inp["name"]}: {inp["description"]} (default: {inp["default"]})' for inp in inputs])}
    '''
    import pandas as pd
    import numpy as np
    
    # Extract OHLCV
    high = df['high']
    low = df['low']
    close = df['close']
    volume = df['volume']
    
    # Converted Pine Script logic
{python_code}
    
    return df  # Return dataframe with new indicator columns
"""
        return func_template

    def _extract_inputs(self, pine_script: str) -> List[Dict]:
        """Trích xuất các input parameters từ Pine Script"""
        inputs = []
        input_pattern = r'input\(([^)]+)\)'
        matches = re.findall(input_pattern, pine_script)
        
        for match in matches:
            # Parse input definition
            parts = [part.strip() for part in match.split(',')]
            param = {"name": "unknown", "default": 0, "description": "Parameter"}
            
            # Extract name and default value
            for part in parts:
                if '=' in part:
                    key, val = part.split('=', 1)
                    key = key.strip()
                    val = val.strip().strip('"\'')
                    if key == 'title':
                        param["name"] = val
                    elif key == 'defval' or 'default' in key:
                        param["default"] = val
                else:
                    # Assume first non-keyword argument is the default value
                    if param["default"] == 0:
                        param["default"] = part.strip().strip('"\'')
            
            inputs.append(param)
        
        return inputs

    def _convert_functions(self, pine_script: str) -> str:
        """Chuyển đổi các hàm Pine sang Python"""
        # Remove Pine annotations
        cleaned = re.sub(r'//@version=\d+', '', pine_script)
        cleaned = re.sub(r'indicator\([^)]+\)', '', cleaned)
        
        # Replace common Pine functions with Python equivalents
        python_code = cleaned
        
        # Handle ta.rsi conversion
        python_code = re.sub(r'ta\.rsi\(([^,]+), ([^)]+)\)', 
                           r'df["rsi"] = talib.RSI(\1, \2)', 
                           python_code)
        
        # Handle ta.atr conversion
        python_code = re.sub(r'ta\.atr\(([^)]+)\)', 
                           r'df["atr"] = talib.ATR(high, low, close, \1)', 
                           python_code)
        
        # Handle basic calculations
        python_code = python_code.replace('plot(', '# plot(')
        python_code = python_code.replace('color=', '# color=')
        
        # Convert to Python indentation
        lines = python_code.split('\n')
        indented_lines = []
        indent_level = 1
        
        for line in lines:
            stripped = line.strip()
            if stripped:
                # Add Python-style indentation
                indented_line = "    " * indent_level + stripped
                indented_lines.append(indented_line)
        
        return '\n'.join(indented_lines)

    def _calculate_rsi(self, series, period=14):
        """Tính RSI nếu không có TA-Lib"""
        import pandas as pd
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _calculate_atr(self, high, low, close, period=14):
        """Tính ATR nếu không có TA-Lib"""
        import pandas as pd
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        return tr.rolling(window=period).mean()
