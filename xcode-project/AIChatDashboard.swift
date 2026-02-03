// AIChatDashboard.swift
// A SwiftUI dashboard for visualizing dialog between Copilot and your AI, plus user/AI chat, health indicators, and functional tools.
// This is a scaffold for a multi-pane AI dashboard app.

import SwiftUI

struct AIChatDashboard: View {
    @State private var userMessage: String = ""
    @State private var aiMessage: String = ""
    @State private var copilotMessage: String = ""
    @State private var chatLog: [String] = []
    @State private var aiHealth: Bool = true
    @State private var copilotHealth: Bool = true
    @State private var backendHealth: Bool = true

    var body: some View {
        HStack(spacing: 0) {
            // Copilot <-> AI dialog window
            VStack(alignment: .leading) {
                Text("Copilot ↔︎ AI Dialog")
                    .font(.headline)
                ScrollView {
                    Text(copilotMessage)
                        .frame(maxWidth: .infinity, alignment: .leading)
                        .padding()
                }
                .background(Color(.systemGray6))
                .cornerRadius(8)
                Spacer()
            }
            .frame(width: 300)
            .padding()
            Divider()
            // User <-> AI chat window
            VStack(alignment: .leading) {
                Text("You ↔︎ AI Chat")
                    .font(.headline)
                ScrollView {
                    ForEach(chatLog, id: \ .self) { msg in
                        Text(msg)
                            .frame(maxWidth: .infinity, alignment: .leading)
                            .padding(.vertical, 2)
                    }
                }
                .background(Color(.systemGray6))
                .cornerRadius(8)
                HStack {
                    TextField("Type your message...", text: $userMessage)
                        .textFieldStyle(RoundedBorderTextFieldStyle())
                    Button("Send") {
                        sendUserMessage()
                    }
                    .buttonStyle(.borderedProminent)
                }
            }
            .frame(width: 350)
            .padding()
            Divider()
            // Health indicators and tools
            VStack(alignment: .leading, spacing: 16) {
                Text("System Health")
                    .font(.headline)
                HStack {
                    healthLight(isHealthy: aiHealth, label: "AI")
                    healthLight(isHealthy: copilotHealth, label: "Copilot")
                    healthLight(isHealthy: backendHealth, label: "Backend")
                }
                Divider()
                Text("Tools & Actions")
                    .font(.headline)
                Button("Restart AI") { /* restart logic */ }
                Button("Export Chat Log") { /* export logic */ }
                Button("Inject Memory") { /* inject logic */ }
                Spacer()
            }
            .frame(width: 200)
            .padding()
        }
        .frame(minWidth: 900, minHeight: 500)
    }

    func sendUserMessage() {
        guard !userMessage.isEmpty else { return }
        chatLog.append("You: " + userMessage)
        // Simulate AI reply
        let aiReply = "AI: (simulated reply to) " + userMessage
        chatLog.append(aiReply)
        userMessage = ""
    }

    func healthLight(isHealthy: Bool, label: String) -> some View {
        HStack {
            Circle()
                .fill(isHealthy ? Color.green : Color.red)
                .frame(width: 16, height: 16)
            Text(label)
                .font(.subheadline)
        }
    }
}

struct AIChatDashboard_Previews: PreviewProvider {
    static var previews: some View {
        AIChatDashboard()
    }
}
