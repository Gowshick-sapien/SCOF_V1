import json
import logging
import asyncio
from typing import Dict, Any, Optional
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import redis.asyncio as redis

from .topics import (
    TOPIC_DISRUPTIONS_TRIGGERED,
    TOPIC_WHATIF_REQUESTED,
    TOPIC_DECISIONS_COMPLETED,
    TOPIC_ORCHESTRATION_FAILED,
    TOPIC_AGENTS_ACTIVITY,
    TOPIC_DLQ,
)
from ..config import KAFKA_CONSUMER_MAX_RETRIES

logger = logging.getLogger(__name__)

class EventBus:
    def __init__(self, bootstrap_servers: str, redis_client: redis.Redis):
        self.bootstrap_servers = bootstrap_servers
        self.redis = redis_client
        self.producer: Optional[AIOKafkaProducer] = None
        self.consumer: Optional[AIOKafkaConsumer] = None
        
        # Mapping from topic to handler function
        # handler(envelope: dict) -> None
        self.handlers = {}
        
    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_servers,
            enable_idempotence=True
        )
        await self.producer.start()
        
        topics = [
            TOPIC_DISRUPTIONS_TRIGGERED,
            TOPIC_WHATIF_REQUESTED,
            TOPIC_DECISIONS_COMPLETED,
            TOPIC_ORCHESTRATION_FAILED,
            TOPIC_AGENTS_ACTIVITY,
        ]
        
        self.consumer = AIOKafkaConsumer(
            *topics,
            bootstrap_servers=self.bootstrap_servers,
            group_id="scof-api-gateway",
            auto_offset_reset="latest",
            enable_auto_commit=False,
            max_poll_records=10
        )
        await self.consumer.start()
        
        # Start background task for consuming
        self._consume_task = asyncio.create_task(self._consume_loop())
        logger.info(f"EventBus started, listening on topics: {topics}")
        
    async def stop(self):
        if self._consume_task:
            self._consume_task.cancel()
        if self.consumer:
            await self.consumer.stop()
        if self.producer:
            await self.producer.stop()
        logger.info("EventBus stopped")
            
    def register_handler(self, topic: str, handler_func):
        self.handlers[topic] = handler_func
        
    async def publish(self, topic: str, key: str, envelope: dict):
        if not self.producer:
            raise RuntimeError("Producer not started")
            
        value = json.dumps(envelope).encode("utf-8")
        await self.producer.send_and_wait(topic, key=key.encode("utf-8"), value=value)
        logger.info(f"Published event {envelope.get('event_id')} to {topic}")
        
    async def publish_dlq(self, envelope: dict):
        if not self.producer:
            return
        value = json.dumps(envelope).encode("utf-8")
        await self.producer.send_and_wait(TOPIC_DLQ, key=b"dlq", value=value)
        logger.warning(f"Sent message to DLQ: {envelope.get('dlq_reason')}")

    async def _consume_loop(self):
        if not self.consumer:
            return
            
        try:
            async for msg in self.consumer:
                topic = msg.topic
                
                # Check deserialization
                try:
                    envelope = json.loads(msg.value.decode("utf-8"))
                except Exception as e:
                    import base64
                    raw_b64 = base64.b64encode(msg.value).decode("utf-8") if msg.value else ""
                    logger.error(f"Failed to deserialize message on {topic}: {e}")
                    await self.publish_dlq({
                        "dlq_reason": "DESERIALIZATION_ERROR",
                        "error": str(e),
                        "source_topic": topic,
                        "partition": msg.partition,
                        "offset": msg.offset,
                        "timestamp": msg.timestamp,
                        "raw_payload_base64": raw_b64
                    })
                    # Commit offset so we don't get stuck
                    await self.consumer.commit()
                    continue
                    
                event_id = envelope.get("event_id")
                if not event_id:
                    logger.warning(f"Message on {topic} missing event_id, skipping deduplication")
                else:
                    # Idempotency check
                    is_processed = await self.redis.exists(f"processed_events:{event_id}")
                    if is_processed:
                        logger.debug(f"Event {event_id} already processed, skipping")
                        await self.consumer.commit()
                        continue
                        
                handler = self.handlers.get(topic)
                if not handler:
                    logger.warning(f"No handler registered for topic {topic}")
                    await self.consumer.commit()
                    continue
                    
                success = False
                for attempt in range(KAFKA_CONSUMER_MAX_RETRIES):
                    try:
                        await handler(envelope)
                        success = True
                        break
                    except Exception as e:
                        logger.error(f"Error handling event {event_id} (attempt {attempt+1}): {e}")
                        await asyncio.sleep(2 ** attempt)
                        
                if success:
                    if event_id:
                        await self.redis.setex(f"processed_events:{event_id}", 86400, "1") # 24 hour TTL
                    await self.consumer.commit()
                else:
                    logger.error(f"Exhausted retries for event {event_id}, sending to DLQ")
                    await self.publish_dlq({
                        "original_event": envelope,
                        "error": "Max retries exceeded",
                        "dlq_reason": "MAX_RETRIES_EXCEEDED"
                    })
                    await self.consumer.commit() # Move past poison message
                    
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Consumer loop error: {e}")
