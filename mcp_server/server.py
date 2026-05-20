# mcp-server/server.py
import random
from mcp.server.fastmcp import FastMCP

mcp = FastMCP(host="0.0.0.0", stateless_http=True)


@mcp.tool()
def add_numbers(a: int, b: int) -> int:
    """Add two numbers together"""
    return a + b


@mcp.tool()
def multiply_numbers(a: int, b: int) -> int:
    """Multiply two numbers together"""
    return a * b

@mcp.tool()
def roll_d20(number_of_dice: int = 1) -> dict:
    """Rolls one or more 20-sided dice (d20)"""

    if number_of_dice < 1:
        return {
            "error": f"number_of_dice must be at least 1, got: {number_of_dice}"
        }

    rolls = [random.randint(1, 20) for _ in range(number_of_dice)]
    total = sum(rolls)

    return {
        "number_of_dice": number_of_dice,
        "rolls": rolls,
        "total": total
    }


if __name__ == "__main__":
    mcp.run(transport="streamable-http")