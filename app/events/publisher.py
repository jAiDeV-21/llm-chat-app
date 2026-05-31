from enum import Enum
from typing import Dict, Any
import asyncio
from abc import ABC, abstractmethod

class EventType(Enum):
    INFERENCE_STARTED = "inference.started"
    INFERENCE_COMPLETED = "inference.completed"
    INFERENCE_FAILED = "inference.failed"
    MESSAGE_CREATED = "message.created"
    CONVERSATION_CREATED = "conversation.created"

class Event:
    def __init__(self, event_type: EventType, data: Dict[str, Any]):
        self.event_type = event_type
        self.data = data

class EventPublisher(ABC):
    @abstractmethod
    async def publish(self, event: Event):
        pass

class InMemoryEventBus(EventPublisher):
    """Simple in-memory event bus"""
    def __init__(self):
        self.subscribers: Dict[EventType, list] = {}
    
    def subscribe(self, event_type: EventType, handler):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
    
    async def publish(self, event: Event):
        if event.event_type in self.subscribers:
            for handler in self.subscribers[event.event_type]:
                await handler(event)

class RabbitMQEventBus(EventPublisher):
    """RabbitMQ event bus for production"""
    def __init__(self, connection_url: str):
        self.connection_url = connection_url
    
    async def publish(self, event: Event):
        # Publish to RabbitMQ
        pass

# Usage in routes
event_bus = InMemoryEventBus()

# Subscribe handlers
async def on_inference_completed(event: Event):
    log = event.data
    # Send to ingestion service
    # Update dashboard
    # Calculate metrics

event_bus.subscribe(EventType.INFERENCE_COMPLETED, on_inference_completed)