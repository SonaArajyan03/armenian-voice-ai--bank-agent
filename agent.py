from __future__ import annotations

from dotenv import load_dotenv
from livekit import agents
from livekit.agents import Agent, AgentSession, RoomInputOptions
from livekit.plugins import openai

from bank_support.answering import BankSupportOrchestrator
from bank_support.prompts import VOICE_AGENT_SYSTEM_PROMPT

load_dotenv()


class BankVoiceAgent(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=VOICE_AGENT_SYSTEM_PROMPT)
        self.orchestrator = BankSupportOrchestrator()

    async def on_user_turn_completed(self, chat_ctx, new_message):  # type: ignore[override]
        answer = self.orchestrator.answer(new_message.text_content)
        chat_ctx.add_message(role="assistant", content=answer)


async def entrypoint(ctx: agents.JobContext) -> None:
    await ctx.connect()

    session = AgentSession(
        stt=openai.STT(model="gpt-4o-mini-transcribe"),
        llm=openai.LLM(model="gpt-4.1-mini"),
        tts=openai.TTS(model="gpt-4o-mini-tts", voice="alloy"),
    )

    await session.start(
        room=ctx.room,
        agent=BankVoiceAgent(),
        room_input_options=RoomInputOptions(),
    )

    await session.generate_reply(
        instructions=(
            "Greet the user in Armenian and explain that you can help only with credits, deposits, "
            "and branch locations for the supported Armenian banks."
        )
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
