import re
from datetime import datetime
from decimal import Decimal

def filter_list(lst: list, filters: dict) -> list:
    """
    Applies exact matching filters to a list of dictionaries.
    """
    result = lst
    for key, val in filters.items():
        if val is None:
            continue
        if isinstance(val, bool):
            result = [item for item in result if item.get(key) == val]
        elif isinstance(val, str) and val.lower() in ["true", "false"]:
            bool_val = val.lower() == "true"
            result = [item for item in result if item.get(key) == bool_val]
        else:
            result = [item for item in result if str(item.get(key)) == str(val)]
    return result

def search_list(lst: list, query: str, fields: list) -> list:
    """
    Applies case-insensitive substring search across multiple fields on a list of dictionaries.
    """
    if not query:
        return lst
    query = query.lower().strip()
    result = []
    for item in lst:
        match = False
        for field in fields:
            val = item.get(field)
            if val and query in str(val).lower():
                match = True
                break
        if match:
            result.append(item)
    return result

def order_list(lst: list, ordering: str, default_field: str = "created_at") -> list:
    """
    Orders a list of dictionaries by a field name. Supports desc order with leading '-'.
    """
    if not ordering:
        ordering = default_field

    reverse = False
    field = ordering
    if ordering.startswith("-"):
        reverse = True
        field = ordering[1:]

    def get_sort_key(item):
        val = item.get(field)
        if val is None:
            # push nulls to the end
            return "" if reverse else "zzzzzzzzzzzz"
        return val

    try:
        return sorted(lst, key=get_sort_key, reverse=reverse)
    except Exception:
        return lst

def estimate_tokens(text: str) -> int:
    """
    Estimates token count based on a standard multiplier (approx 4 chars per token).
    """
    if not text:
        return 0
    return max(1, int(len(text) / 4))

def calculate_cost(prompt_tokens: int, completion_tokens: int, model_pricing: dict) -> float:
    """
    Calculates estimated cost in USD based on input rates.
    """
    p_rate = model_pricing.get("prompt_token_rate", 0.0)
    c_rate = model_pricing.get("completion_token_rate", 0.0)
    return float((prompt_tokens * p_rate) + (completion_tokens * c_rate))

def generate_mock_assistant_response(user_content: str, model_id: str) -> dict:
    """
    Generates a streaming-ready mock assistant response filled with rich metadata,
    markdown formatting, code blocks, references, and citations.
    """
    # Detect category from content
    category = "General"
    if any(k in user_content.lower() for k in ["code", "python", "javascript", "react", "program"]):
        category = "Programming"
    elif any(k in user_content.lower() for k in ["resume", "cv", "career", "job"]):
        category = "Resume & Career"
    elif any(k in user_content.lower() for k in ["portfolio", "project", "showcase"]):
        category = "Portfolio"
    elif any(k in user_content.lower() for k in ["math", "sum", "equation", "solve"]):
        category = "Mathematics"
    elif any(k in user_content.lower() for k in ["science", "physics", "chemistry", "biology"]):
        category = "Science"

    # Craft beautiful markdown response with code blocks
    markdown_content = f"""### Vidya AI Assistant: {category} Response

Thank you for your inquiry about **"{user_content[:60]}..."** using **{model_id}**. Here is a detailed, structured expert answer tailored specifically to your goals on the BrahmaVidya Galaxy portal.

#### Key Concept Breakdown
1. **Academic Excellence**: Combining rigorous curricula with real-time feedback ensures superior learning retention.
2. **Dynamic Ledger Auditing**: Transactions on the BrahmaVidya blockchain (and our double-entry ledger database) remain completely secure and immutable.

#### Implementation & Sample Code
If you are designing custom solutions, consider the following blueprint implementation:

```python
# BrahmaVidya AI - Automated Ledger Audit Hook
import hashlib
from datetime import datetime

def generate_audit_checksum(wallet_id: str, balance: float, ts: datetime) -> str:
    \"\"\"
    Computes secure verification checksum block.
    \"\"\"
    raw_payload = f"{{wallet_id}}:{{balance}}:{{ts.isoformat()}}"
    return hashlib.sha256(raw_payload.encode('utf-8')).hexdigest()

# Example Usage
print(generate_audit_checksum("W-10024", 1520.45, datetime.utcnow()))
```

#### Strategic Next Steps
- Review your current **Portfolio Builder** integration checklist.
- Verify your available reward points or **Vidya Tokens** to purchase courses or unlock premium mentoring sessions.
- Consult the attached resources below to read complete specs.
"""

    references = [
        {
            "title": "BrahmaVidya Enterprise API Standards",
            "url": "https://brahmavidya.edu/docs/api-standards",
            "snippet": "Contains absolute rules for building standard RESTful APIs with strict security permissions and token auditing."
        },
        {
            "title": "Double-Entry Ledger Architecture Documentation",
            "url": "https://brahmavidya.edu/docs/ledger-architecture",
            "snippet": "Specifies 3NF schemas for handling high-volume wallet credits, debits, and transfers safely."
        }
    ]

    citations = [
        {
            "source": "BrahmaVidya Master Specification v2.4",
            "start_char": 0,
            "end_char": 100
        }
    ]

    attachments = [
        {
            "name": "enterprise_architecture_blueprint.pdf",
            "file_type": "application/pdf",
            "file_size_bytes": 2048500,
            "url": "https://brahmavidya.edu/assets/enterprise_architecture_blueprint.pdf"
        }
    ]

    images_metadata = [
        {
            "name": "ledger_flowchart.png",
            "dimensions": "1200x800",
            "url": "https://brahmavidya.edu/assets/ledger_flowchart.png"
        }
    ]

    return {
        "content": markdown_content,
        "references": references,
        "citations": citations,
        "attachments": attachments,
        "images_metadata": images_metadata
    }
