import SwiftUI

struct FocusTimerView: View {
    let task: TaskItem
    @ObservedObject var viewModel: FocusTimerViewModel
    let onComplete: (Int) -> Void
    
    @Environment(\.dismiss) private var dismiss
    @State private var showingStopConfirmation = false
    
    var body: some View {
        ZStack {
            // Red background
            Theme.focusRed
                .ignoresSafeArea()
            
            VStack(spacing: Theme.spacing48) {
                Spacer()
                
                // Task name
                VStack(spacing: Theme.spacing16) {
                    Text("Focusing on")
                        .font(Theme.callout)
                        .foregroundColor(.white.opacity(0.8))
                    
                    Text(task.text)
                        .font(Theme.headline)
                        .foregroundColor(.white)
                        .multilineTextAlignment(.center)
                        .lineLimit(3)
                        .padding(.horizontal, Theme.spacing32)
                }
                
                // Timer display
                timerDisplay
                
                Spacer()
                
                // Control buttons
                VStack(spacing: Theme.spacing24) {
                    if viewModel.isRunning {
                        // Pause button
                        Button(action: {
                            viewModel.pauseTimer()
                        }) {
                            HStack(spacing: Theme.spacing12) {
                                Image(systemName: "pause.fill")
                                    .font(.title2)
                                Text("Pause")
                                    .font(Theme.headline)
                            }
                            .foregroundColor(Theme.focusRed)
                            .padding(.horizontal, Theme.spacing32)
                            .padding(.vertical, Theme.spacing16)
                            .background(
                                RoundedRectangle(cornerRadius: Theme.cornerRadiusLarge)
                                    .fill(.white)
                            )
                        }
                        .buttonStyle(PlainButtonStyle())
                    } else if viewModel.elapsedTime > 0 {
                        // Resume button
                        Button(action: {
                            viewModel.resumeTimer()
                        }) {
                            HStack(spacing: Theme.spacing12) {
                                Image(systemName: "play.fill")
                                    .font(.title2)
                                Text("Resume")
                                    .font(Theme.headline)
                            }
                            .foregroundColor(Theme.focusRed)
                            .padding(.horizontal, Theme.spacing32)
                            .padding(.vertical, Theme.spacing16)
                            .background(
                                RoundedRectangle(cornerRadius: Theme.cornerRadiusLarge)
                                    .fill(.white)
                            )
                        }
                        .buttonStyle(PlainButtonStyle())
                    }
                    
                    // Stop recording button
                    Button(action: {
                        showingStopConfirmation = true
                    }) {
                        HStack(spacing: Theme.spacing12) {
                            Image(systemName: "stop.fill")
                                .font(.title2)
                            Text("Stop Recording")
                                .font(Theme.headline)
                        }
                        .foregroundColor(.white)
                        .padding(.horizontal, Theme.spacing32)
                        .padding(.vertical, Theme.spacing16)
                        .background(
                            RoundedRectangle(cornerRadius: Theme.cornerRadiusLarge)
                                .stroke(.white, lineWidth: 2)
                        )
                    }
                    .buttonStyle(PlainButtonStyle())
                }
                
                Spacer()
            }
        }
        .preferredColorScheme(.dark)
        .onAppear {
            // Start the timer automatically
            if !viewModel.isRunning && viewModel.elapsedTime == 0 {
                viewModel.startTimer(for: task)
            }
        }
        .alert("Stop Focus Session", isPresented: $showingStopConfirmation) {
            Button("Cancel", role: .cancel) { }
            Button("Stop", role: .destructive) {
                stopTimer()
            }
        } message: {
            Text("Are you sure you want to stop the focus session?")
        }
        .gesture(
            // Swipe down to dismiss (alternative to stop button)
            DragGesture()
                .onEnded { value in
                    if value.translation.y > 100 && abs(value.translation.x) < 100 {
                        showingStopConfirmation = true
                    }
                }
        )
    }
    
    // MARK: - Timer Display
    
    private var timerDisplay: some View {
        VStack(spacing: Theme.spacing16) {
            // Main time display
            HStack(spacing: Theme.spacing8) {
                let (hours, minutes, seconds) = viewModel.hoursMinutesSeconds
                
                if Int(viewModel.elapsedTime) >= 3600 {
                    // Show hours when >= 1 hour
                    Group {
                        Text(hours)
                        Text(":")
                        Text(minutes)
                        Text(":")
                        Text(seconds)
                    }
                    .font(Theme.timerDisplay)
                    .foregroundColor(.white)
                    .monospacedDigit()
                } else {
                    // Show only minutes and seconds
                    Group {
                        Text(minutes)
                        Text(":")
                        Text(seconds)
                    }
                    .font(Theme.timerDisplay)
                    .foregroundColor(.white)
                    .monospacedDigit()
                }
            }
            
            // Status indicator
            HStack(spacing: Theme.spacing8) {
                Circle()
                    .fill(viewModel.isRunning ? .white : .white.opacity(0.5))
                    .frame(width: 12, height: 12)
                    .scaleEffect(viewModel.isRunning ? 1.2 : 1.0)
                    .animation(.easeInOut(duration: 1.0).repeatForever(autoreverses: true), value: viewModel.isRunning)
                
                Text(viewModel.isRunning ? "Recording..." : "Paused")
                    .font(Theme.callout)
                    .foregroundColor(.white.opacity(0.8))
            }
        }
    }
    
    // MARK: - Actions
    
    private func stopTimer() {
        let focusedSeconds = viewModel.stopTimer()
        onComplete(focusedSeconds)
        dismiss()
    }
}

#Preview {
    FocusTimerView(
        task: TaskItem(text: "Work on important project presentation"),
        viewModel: FocusTimerViewModel(),
        onComplete: { seconds in
            print("Completed with \(seconds) seconds")
        }
    )
}