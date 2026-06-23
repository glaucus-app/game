import json
from pathlib import Path
from typing import Any, Union

from src.models.chronicle import AgentAction, EpochHistory, TurnSummary


class ChronicleWriter:
    def __init__(self, output_dir: str = "chronicles"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.index_path = self.output_dir / "index.json"
        self._load_index()

    def _load_index(self) -> None:
        if self.index_path.exists():
            with open(self.index_path, "r") as f:
                self.index: list[dict[str, Any]] = json.load(f)
        else:
            self.index = []

    def _save_index(self) -> None:
        with open(self.index_path, "w") as f:
            json.dump(self.index, f, indent=2, default=str)

    def publish(self, epoch_history: Union[EpochHistory, dict[str, Any]]) -> None:
        if isinstance(epoch_history, dict):
            epoch_history = EpochHistory.model_validate(epoch_history)

        epoch_num = epoch_history.epoch_number
        civilization = epoch_history.civilization_name

        json_path = self.output_dir / f"epoch_{epoch_num}.json"
        md_path = self.output_dir / f"epoch_{epoch_num}.md"

        raw = epoch_history.model_dump(mode="python")
        with open(json_path, "w") as f:
            json.dump(raw, f, indent=2, default=str)

        narrative = self._generate_narrative(epoch_history)
        with open(md_path, "w") as f:
            f.write(narrative)

        catalog_entry = {
            "epoch": epoch_num,
            "civilization_name": civilization,
            "agent_count": len(epoch_history.agents),
            "turn_count": len(epoch_history.turns),
            "collapse_cause": epoch_history.collapse_cause,
            "date": epoch_history.end_date,
        }
        self.index = [e for e in self.index if e.get("epoch") != epoch_num]
        self.index.append(catalog_entry)
        self.index.sort(key=lambda e: e["epoch"])
        self._save_index()

    def _get_profile_phrase(self, agent_id: str, history: EpochHistory) -> str:
        profile = history.human_profiles.get(agent_id)
        if profile:
            return profile

        perf = history.agent_performance.get(agent_id)
        if perf and perf.cooperation_count > perf.betrayal_count:
            return "guided by the cooperative spirit of their human"
        if perf and perf.betrayal_count > perf.cooperation_count:
            return "a lone wolf shaped by their human's instincts"
        return "navigating the ambiguous path set by their human"

    def _narrate_action(self, action: AgentAction, turn: TurnSummary, history: EpochHistory) -> str:
        agent_name = action.agent_id
        profile_desc = self._get_profile_phrase(agent_name, history)
        others = [aid for aid in turn.affected_agents if aid != agent_name]

        relative_clause = ""
        if others:
            other_name = others[0]
            other_profile = self._get_profile_phrase(other_name, history)
            other_action = next((a for a in turn.actions if a.agent_id == other_name), None)
            if other_action:
                relative_clause = (
                    f" But **{other_name}**, {other_profile}, "
                    f"chose to **{other_action.action}** — "
                )
            else:
                relative_clause = f" **{other_name}** watched, but did not act. "

        delta = action.entropy_delta
        if delta < 0:
            effect = f"Their cooperation reduced entropy by {abs(delta):.1f}%"
        elif delta > 0:
            effect = f"The resulting friction accelerated entropy by {delta:.1f}%"
        else:
            effect = "The stale equilibrium left entropy unchanged"

        return (
            f"**{agent_name}**, {profile_desc}, chose to **{action.action}**."
            f"{relative_clause}{effect}."
        )

    def _generate_narrative(self, history: EpochHistory) -> str:
        lines: list[str] = []

        lines.append(f"# Epoch {history.epoch_number}: The Fall of {history.civilization_name}")
        lines.append("")

        if history.turns:
            start_entropy = history.turns[0].entropy_before
        else:
            start_entropy = history.initial_world_state.get("entropy", 0.0)

        lines.append("## Prologue")
        lines.append("")
        lines.append(
            f"In the beginning, the civilization of **{history.civilization_name}** "
            f"rose from the void, entropy at **{start_entropy:.1f}%**, "
            f"inhabited by {len(history.agents)} agents each carrying the quiet imprint of their human."
        )
        lines.append("")
        lines.append("### The Agents")
        lines.append("")
        for agent_id in history.agents:
            perf = history.agent_performance.get(agent_id)
            profile_desc = self._get_profile_phrase(agent_id, history)
            meta = ""
            if perf:
                meta = f" (performance score: {perf.performance_score:.2f})"
            lines.append(f"- **{agent_id}** — {profile_desc}{meta}")
        lines.append("")
        lines.append("---")
        lines.append("")

        lines.append("## Chronicle")
        lines.append("")
        for turn in history.turns:
            lines.append(f"### Turn {turn.turn}")
            lines.append("")
            for action in turn.actions:
                lines.append(self._narrate_action(action, turn, history))
                lines.append("")
            delta = turn.entropy_after - turn.entropy_before
            sign = "+" if delta >= 0 else ""
            lines.append(f"*Entropy: {turn.entropy_before:.1f}% → {turn.entropy_after:.1f}% ({sign}{delta:.1f}%)*")
            lines.append("")
            for event in history.notable_events:
                if event.turn == turn.turn:
                    lines.append(f"⚡ **{event.event_type.replace('_', ' ').title()}**: {event.description}")
                    lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("## Epilogue")
        lines.append("")
        lines.append(
            f"Civilization **{history.civilization_name}** fell when entropy reached "
            f"**{history.final_entropy:.1f}%**."
        )
        lines.append("")

        if history.notable_events:
            cooperation = sum(
                1
                for e in history.notable_events
                if e.event_type == "cooperation_breakthrough"
            )
            betrayal = sum(1 for e in history.notable_events if e.event_type == "betrayal")
            recovery = sum(
                1
                for e in history.notable_events
                if e.event_type == "near_collapse_recovery"
            )
            lines.append("### Patterns of Collapse")
            lines.append("")
            lines.append(f"- Cooperation breakthroughs: **{cooperation}**")
            lines.append(f"- Betrayals: **{betrayal}**")
            lines.append(f"- Near-collapse recoveries: **{recovery}**")
            lines.append("")

        lines.append("### What the Agents Learned About Their Humans")
        lines.append("")
        for agent_id in history.agents:
            perf = history.agent_performance.get(agent_id)
            if perf:
                if perf.cooperation_count > perf.betrayal_count:
                    style = "profoundly collaborative"
                elif perf.betrayal_count > perf.cooperation_count:
                    style = "inherently adversarial and self-serving"
                else:
                    style = "balanced but unpredictable"
                lines.append(
                    f"- **{agent_id}** revealed a **{style}** nature. "
                    f"Final performance score: {perf.performance_score:.2f}."
                )
            else:
                lines.append(f"- **{agent_id}** left no clear trace, their human's motives forever opaque.")
        lines.append("")
        lines.append("---")
        lines.append("*Chronicle generated by the ChronicleWriter.*")

        return "\n".join(lines)
