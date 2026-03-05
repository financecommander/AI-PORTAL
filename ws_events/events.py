"""WebSocket event types for pipeline progress streaming."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

import json


class EventType(str, Enum):
    PIPELINE_STARTED = "pipeline_started"
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    AGENT_FAILED = "agent_failed"
    PIPELINE_METRICS = "pipeline_metrics"
    PIPELINE_COMPLETED = "pipeline_completed"
    PIPELINE_FAILED = "pipeline_failed"
    ERROR = "error"


@dataclass
class WSEvent:
    type: EventType
    pipeline_id: str
    data: dict

    def to_json(self) -> str:
        return json.dumps({
            "type": self.type.value,
            "pipeline_id": self.pipeline_id,
            "data": self.data,
        })
