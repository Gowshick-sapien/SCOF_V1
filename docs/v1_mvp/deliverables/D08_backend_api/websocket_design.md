# WebSocket Design

## Channel Architecture

| Channel Path | Trigger | Payload Model | Push Strategy |
|---|---|---|---|
| `ws://.../ws/dashboard/state` | Kafka `scof.decisions.completed` or periodic (30s) | Complete dashboard state snapshot | Model A: full state push |
| `ws://.../ws/decisions/live` | Kafka `scof.decisions.completed` or `scof.orchestration.failed` | Decision summary or failure summary | Event-driven |
| `ws://.../ws/agents/activity` | Kafka `scof.agents.activity` | Agent lifecycle event | Event-driven |

## Dashboard State Push (Model A)

When a `scof.decisions.completed` event arrives, the notification consumer:
1. Invalidates the Redis dashboard cache.
2. Assembles a fresh dashboard state snapshot.
3. Broadcasts the complete snapshot to all connected `dashboard/state` clients.

A periodic heartbeat (every 30 seconds) also broadcasts the current cached state to handle missed events and client reconnections.

Clients do **not** need to call `GET /dashboard/state` after receiving a WebSocket push -- the push contains the full state.

## Connection Lifecycle

- **Connect**: Client connects to a channel path. Server registers the WebSocket in the `ConnectionManager` per-channel set. Server sends an initial state snapshot (for `dashboard/state`) or an acknowledgment message.
- **Heartbeat**: Server sends a ping frame every 15 seconds. Client must respond with pong within 10 seconds or the connection is considered dead.
- **Disconnect**: Server removes the WebSocket from the channel set.
- **Reconnect**: Client-side responsibility. On reconnect, the server sends the current state as the first message.
