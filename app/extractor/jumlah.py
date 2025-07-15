import re
from app.utils.helpers import clean_transaction_value
# utils/parsing/jumlah.py
def parse_jumlah(text_blocks):
    # Validasi input
    if not text_blocks or not isinstance(text_blocks, (list, tuple)):
        return None
        
    candidate_values = []
    money_pattern = re.compile(r'([\d.,]+[\d])')
    keywords = ['jumlah', 'total', 'amount', 'nilai', 'setor', 'rp', 'idr']

    for text in text_blocks:
        # Skip empty or None text
        if not text or not isinstance(text, str):
            continue
            
        if any(key in text for key in keywords):
            for num_str in money_pattern.findall(text):
                value = clean_transaction_value(num_str)
                if value and len(str(value)) >= 4:
                    candidate_values.append(value)

    if not candidate_values:
        for text in text_blocks:
            # Skip empty or None text
            if not text or not isinstance(text, str):
                continue
                
            for num_str in money_pattern.findall(text):
                value = clean_transaction_value(num_str)
                if value and len(str(value)) >= 4:
                    candidate_values.append(value)

    return max(candidate_values) if candidate_values else None
