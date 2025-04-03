from tools import ScrapTool, SearchTool
from prompt import Prompt
from workspace import Workspace
from util import extract_largest_json


import asyncio
import re
import traceback
from datetime import datetime
from typing import (
    Any,
    Dict,    
)


class Agent:
    # Tools the agent can call
    tools = {"search": SearchTool(), "scrape": ScrapTool()}

    def __init__(
        self,
        task: str,
        prompt: Prompt,
        current_date: str = datetime.now().strftime("%Y-%m-%d"),
    ):
        self.task = task
        self.prompt = prompt
        self.current_date = current_date
        self.tool_records = None
        self.workspace = Workspace()
        self.round = 0

    async def run_tool(
        self, tool_id: str, tool_input: str, context: str | None = None
    ) -> str:
        try:
            assert tool_id in ["search", "scrape"], f"Illegal tool: {tool_id}"
            tool = self.tools[tool_id]
            result = await tool(tool_input, context)
            return result
        except Exception as e:
            print(f"Failed to run tool {e}")
            print(traceback.format_exc())
            return f"Tool execution failed: {e}"

    async def run(self, loop=True, max_rounds: int | None = None) -> Dict[str, Any]:
        while True:
            try:
                # Rate limiting - 1 round per 20 seconds
                await asyncio.sleep(20)
                ######   clear_output(wait=True)

                response = await self.prompt.run(
                    {
                        "current_date": self.current_date,
                        "task": self.task,
                        "workspace": self.workspace.to_string(),
                        "tool_records": self.tool_records,
                    }
                )

                response = re.sub(
                    r"(?:<think>)?.*?</think>", "", response, flags=re.DOTALL
                )
                response_json = extract_largest_json(response)
                assert response_json

                self.workspace.update_blocks(
                    response_json.get("status_update", "IN_PROGRESS"),
                    response_json.get("memory_updates"),
                    response_json.get("answer", None),
                )

                assert "tool_calls" in response_json

                tool_calls = response_json["tool_calls"]

                tasks = [
                    self.run_tool(call["tool"], call["input"], self.task)
                    for call in tool_calls
                ]

                tool_outputs = await asyncio.gather(*tasks)

                tool_records = [
                    {**call, "output": output}
                    for call, output in zip(tool_calls, tool_outputs)
                ]

                # Will be appended to the prompt in the next round
                self.tool_records = tool_records

            except Exception as e:
                print(f"Error in agent loop: {str(e)}")
                await asyncio.sleep(10)
                continue

            self.round += 1
            if max_rounds and self.round > max_rounds:
                break

            if not loop:
                break

            if self.workspace.is_done():
                break
