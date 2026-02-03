import * as vscode from 'vscode';
import { agentService } from './agentService';
import * as fs from 'fs';
import * as path from 'path';

const OUTBOX_PATH = path.join(__dirname, '../../ipc/outbox.jsonl');
let lastReadPosition = 0;
const POLL_INTERVAL = 1000; // Define POLL_INTERVAL

function pollOutbox() {
    try {
        const stats = fs.statSync(OUTBOX_PATH);
        if (stats.size > lastReadPosition) {
            const fileDescriptor = fs.openSync(OUTBOX_PATH, 'r');
            const buffer = Buffer.alloc(stats.size - lastReadPosition);
            fs.readSync(fileDescriptor, buffer, 0, buffer.length, lastReadPosition);
            fs.closeSync(fileDescriptor);

            const newContent = buffer.toString('utf-8');
            const lines = newContent.split('\n').filter(line => line.trim());
            lines.forEach(line => {
                try {
                    const message = JSON.parse(line);
                    // Process the message
                } catch (jsonError: unknown) {
                    if (jsonError instanceof Error) {
                        console.error(`Failed to parse JSON: ${jsonError.message}`);
                    } else {
                        console.error('Failed to parse JSON: Unknown error');
                    }
                }
            });
            lastReadPosition = stats.size;
        }
    } catch (error: unknown) {
        if (error instanceof Error) {
            console.error(`Error reading outbox.jsonl: ${error.message}`);
        } else {
            console.error('Error reading outbox.jsonl: Unknown error');
        }
    }
}

setInterval(pollOutbox, POLL_INTERVAL);

export class WebviewPanel {
    private panel: vscode.WebviewPanel;
    private pollInterval: NodeJS.Timeout;

    constructor(context: vscode.ExtensionContext) {
        this.panel = vscode.window.createWebviewPanel(
            'agentWebview',
            'Agent Output',
            vscode.ViewColumn.One,
            {
                enableScripts: true
            }
        );

        this.panel.webview.html = this.getHtmlContent();

        // Start polling for updates in outbox.jsonl
        this.pollInterval = setInterval(() => {
            this.checkOutboxUpdates();
        }, POLL_INTERVAL);

        this.panel.onDidDispose(() => {
            clearInterval(this.pollInterval);
        });
    }

    private checkOutboxUpdates(): void {
        try {
            const content = fs.readFileSync(OUTBOX_PATH, 'utf-8');
            const lines = content.split('\n').filter(line => line.trim());
            const lastLine = lines[lines.length - 1];
            if (lastLine) {
                const message = JSON.parse(lastLine);
                this.panel.webview.postMessage(message);
            }
        } catch (error: unknown) {
            if (error instanceof Error) {
                console.error(`Error reading outbox.jsonl: ${error.message}`);
            } else {
                console.error('Error reading outbox.jsonl: Unknown error');
            }
        }
    }

    private getHtmlContent(): string {
        return `
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Agent Output</title>
            </head>
            <body>
                <h1>Agent Output</h1>
                <div id="output"></div>
                <script>
                    const vscode = acquireVsCodeApi();

                    window.addEventListener('message', event => {
                        const message = event.data;
                        const outputDiv = document.getElementById('output');
                        const messageElement = document.createElement('div');
                        messageElement.textContent = JSON.stringify(message, null, 2);
                        outputDiv.appendChild(messageElement);
                    });
                </script>
            </body>
            </html>
        `;
    }
}