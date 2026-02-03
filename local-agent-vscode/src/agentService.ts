import * as fs from 'fs';
import * as path from 'path';

const OUTBOX_PATH = path.join(__dirname, '../ipc/outbox.jsonl');

export class AgentService {
    private listeners: Array<(data: any) => void> = [];

    constructor() {
        this.startListening();
    }

    private startListening() {
        fs.watch(OUTBOX_PATH, (eventType, filename) => {
            if (eventType === 'change') {
                this.readOutbox();
            }
        });
    }

    private readOutbox() {
        fs.readFile(OUTBOX_PATH, 'utf-8', (err, data) => {
            if (err) {
                console.error('Error reading outbox:', err);
                return;
            }

            const lines = data.trim().split('\n');
            const lastLine = lines[lines.length - 1] || '{}'; // Ensure lastLine is always a string

            try {
                const parsed = JSON.parse(lastLine);
                this.notifyListeners(parsed);
            } catch (error: unknown) {
                if (error instanceof Error) {
                    console.error('Error parsing outbox line:', error.message);
                } else {
                    console.error('Error parsing outbox line: Unknown error');
                }
            }
        });
    }

    private notifyListeners(data: any) {
        this.listeners.forEach(listener => listener(data));
    }

    public onNewMessage(callback: (data: any) => void) {
        this.listeners.push(callback);
    }
}

export const agentService = new AgentService();