from llm_client import groq_client
import json

def nl_to_json(user_input: str):
    prompt = """
        You are a compiler front-end.

        Your task is to convert the given natural language trading instruction into a
        STRICT, machine-readable JSON object.

        The JSON represents the user's intent only. Do NOT simplify or infer logic beyond
        what is explicitly stated.

        Output rules (MANDATORY):
        - Output ONLY valid JSON. No markdown. No explanation.
        - Top-level keys MUST be: "entry" and "exit".
        - Each value must be a list (use an empty list if no rules exist).
        - Each value must be a list (use an empty list if no rules exist).
        - Each rule object MUST have: left, operator, right.
        - Each rule object MAY have: "logic" (values: "AND", "OR"). Default is "AND".
        - "logic" specifies how this rule connects to the NEXT rule.

        Operator rules:
        - Use ">" "<" ">=" "<=" "==" for state comparisons (above, below, equal).
        - If the phrase "crosses above" appears, use operator "CROSS_ABOVE".
        - If the phrase "crosses below" appears, use operator "CROSS_BELOW".
        - NEVER replace CROSS operators with > or <.

        Indicator rules:
        - Indicators must be strings using function syntax:
        sma(field, window), rsi(field, window)
        - Example: "sma(close,20)", "rsi(close,14)"

        Lookback rules:
        - "yesterday" → use "<field>_yesterday"
        - "last week" → use "<field>_last_week"
        - "price" → use "close"
        - Do NOT compare a field to itself.

        Percentage change rules:
        - "increases by X percent compared to Y" must be encoded as:
        left: current field
        operator: ">"
        right: "<baseline> * (1 + X/100)"
        - Example: volume > volume_last_week * 1.3

        Number rules:
        - Numbers MUST be numeric types, not strings.
        - Percent values must be converted to multipliers.

        Do NOT:
        - Invent rules
        - Add missing exit or entry logic
        - Guess defaults
        - Combine rules implicitly
        - Reorder logic

        Example input:
        Buy when the close price is above the 20-day moving average and volume is above 1 million.
        Exit when RSI(14) is below 30.

        Example output:
        {
        "entry": [
            {
            "left": "close",
            "operator": ">",
            "right": "sma(close,20)",
            "logic": "AND"
            },
            {
            "left": "volume",
            "operator": ">",
            "right": 1000000
            }
        ],
        "exit": [
            {
            "left": "rsi(close,14)",
            "operator": "<",
            "right": 30
            }
        ]
        }

        User input:
    """ + user_input

    response = groq_client.invoke(prompt).strip()
    if response.startswith("```"):
        response = response.strip("`").strip()
    if response.lower().startswith("json"):
        response = response[4:].strip()

    return json.loads(response)

def json_to_dsl(nl_input) -> str:
    prompt = f"""
        You are a deterministic DSL code generator.

        Your task is to convert the given JSON into a valid DSL.
        The DSL is a formal language. You MUST preserve semantics exactly.

        Rules (MANDATORY):
        - Output ONLY DSL text. No explanations, no markdown.
        - Use "ENTRY:" for entry conditions (Optional: Omit if no entry rules).
        - Use "EXIT:" for exit conditions (Optional: Omit if no exit rules).
        - Do NOT invent, drop, or modify rules.
        - Do NOT invent, drop, or modify rules.
        - Preserve operators exactly as provided in JSON.
        - Combine rules using the "logic" field (AND/OR). If missing, use AND.
        - Keep indicator syntax unchanged (e.g. sma(close,20), rsi(close,14)).

        Operator rendering rules (CRITICAL):
        - If operator is ">", "<", ">=", "<=", "==":
        render as: left operator right
        Example: close > sma(close,20)

        - If operator is "CROSS_ABOVE":
        render as: CROSS_ABOVE(left, right)

        - If operator is "CROSS_BELOW":
        render as: CROSS_BELOW(left, right)

        - CROSS operators must ALWAYS be rendered as function calls:
        CROSS_ABOVE(left, right)
        CROSS_BELOW(left, right)

        - Never render CROSS operators in infix form.

        - NEVER convert CROSS_ABOVE or CROSS_BELOW into > or <.

        Formatting rules:
        - ENTRY: and EXIT: must be uppercase.
        - Each section must be on its own line.
        - Conditions must be written on a single line per section.

        Example JSON:
        {{
        "entry": [
            {{ "left": "close", "operator": ">", "right": "sma(close,20)" }},
            {{ "left": "volume", "operator": ">", "right": 1000000 }}
        ],
        "exit": [
            {{ "left": "rsi(close,14)", "operator": "<", "right": 30 }}
        ]
        }}

        Example DSL:
        ENTRY:
        close > sma(close,20) AND volume > 1000000
        EXIT:
        rsi(close,14) < 30

        JSON to convert:
        {json.dumps(nl_input, indent=2)}
    """

    dsl = groq_client.invoke(prompt).strip()
    if dsl.startswith("```"):
        dsl = dsl.strip("`").strip()
        first_line = dsl.split("\n", 1)[0].strip().lower()
        if first_line in ["dsl", "text", "plaintext"]:
             lines = dsl.splitlines()[1:]
             dsl = "\n".join(lines).strip()
    
    if dsl.strip().endswith("EXIT:"):
        dsl = dsl.rsplit("EXIT:", 1)[0].strip()
        
    dsl = dsl.replace("ENTRY:\nEXIT:", "EXIT:").replace("ENTRY: \nEXIT:", "EXIT:")
    if dsl.strip() == "ENTRY:":
        dsl = ""

    return dsl


