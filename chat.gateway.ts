// ...existing imports...

export class ChatGateway {
  // Temporarily removed decorators to isolate issues
  handleMessage(message: string): string {
    return `Received: ${message}`;
  }
}