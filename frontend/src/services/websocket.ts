/**
 * Real-time WebSocket connection and event dispatcher service.
 */

type MessageHandler = (data: any) => void

class WebSocketService {
  private ws: WebSocket | null = null
  private handlers: Map<string, Set<MessageHandler>> = new Map()
  private reconnectTimeout: ReturnType<typeof setTimeout> | null = null
  private pingInterval: ReturnType<typeof setInterval> | null = null
  private retryDelay: number = 2000
  private maxRetryDelay: number = 30000
  private isExplicitlyClosed: boolean = false

  public connect(): void {
    if (this.ws && (this.ws.readyState === WebSocket.OPEN || this.ws.readyState === WebSocket.CONNECTING)) {
      return
    }

    this.isExplicitlyClosed = false
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host || 'localhost:8080'
    const wsUrl = `${protocol}//${host}/ws/dashboard`

    try {
      this.ws = new WebSocket(wsUrl)

      this.ws.onopen = () => {
        this.retryDelay = 2000
        this.startHeartbeat()
        this.emit('connection_status', { status: 'connected' })
      }

      this.ws.onmessage = (event: MessageEvent) => {
        try {
          const parsed = JSON.parse(event.data)
          if (parsed && parsed.type) {
            this.emit(parsed.type, parsed.data)
          }
        } catch {
          // Non-JSON message ignore
        }
      }

      this.ws.onclose = () => {
        this.stopHeartbeat()
        this.emit('connection_status', { status: 'disconnected' })
        if (!this.isExplicitlyClosed) {
          this.scheduleReconnect()
        }
      }

      this.ws.onerror = () => {
        if (this.ws) {
          this.ws.close()
        }
      }
    } catch {
      this.scheduleReconnect()
    }
  }

  public disconnect(): void {
    this.isExplicitlyClosed = true
    this.stopHeartbeat()
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout)
      this.reconnectTimeout = null
    }
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  public on(eventType: string, handler: MessageHandler): () => void {
    if (!this.handlers.has(eventType)) {
      this.handlers.set(eventType, new Set())
    }
    this.handlers.get(eventType)!.add(handler)

    return () => {
      this.handlers.get(eventType)?.delete(handler)
    }
  }

  public emit(eventType: string, data: any): void {
    const listeners = this.handlers.get(eventType)
    if (listeners) {
      listeners.forEach((fn) => fn(data))
    }
  }

  public send(type: string, data: any = {}): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, ...data }))
    }
  }

  private startHeartbeat(): void {
    this.stopHeartbeat()
    this.pingInterval = setInterval(() => {
      this.send('ping')
    }, 25000)
  }

  private stopHeartbeat(): void {
    if (this.pingInterval) {
      clearInterval(this.pingInterval)
      this.pingInterval = null
    }
  }

  private scheduleReconnect(): void {
    if (this.reconnectTimeout) return
    this.reconnectTimeout = setTimeout(() => {
      this.reconnectTimeout = null
      this.retryDelay = Math.min(this.retryDelay * 1.5, this.maxRetryDelay)
      this.connect()
    }, this.retryDelay)
  }
}

export const wsService = new WebSocketService()
