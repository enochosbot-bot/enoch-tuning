import SwiftUI

struct TaskRowView: View {
    let task: TaskItem
    let isExpanded: Bool
    let onTap: () -> Void
    let onToggleComplete: () -> Void
    let onDelete: () -> Void
    let onEdit: () -> Void
    let onFocus: () -> Void
    
    @State private var swipeOffset: CGFloat = 0
    @State private var showingActions = false
    
    private let swipeThreshold: CGFloat = 100
    private let actionWidth: CGFloat = 160
    
    var body: some View {
        VStack(spacing: 0) {
            ZStack {
                // Background actions (right swipe - delete/edit)
                HStack {
                    Spacer()
                    
                    if showingActions {
                        actionButtons
                    }
                }
                .frame(width: actionWidth)
                .offset(x: swipeOffset > 0 ? swipeOffset - actionWidth : 0)
                
                // Main task content
                taskContent
                    .background(
                        Rectangle()
                            .fill(task.isCompleted ? Theme.completedTaskText.opacity(0.1) : Theme.taskBackground)
                    )
                    .offset(x: swipeOffset)
                    .gesture(
                        DragGesture()
                            .onChanged { value in
                                handleSwipeChanged(value)
                            }
                            .onEnded { value in
                                handleSwipeEnded(value)
                            }
                    )
            }
            .clipped()
            
            // Divider
            Divider()
                .padding(.leading, Theme.spacing16)
        }
        .animation(Theme.springAnimation, value: swipeOffset)
        .animation(Theme.springAnimation, value: showingActions)
    }
    
    // MARK: - Task Content
    
    private var taskContent: some View {
        HStack(spacing: Theme.spacing12) {
            // Completion indicator
            Button(action: onToggleComplete) {
                ZStack {
                    Circle()
                        .stroke(Theme.accentBlue, lineWidth: 2)
                        .frame(width: 24, height: 24)
                    
                    if task.isCompleted {
                        Image(systemName: "checkmark")
                            .font(.caption.weight(.semibold))
                            .foregroundColor(Theme.accentBlue)
                    }
                }
            }
            .buttonStyle(PlainButtonStyle())
            
            // Task text with progressive strikethrough
            VStack(alignment: .leading, spacing: Theme.spacing4) {
                ZStack(alignment: .leading) {
                    Text(task.text)
                        .font(Theme.taskText)
                        .foregroundColor(task.isCompleted ? Theme.completedTaskText : Theme.primaryText)
                        .multilineTextAlignment(.leading)
                    
                    // Progressive strikethrough overlay
                    if task.isCompleted || abs(swipeOffset) > 20 {
                        progressiveStrikeThroughOverlay
                    }
                }
                
                // Subtask preview
                if task.hasSubtasks {
                    HStack(spacing: Theme.spacing4) {
                        Image(systemName: "checkmark.square")
                            .font(.caption2)
                            .foregroundColor(Theme.tertiaryText)
                        
                        Text("\(task.completedSubtasksCount)/\(task.subtasks.count) subtasks")
                            .font(Theme.caption2)
                            .foregroundColor(Theme.tertiaryText)
                    }
                }
                
                // Note preview
                if task.hasNote {
                    Text(task.note)
                        .font(Theme.taskNote)
                        .foregroundColor(Theme.secondaryText)
                        .lineLimit(2)
                }
            }
            
            Spacer()
            
            // Status indicators
            VStack(spacing: Theme.spacing4) {
                if task.focusedSeconds > 0 {
                    HStack(spacing: Theme.spacing2) {
                        Image(systemName: "timer")
                            .font(.caption2)
                            .foregroundColor(Theme.focusRed)
                        Text(task.formattedFocusTime)
                            .font(Theme.caption2)
                            .foregroundColor(Theme.focusRed)
                    }
                }
                
                if isExpanded {
                    Image(systemName: "chevron.up")
                        .font(.caption)
                        .foregroundColor(Theme.accentBlue)
                }
            }
        }
        .padding(.horizontal, Theme.spacing16)
        .padding(.vertical, Theme.spacing12)
        .contentShape(Rectangle())
        .onTapGesture {
            onTap()
        }
    }
    
    // MARK: - Progressive Strikethrough
    
    private var progressiveStrikeThroughOverlay: some View {
        GeometryReader { geometry in
            let progress = task.isCompleted ? 1.0 : min(abs(swipeOffset) / swipeThreshold, 1.0)
            
            Rectangle()
                .fill(Theme.primaryText.opacity(0.7))
                .frame(width: geometry.size.width * progress, height: 1)
                .position(x: geometry.size.width * progress / 2, y: geometry.size.height / 2)
                .animation(Theme.quickAnimation, value: progress)
        }
    }
    
    // MARK: - Action Buttons
    
    private var actionButtons: some View {
        HStack(spacing: 0) {
            Button(action: onEdit) {
                VStack(spacing: Theme.spacing4) {
                    Image(systemName: "pencil")
                        .font(.title3)
                    Text("Edit")
                        .font(.caption2)
                }
                .foregroundColor(.white)
                .frame(width: 80, height: 60)
                .background(Theme.accentBlue)
            }
            
            Button(action: onDelete) {
                VStack(spacing: Theme.spacing4) {
                    Image(systemName: "trash")
                        .font(.title3)
                    Text("Delete")
                        .font(.caption2)
                }
                .foregroundColor(.white)
                .frame(width: 80, height: 60)
                .background(Color.red)
            }
        }
        .clipShape(RoundedRectangle(cornerRadius: Theme.cornerRadiusSmall))
    }
    
    // MARK: - Swipe Handling
    
    private func handleSwipeChanged(_ value: DragGesture.Value) {
        let translation = value.translation.x
        
        if task.isCompleted {
            // For completed tasks, only allow left-to-right swipe to uncomplete
            if translation > 0 {
                swipeOffset = min(translation, swipeThreshold)
                
                // Provide haptic feedback during swipe
                if abs(translation) > 30 && abs(translation) < 35 {
                    HapticManager.shared.swipeProgress()
                }
            }
        } else {
            // For active tasks
            if translation > 0 {
                // Right swipe - complete task
                swipeOffset = min(translation, swipeThreshold * 1.5)
                
                // Provide haptic feedback during swipe
                if translation > 30 && translation < 35 {
                    HapticManager.shared.swipeProgress()
                }
            } else if translation < -50 {
                // Left swipe - show actions
                swipeOffset = max(translation, -actionWidth)
                showingActions = abs(translation) > 75
                
                if abs(translation) > 75 && abs(translation) < 80 {
                    HapticManager.shared.lightImpact()
                }
            }
        }
    }
    
    private func handleSwipeEnded(_ value: DragGesture.Value) {
        let translation = value.translation.x
        let velocity = value.velocity.x
        
        if task.isCompleted {
            // For completed tasks - uncomplete on sufficient right swipe
            if translation > swipeThreshold * 0.6 || velocity > 500 {
                onToggleComplete()
            }
            
            resetSwipe()
        } else {
            // For active tasks
            if translation > 0 {
                // Right swipe - complete if threshold met
                if translation > swipeThreshold * 0.6 || velocity > 500 {
                    onToggleComplete()
                }
                resetSwipe()
            } else {
                // Left swipe - show/hide actions
                if abs(translation) > actionWidth * 0.5 || abs(velocity) > 500 {
                    showingActions = true
                    swipeOffset = -actionWidth
                } else {
                    resetSwipe()
                }
            }
        }
    }
    
    private func resetSwipe() {
        withAnimation(Theme.springAnimation) {
            swipeOffset = 0
            showingActions = false
        }
    }
}

#Preview {
    VStack {
        TaskRowView(
            task: TaskItem(text: "Sample task with a longer description to see how it wraps", note: "This is a note"),
            isExpanded: false,
            onTap: { },
            onToggleComplete: { },
            onDelete: { },
            onEdit: { },
            onFocus: { }
        )
        
        TaskRowView(
            task: TaskItem(text: "Completed task", isCompleted: true, completedAt: Date()),
            isExpanded: false,
            onTap: { },
            onToggleComplete: { },
            onDelete: { },
            onEdit: { },
            onFocus: { }
        )
    }
    .modelContainer(for: [TaskItem.self, SubTask.self, TaskList.self])
}