import SwiftUI

struct Theme {
    // MARK: - Colors
    
    // Primary Colors
    static let accentBlue = Color("AccentColor")
    static let primaryText = Color.primary
    static let secondaryText = Color.secondary
    static let tertiaryText = Color(.tertiaryLabel)
    
    // Background Colors
    static let primaryBackground = Color(.systemBackground)
    static let secondaryBackground = Color(.secondarySystemBackground)
    static let tertiaryBackground = Color(.tertiarySystemBackground)
    static let groupedBackground = Color(.systemGroupedBackground)
    
    // Task Colors
    static let taskBackground = Color(.systemBackground)
    static let completedTaskText = Color.secondary
    static let deletedTaskBackground = Color.red.opacity(0.1)
    
    // Focus Timer Colors
    static let focusRed = Color.red
    static let focusBackground = Color.red.opacity(0.05)
    
    // Border Colors
    static let border = Color(.separator)
    static let lightBorder = Color(.separator).opacity(0.5)
    
    // MARK: - Typography
    
    static let largeTitle = Font.largeTitle.weight(.bold)
    static let title = Font.title2.weight(.semibold)
    static let headline = Font.headline
    static let body = Font.body
    static let callout = Font.callout
    static let caption = Font.caption
    static let caption2 = Font.caption2
    
    // Task specific fonts
    static let taskText = Font.body
    static let taskNote = Font.caption
    static let subtaskText = Font.callout
    
    // Focus timer fonts
    static let timerDisplay = Font.system(size: 64, weight: .light, design: .monospaced)
    static let timerSeconds = Font.system(size: 48, weight: .light, design: .monospaced)
    
    // MARK: - Spacing
    
    static let spacing2: CGFloat = 2
    static let spacing4: CGFloat = 4
    static let spacing8: CGFloat = 8
    static let spacing12: CGFloat = 12
    static let spacing16: CGFloat = 16
    static let spacing20: CGFloat = 20
    static let spacing24: CGFloat = 24
    static let spacing32: CGFloat = 32
    static let spacing48: CGFloat = 48
    
    // MARK: - Corner Radius
    
    static let cornerRadiusSmall: CGFloat = 8
    static let cornerRadiusMedium: CGFloat = 12
    static let cornerRadiusLarge: CGFloat = 16
    
    // MARK: - Animation
    
    static let quickAnimation = Animation.easeInOut(duration: 0.2)
    static let standardAnimation = Animation.easeInOut(duration: 0.3)
    static let slowAnimation = Animation.easeInOut(duration: 0.5)
    static let springAnimation = Animation.spring(response: 0.4, dampingFraction: 0.8)
    
    // MARK: - Shadow
    
    static let subtleShadow = Shadow(color: .black.opacity(0.05), radius: 2, x: 0, y: 1)
    static let cardShadow = Shadow(color: .black.opacity(0.1), radius: 8, x: 0, y: 2)
}

// MARK: - Shadow Helper

struct Shadow {
    let color: Color
    let radius: CGFloat
    let x: CGFloat
    let y: CGFloat
}

// MARK: - View Extensions

extension View {
    func applyShadow(_ shadow: Shadow) -> some View {
        self.shadow(color: shadow.color, radius: shadow.radius, x: shadow.x, y: shadow.y)
    }
    
    func taskRowStyle() -> some View {
        self
            .padding(.horizontal, Theme.spacing16)
            .padding(.vertical, Theme.spacing12)
            .background(Theme.taskBackground)
    }
    
    func cardStyle() -> some View {
        self
            .background(Theme.secondaryBackground)
            .cornerRadius(Theme.cornerRadiusMedium)
            .applyShadow(Theme.subtleShadow)
    }
}