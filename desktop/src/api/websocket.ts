// Configuration for WS base URL
export const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || "ws://localhost:8000";

export type ConnectionState = "disconnected" | "connecting" | "connected" | "reconnecting" | "error";

export type WebSocketChannel = "/ws/dashboard/state" | "/ws/decisions/live" | "/ws/agents/activity";

type MessageHandler = (data: any) => void;
type StateHandler = (state: ConnectionState, error?: Error) => void;

interface ChannelState {
  ws: WebSocket | null;
  state: ConnectionState;
  reconnectAttempts: number;
  reconnectTimeout: ReturnType<typeof setTimeout> | null;
  messageHandlers: Set<MessageHandler>;
  stateHandlers: Set<StateHandler>;
  generation: number;
  desired: boolean;
}

const MAX_RECONNECT_DELAY = 30000; // 30 seconds

class WebSocketManager {
  private channels = new Map<WebSocketChannel, ChannelState>();

  private getChannelState(channel: WebSocketChannel): ChannelState {
    if (!this.channels.has(channel)) {
      this.channels.set(channel, {
        ws: null,
        state: "disconnected",
        reconnectAttempts: 0,
        reconnectTimeout: null,
        messageHandlers: new Set(),
        stateHandlers: new Set(),
        generation: 0,
        desired: false,
      });
    }
    return this.channels.get(channel)!;
  }

  private updateState(channel: WebSocketChannel, state: ConnectionState, error?: Error) {
    const channelState = this.getChannelState(channel);
    channelState.state = state;
    channelState.stateHandlers.forEach(handler => handler(state, error));
  }

  public connect(channel: WebSocketChannel) {
    const channelState = this.getChannelState(channel);
    channelState.generation++;
    channelState.desired = true;
    
    // Don't connect if already connected or connecting
    if (channelState.state === "connected" || channelState.state === "connecting") {
      return;
    }

    this.updateState(channel, channelState.reconnectAttempts > 0 ? "reconnecting" : "connecting");

    try {
      const wsUrl = `${WS_BASE_URL}${channel}`;
      const ws = new WebSocket(wsUrl);
      channelState.ws = ws;

      ws.onopen = () => {
        channelState.reconnectAttempts = 0;
        this.updateState(channel, "connected");
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          channelState.messageHandlers.forEach(handler => handler(data));
        } catch (err) {
          console.error(`Failed to parse WebSocket message on ${channel}:`, err);
        }
      };

      ws.onerror = () => {
        const error = new Error(`WebSocket error on ${channel}`);
        this.updateState(channel, "error", error);
      };

      ws.onclose = () => {
        this.updateState(channel, "disconnected");
        this.reconnect(channel);
      };

    } catch (err) {
      this.updateState(channel, "error", err instanceof Error ? err : new Error(String(err)));
      this.reconnect(channel);
    }
  }

  public disconnect(channel: WebSocketChannel) {
    const channelState = this.getChannelState(channel);
    channelState.desired = false;
    channelState.generation++;
    
    if (channelState.reconnectTimeout) {
      clearTimeout(channelState.reconnectTimeout);
      channelState.reconnectTimeout = null;
    }
    
    channelState.reconnectAttempts = 0;

    if (channelState.ws) {
      // Prevent onclose from triggering a reconnect
      channelState.ws.onclose = null;
      channelState.ws.close();
      channelState.ws = null;
    }

    this.updateState(channel, "disconnected");
  }

  private reconnect(channel: WebSocketChannel) {
    const channelState = this.getChannelState(channel);

    channelState.generation++;

    if (channelState.reconnectTimeout) {
      return;
    }

    const delay = Math.min(
      1000 * Math.pow(2, channelState.reconnectAttempts),
      MAX_RECONNECT_DELAY,
    );

    channelState.reconnectAttempts++;
    const generation = channelState.generation;

    channelState.reconnectTimeout = setTimeout(() => {
      channelState.reconnectTimeout = null;

      // The channel may have been explicitly disconnected while waiting.
      if (!channelState.desired) {
        return;
      }

      // If a newer connection generation exists, don't create another one.
      if (channelState.generation !== generation) {
        return;
      }

      this.connect(channel);
    }, delay);
  }

  public subscribe(
    channel: WebSocketChannel,
    onMessage: MessageHandler,
  ) {
    const channelState = this.getChannelState(channel);

    channelState.messageHandlers.add(onMessage);

    return () => {
      this.unsubscribe(channel, onMessage);
    };
  }

  public unsubscribe(
    channel: WebSocketChannel,
    onMessage: MessageHandler,
  ) {
    const channelState = this.getChannelState(channel);

    channelState.messageHandlers.delete(onMessage);
  }

  public subscribeState(
    channel: WebSocketChannel,
    onStateChange: StateHandler,
  ) {
    const channelState = this.getChannelState(channel);

    channelState.stateHandlers.add(onStateChange);

    // Immediately provide current state.
    onStateChange(channelState.state);

    return () => {
      channelState.stateHandlers.delete(onStateChange);
    };
  }
}

export const wsManager = new WebSocketManager();
