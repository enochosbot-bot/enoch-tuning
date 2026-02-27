import Foundation
import SwiftUI

@MainActor
class FocusTimerViewModel: ObservableObject {
    @Published var isRunning = false
    @Published var elapsedTime: TimeInterval = 0
    @Published var task: TaskItem?
    
    private var timer: Timer?
    private var startTime: Date?
    
    // MARK: - Timer Control
    
    func startTimer(for task: TaskItem) {
        self.task = task
        self.startTime = Date()
        self.isRunning = true
        self.elapsedTime = 0
        
        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            self?.updateElapsedTime()
        }
        
        HapticManager.shared.lightImpact()
    }
    
    func stopTimer() -> Int {
        timer?.invalidate()
        timer = nil
        isRunning = false
        
        let focusedSeconds = Int(elapsedTime)
        
        // Reset state
        elapsedTime = 0
        startTime = nil
        task = nil
        
        HapticManager.shared.mediumImpact()
        
        return focusedSeconds
    }
    
    func pauseTimer() {
        guard isRunning else { return }
        
        timer?.invalidate()
        timer = nil
        isRunning = false
        
        HapticManager.shared.lightImpact()
    }
    
    func resumeTimer() {
        guard !isRunning, task != nil else { return }
        
        isRunning = true
        startTime = Date().addingTimeInterval(-elapsedTime)
        
        timer = Timer.scheduledTimer(withTimeInterval: 1.0, repeats: true) { [weak self] _ in
            self?.updateElapsedTime()
        }
        
        HapticManager.shared.lightImpact()
    }
    
    // MARK: - Time Formatting
    
    var formattedTime: String {
        let hours = Int(elapsedTime) / 3600
        let minutes = (Int(elapsedTime) % 3600) / 60
        let seconds = Int(elapsedTime) % 60
        
        return String(format: "%02d:%02d:%02d", hours, minutes, seconds)
    }
    
    var hoursMinutesSeconds: (String, String, String) {
        let hours = Int(elapsedTime) / 3600
        let minutes = (Int(elapsedTime) % 3600) / 60
        let seconds = Int(elapsedTime) % 60
        
        return (
            String(format: "%02d", hours),
            String(format: "%02d", minutes),
            String(format: "%02d", seconds)
        )
    }
    
    var displayTime: String {
        let (hours, minutes, seconds) = hoursMinutesSeconds
        
        if Int(elapsedTime) >= 3600 {
            return "\(hours):\(minutes):\(seconds)"
        } else {
            return "\(minutes):\(seconds)"
        }
    }
    
    // MARK: - Private Helpers
    
    private func updateElapsedTime() {
        guard let startTime = startTime else { return }
        elapsedTime = Date().timeIntervalSince(startTime)
    }
    
    deinit {
        timer?.invalidate()
    }
}

// MARK: - Timer State

extension FocusTimerViewModel {
    var canStart: Bool {
        !isRunning && task == nil
    }
    
    var canStop: Bool {
        task != nil
    }
    
    var canPause: Bool {
        isRunning
    }
    
    var canResume: Bool {
        !isRunning && task != nil && elapsedTime > 0
    }
}