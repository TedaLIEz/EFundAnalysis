import asyncio

from workflows import Workflow, step
from workflows.events import (
    Event,
    StartEvent,
    StopEvent,
)

from core.llm.model import create_llm


class JokeEvent(Event):
    joke: str


class JokeFlow(Workflow):
    llm = create_llm()

    @step
    async def generate_joke(self, ev: StartEvent) -> JokeEvent:
        topic = ev.topic

        prompt = f"Write your best joke about {topic}."
        response = await self.llm.acomplete(prompt)
        return JokeEvent(joke=str(response))

    @step
    async def critique_joke(self, ev: JokeEvent) -> StopEvent:
        joke = ev.joke

        prompt = f"Give a thorough analysis and critique of the following joke: {joke}"
        response = await self.llm.acomplete(prompt)
        return StopEvent(result=str(response))


async def main():
    w = JokeFlow(timeout=60, verbose=False)
    result = await w.run(topic="Microsoft")
    print(str(result))


if __name__ == "__main__":
    asyncio.run(main())
