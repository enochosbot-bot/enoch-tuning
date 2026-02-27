import UIKit

class HapticManager {
    static let shared = HapticManager()
    
    private init() {}
    
    func lightImpact() {
        let generator = UIImpactFeedbackGenerator(style: .light)
        generator.impactOccurred()
    }
    
    func mediumImpact() {
        let generator = UIImpactFeedbackGenerator(style: .medium)
        generator.impactOccurred()
    }
    
    func heavyImpact() {
        let generator = UIImpactFeedbackGenerator(style: .heavy)
        generator.impactOccurred()
    }
    
    func successFeedback() {
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.success)
    }
    
    func errorFeedback() {
        let generator = UINotificationFeedbackGenerator()
        generator.notificationOccurred(.error)
    }
    
    func selectionChanged() {
        let generator = UISelectionFeedbackGenerator()
        generator.selectionChanged()
    }
}

// Convenience extensions
extension HapticManager {
    func taskCompleted() {
        successFeedback()
    }
    
    func taskDeleted() {
        mediumImpact()
    }
    
    func taskSelected() {
        lightImpact()
    }
    
    func swipeProgress() {
        selectionChanged()
    }
}