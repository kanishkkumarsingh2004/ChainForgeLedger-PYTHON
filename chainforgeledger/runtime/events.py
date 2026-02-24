"""
Event System - Modular event management framework

A robust, extensible event system for blockchain operations.
Features:
- Event bus architecture
- Multiple event types (transaction, block, contract, network)
- Event filtering and subscription
- Event replay functionality
- Event validation and schema checking
- Performance optimization with async processing
- Plugin system integration
"""

import time
from typing import Dict, List, Optional, Set, Callable, Any
from dataclasses import dataclass, field


@dataclass
class Event:
    """Represents an event with metadata"""
    event_type: str
    data: Dict[str, Any]
    timestamp: float = field(default_factory=lambda: time.time())
    id: str = field(default_factory=lambda: f"{time.time():.8f}")


class EventSystem:
    """
    Event system for blockchain operations
    """
    
    def __init__(self, options: Dict = None):
        options = options or {}
        self.subscribers: Dict[str, List[Callable]] = {}
        self.event_history: List[Event] = []
        self.max_history_size = options.get('maxHistorySize', 10000)
        self.event_queue: List[Event] = []
        self.processing_queue = False
        self.event_types: Set[str] = {
            'block.created',
            'block.added',
            'block.finalized',
            'transaction.created',
            'transaction.added',
            'transaction.processed',
            'transaction.confirmed',
            'transaction.failed',
            'contract.created',
            'contract.executed',
            'contract.stopped',
            'contract.storage.updated',
            'network.peer.connected',
            'network.peer.disconnected',
            'network.message.received',
            'network.message.sent',
            'validator.elected',
            'validator.slash',
            'validator.rewarded',
            'state.updated',
            'gas.price.changed',
            'fork.detected',
            'fork.resolved',
            'bridge.transaction.created',
            'bridge.transaction.relayed',
            'bridge.transaction.confirmed'
        }
        
        self.event_schemas: Dict[str, Dict[str, str]] = {}
        self.setup_default_schemas()
    
    def setup_default_schemas(self):
        """Setup default event schemas"""
        # Block events
        self.event_schemas['block.created'] = {
            'blockNumber': 'number',
            'blockHash': 'string',
            'timestamp': 'number',
            'transactionCount': 'number'
        }
        
        self.event_schemas['block.added'] = {
            'blockNumber': 'number',
            'blockHash': 'string',
            'previousHash': 'string',
            'timestamp': 'number',
            'transactionCount': 'number'
        }
        
        self.event_schemas['block.finalized'] = {
            'blockNumber': 'number',
            'blockHash': 'string',
            'timestamp': 'number',
            'confirmationCount': 'number'
        }
        
        # Transaction events
        self.event_schemas['transaction.created'] = {
            'transactionId': 'string',
            'from': 'string',
            'to': 'string',
            'value': 'number',
            'gasLimit': 'number',
            'gasPrice': 'number'
        }
        
        self.event_schemas['transaction.added'] = {
            'transactionId': 'string',
            'blockNumber': 'number',
            'blockHash': 'string',
            'index': 'number'
        }
    
    def subscribe(self, event_type: str, callback: Callable):
        """Subscribe to events of specific type"""
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(callback)
    
    def unsubscribe(self, event_type: str, callback: Callable):
        """Unsubscribe from events of specific type"""
        if event_type in self.subscribers:
            self.subscribers[event_type] = [
                cb for cb in self.subscribers[event_type] if cb != callback
            ]
    
    def publish(self, event_type: str, data: Dict[str, Any]):
        """Publish an event"""
        # Validate event type
        if event_type not in self.event_types:
            raise ValueError(f"Unknown event type: {event_type}")
        
        # Validate data against schema
        if event_type in self.event_schemas:
            self._validate_event_data(event_type, data)
        
        event = Event(event_type, data)
        
        # Add to history
        self.event_history.append(event)
        if len(self.event_history) > self.max_history_size:
            self.event_history.pop(0)
        
        # Add to processing queue
        self.event_queue.append(event)
        self._process_queue()
    
    def _validate_event_data(self, event_type: str, data: Dict[str, Any]):
        """Validate event data against schema"""
        schema = self.event_schemas[event_type]
        for field_name, field_type in schema.items():
            if field_name not in data:
                raise ValueError(f"Missing required field: {field_name}")
            
            value = data[field_name]
            if not self._validate_type(value, field_type):
                raise ValueError(f"Invalid type for field {field_name}: expected {field_type}")
    
    def _validate_type(self, value: Any, expected_type: str) -> bool:
        """Validate value type against expected type"""
        if expected_type == 'string':
            return isinstance(value, str)
        elif expected_type == 'number':
            return isinstance(value, (int, float))
        elif expected_type == 'boolean':
            return isinstance(value, bool)
        elif expected_type == 'object':
            return isinstance(value, dict)
        elif expected_type == 'array':
            return isinstance(value, list)
        
        return True
    
    def _process_queue(self):
        """Process event queue"""
        if self.processing_queue:
            return
        
        self.processing_queue = True
        
        while self.event_queue:
            event = self.event_queue.pop(0)
            
            # Notify subscribers
            if event.event_type in self.subscribers:
                for callback in self.subscribers[event.event_type]:
                    try:
                        callback(event)
                    except Exception as e:
                        print(f"Error in event callback: {e}")
        
        self.processing_queue = False
    
    def get_events(self, options: Dict = None) -> List[Event]:
        """Get events with filtering options"""
        options = options or {}
        events = list(self.event_history)
        
        if 'eventType' in options:
            events = [e for e in events if e.event_type == options['eventType']]
        
        if 'startTime' in options:
            events = [e for e in events if e.timestamp >= options['startTime']]
        
        if 'endTime' in options:
            events = [e for e in events if e.timestamp <= options['endTime']]
        
        if 'limit' in options:
            events = events[-options['limit']:]
        
        return events
    
    def clear_history(self):
        """Clear event history"""
        self.event_history.clear()
    
    def get_event_types(self) -> Set[str]:
        """Get all supported event types"""
        return set(self.event_types)
    
    def add_event_type(self, event_type: str, schema: Dict = None):
        """Add new event type with optional schema"""
        self.event_types.add(event_type)
        if schema:
            self.event_schemas[event_type] = schema
    
    def remove_event_type(self, event_type: str):
        """Remove event type"""
        if event_type in self.event_types:
            self.event_types.remove(event_type)
            if event_type in self.event_schemas:
                del self.event_schemas[event_type]
            if event_type in self.subscribers:
                del self.subscribers[event_type]
