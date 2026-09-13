import json
from pathlib import Path

from transformers import TrainerCallback


class ProgressFileCallback(TrainerCallback):
    def __init__(self, task: str):
        self.path = Path(__file__).with_name(f"{task}_training_status.json")

    def _write(self, state, args, status: str = "training"):
        payload = {
            "status": status,
            "step": state.global_step,
            "total_steps": state.max_steps,
            "epoch": state.epoch or 0,
            "total_epochs": args.num_train_epochs,
        }
        self.path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def on_step_end(self, args, state, control, **kwargs):
        self._write(state, args)

    def on_train_end(self, args, state, control, **kwargs):
        self._write(state, args, status="completed")