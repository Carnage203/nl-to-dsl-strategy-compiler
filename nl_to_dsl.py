"""
Natural Language to DSL Translator.
Converts English trading rule descriptions into DSL format using rule-based pattern matching.
"""

import re
from typing import Dict, List, Tuple


class NLToDSLTranslator:
    """
    Translates natural language trading rules into DSL format.
    """
    
    def __init__(self):
        """Initialize translator with pattern rules."""
        self.patterns = self._init_patterns()
    
    def _init_patterns(self) -> List[Tuple[str, str, str]]:
        """
        Initialize replacement patterns.
        Returns list of (pattern, replacement, description) tuples.
        """
        return [
                                    
            (r'\bprice\b', 'close', 'price -> close'),
            (r'\bclosing price\b', 'close', 'closing price -> close'),
            (r'\bclose price\b', 'close', 'close price -> close'),
            
                                     
            (r'\b(\d+)[-\s]?day moving average\b', r'SMA(close,\1)', 'N-day moving average'),
            (r'\bsma[-\s]?(\d+)\b', r'SMA(close,\1)', 'sma-N'),
            (r'\b(\d+)[-\s]?day sma\b', r'SMA(close,\1)', 'N-day sma'),
            (r'\bmoving average[-\s]?(\d+)\b', r'SMA(close,\1)', 'moving average-N'),
            (r'\bma[-\s]?(\d+)\b', r'SMA(close,\1)', 'ma-N'),
            
                          
            (r'\brsi[-\s]?\(?(\d+)\)?\b', r'RSI(close,\1)', 'rsi-N'),
            (r'\brsi\b', 'RSI(close,14)', 'rsi (default 14)'),
            
                             
            (r'\b(\d+(?:\.\d+)?)\s*million\b', r'\1M', 'N million -> NM'),
            (r'\b(\d+(?:\.\d+)?)\s*m\b(?!\w)', r'\1M', 'N m -> NM'),
            (r'\b(\d+(?:\.\d+)?)\s*thousand\b', r'\1K', 'N thousand -> NK'),
            (r'\b(\d+(?:\.\d+)?)\s*k\b(?!\w)', r'\1K', 'N k -> NK'),
            
                            
            (r'\bcrosses? above\b', 'crosses above', 'crosses above'),
            (r'\bcrosses? over\b', 'crosses above', 'crosses over -> crosses above'),
            (r'\bcrosses? below\b', 'crosses below', 'crosses below'),
            (r'\bcrosses? under\b', 'crosses below', 'crosses under -> crosses below'),
            
                               
            (r'\bvol\b', 'volume', 'vol -> volume'),
            
                                                      
            (r'\band\b', 'AND', 'and -> AND'),
            (r'\bor\b', 'OR', 'or -> OR'),
        ]
    
    def translate(self, nl_text: str) -> str:
        """
        Translate natural language text to DSL format.
        
        Args:
            nl_text: Natural language trading rule description
            
        Returns:
            DSL text with ENTRY: and/or EXIT: prefixes
        """
                         
        text = self._normalize(nl_text)
        
                                    
        text = self._apply_replacements(text)
        
                                            
        dsl = self._add_rule_prefixes(text)
        
        return dsl
    
    def _normalize(self, text: str) -> str:
        """
        Normalize text: lowercase, remove extra spaces, trim.
        
        Args:
            text: Input text
            
        Returns:
            Normalized text
        """
                              
        text = text.lower()
        
                                 
        text = re.sub(r'\s+', ' ', text)
        
              
        text = text.strip()
        
        return text
    
    def _apply_replacements(self, text: str) -> str:
        """
        Apply pattern replacements to text.
        
        Args:
            text: Normalized text
            
        Returns:
            Text with replacements applied
        """
                                     
        for pattern, replacement, _ in self.patterns:
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
                                                                                         
        
        return text
    
    def _add_rule_prefixes(self, text: str) -> str:
        """
        Detect entry/exit keywords and add ENTRY:/EXIT: prefixes.
        
        Args:
            text: Text after replacements
            
        Returns:
            DSL text with ENTRY:/EXIT: prefixes
        """
                        
        entry_keywords = ['buy', 'enter', 'entry', 'long', 'go long']
                       
        exit_keywords = ['exit', 'sell', 'close', 'stop']
        
                                                       
        has_entry = any(keyword in text for keyword in entry_keywords)
        has_exit = any(keyword in text for keyword in exit_keywords)
        
                                                              
        if not has_entry and not has_exit:
            return f"ENTRY: {text}"
        
                                           
        sentences = re.split(r'[.!?]\s+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        dsl_parts = []
        
        for sentence in sentences:
            is_entry = any(keyword in sentence for keyword in entry_keywords)
            is_exit = any(keyword in sentence for keyword in exit_keywords)
            
                                                                                        
                                                                              
            keywords_to_remove = [k for k in entry_keywords + exit_keywords if k != 'close']
            for keyword in keywords_to_remove:
                sentence = re.sub(rf'\b{keyword}\b', '', sentence, flags=re.IGNORECASE)
            sentence = re.sub(r'\s+', ' ', sentence).strip()
            
                                               
            sentence = re.sub(r'^when\s+', '', sentence, flags=re.IGNORECASE)
            
                                   
            sentence = re.sub(r'\s+', ' ', sentence).strip()
            
                                                                                 
            if re.search(r'\bcrosses (above|below)\b', sentence, re.IGNORECASE):
                                                                   
                if not re.search(r'\b(open|high|low|close|volume)\s+crosses\b', sentence, re.IGNORECASE):
                    sentence = re.sub(r'\bcrosses (above|below)\b', r'close crosses \1', sentence, flags=re.IGNORECASE)
            
            if is_entry:
                dsl_parts.append(f"ENTRY: {sentence}")
            elif is_exit:
                dsl_parts.append(f"EXIT: {sentence}")
            else:
                                               
                dsl_parts.append(f"ENTRY: {sentence}")
        
        return '\n'.join(dsl_parts) if dsl_parts else f"ENTRY: {text}"

