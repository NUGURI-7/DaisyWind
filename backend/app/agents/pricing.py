"""
    @project: DaisyWind
    @Author: niu
    @file: pricing.py.py
    @date: 2026/4/10 15:24
    @desc: Token 价格表与费用计算。
"""



# 单价：美元 / 百万 token
TOKEN_PRICE: dict[str, dict[str, float]] = {
    "deepseek-chat":            {"input": 0.27,  "output": 1.10},
    "deepseek-reasoner":        {"input": 0.55,  "output": 2.19},
    "gemini-3.1-pro-preview":   {"input": 2.00,  "output": 12.00},
    "gemini-3-flash-preview":   {"input": 0.50,  "output": 3.00},
}



def calc_cost(model_name: str, input_tokens: int, output_tokens: int) -> float | None:
    """计算一次调用的费用（美元）。模型不在价格表中时返回 None。"""
    price = TOKEN_PRICE.get(model_name)
    if not price:
        return None
    return ((input_tokens * price["input"]) + output_tokens * price["output"]) / 1_000_000
