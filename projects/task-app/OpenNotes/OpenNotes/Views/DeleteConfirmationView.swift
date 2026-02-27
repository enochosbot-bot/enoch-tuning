import SwiftUI

struct DeleteConfirmationView: View {
    let task: TaskItem
    let onConfirm: () -> Void
    let onCancel: () -> Void
    
    @Environment(\.dismiss) private var dismiss
    
    var body: some View {
        VStack(spacing: Theme.spacing24) {
            // Icon
            Image(systemName: "trash.circle.fill")
                .font(.system(size: 64))
                .foregroundColor(.red)
            
            // Title
            Text("Delete Task?")
                .font(Theme.largeTitle)
                .foregroundColor(Theme.primaryText)
            
            // Task preview
            VStack(spacing: Theme.spacing8) {
                Text("Are you sure you want to remove:")
                    .font(Theme.callout)
                    .foregroundColor(Theme.secondaryText)
                    .multilineTextAlignment(.center)
                
                Text(task.text)
                    .font(Theme.headline)
                    .foregroundColor(Theme.primaryText)
                    .multilineTextAlignment(.center)
                    .lineLimit(3)
                    .padding(.horizontal, Theme.spacing16)
                    .padding(.vertical, Theme.spacing12)
                    .background(
                        RoundedRectangle(cornerRadius: Theme.cornerRadiusMedium)
                            .fill(Theme.tertiaryBackground)
                    )
            }
            
            // Warning message
            VStack(spacing: Theme.spacing8) {
                Text("This action cannot be undone.")
                    .font(Theme.callout)
                    .foregroundColor(.red)
                    .multilineTextAlignment(.center)
                
                if task.hasSubtasks {
                    Text("All \(task.subtasks.count) subtasks will also be deleted.")
                        .font(Theme.caption)
                        .foregroundColor(Theme.secondaryText)
                        .multilineTextAlignment(.center)
                }
                
                if task.focusedSeconds > 0 {
                    Text("Focus time: \(task.formattedFocusTime) will be lost.")
                        .font(Theme.caption)
                        .foregroundColor(Theme.secondaryText)
                        .multilineTextAlignment(.center)
                }
            }
            .padding(.horizontal, Theme.spacing16)
            
            Spacer()
            
            // Action buttons
            VStack(spacing: Theme.spacing12) {
                // Confirm delete button
                Button(action: {
                    onConfirm()
                    dismiss()
                    HapticManager.shared.errorFeedback()
                }) {
                    HStack {
                        Image(systemName: "trash")
                            .font(.headline)
                        Text("Delete Task")
                            .font(Theme.headline)
                    }
                    .foregroundColor(.white)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, Theme.spacing16)
                    .background(
                        RoundedRectangle(cornerRadius: Theme.cornerRadiusMedium)
                            .fill(.red)
                    )
                }
                .buttonStyle(PlainButtonStyle())
                
                // Cancel button
                Button(action: {
                    onCancel()
                    dismiss()
                }) {
                    HStack {
                        Text("Cancel")
                            .font(Theme.headline)
                    }
                    .foregroundColor(Theme.accentBlue)
                    .frame(maxWidth: .infinity)
                    .padding(.vertical, Theme.spacing16)
                    .background(
                        RoundedRectangle(cornerRadius: Theme.cornerRadiusMedium)
                            .fill(Theme.tertiaryBackground)
                    )
                }
                .buttonStyle(PlainButtonStyle())
            }
        }
        .padding(.horizontal, Theme.spacing24)
        .padding(.vertical, Theme.spacing32)
        .background(Theme.primaryBackground)
        .cornerRadius(Theme.cornerRadiusLarge)
        .padding(.horizontal, Theme.spacing16)
        .background(Color.black.opacity(0.3))
        .onTapGesture {
            // Dismiss on background tap
            onCancel()
            dismiss()
        }
    }
}

#Preview {
    ZStack {
        Color.gray.opacity(0.2)
            .ignoresSafeArea()
        
        DeleteConfirmationView(
            task: TaskItem(
                text: "Sample task with a longer title that might wrap to multiple lines",
                note: "This task has a note",
                focusedSeconds: 3600
            ),
            onConfirm: {
                print("Task deleted")
            },
            onCancel: {
                print("Delete cancelled")
            }
        )
    }
}