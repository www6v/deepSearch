from agent import Agent
from prompt import prompt

import os
import asyncio

os.environ["JINA_API_KEY"] = ''
os.environ["OPENROUTER_API_KEY"] = ''

async def main():
    task = """
    Help me plan a 3 day holiday in Europe in May for under 2000 EURO.
    1. I need specific flight and hotel recommendations.
    2. I want the destination to be warm.
    3. I want to have a beach nearby the hotel.
    I live in Germany.
    """

    agent = Agent(task=task, prompt=prompt)
    print(agent.workspace.to_string())


    await agent.run(loop=False)
    agent.workspace.to_string()


    await agent.run(loop=False)
    agent.workspace.to_string()


    await agent.run(loop=False)
    agent.workspace.to_string()


if __name__ == "__main__":
    asyncio.run(main())
