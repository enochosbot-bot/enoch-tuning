import SwiftUI

struct TaskExpandedView: View {
    let task: TaskItem
    let onAddSubtask: (String) -> Void
    let onToggleSubtask: (SubTask) -> Void
    let onDeleteSubtask: (SubTask) -> Void
    let onEdit: () -> Void
    let onDelete: () -> Void
    let onFocus: () -> Void
    let onDone: () -> Void
    
    @State private var newSubtaskText = ""
    @State private var showingNewSubtaskField = false
    @FocusState private var isSubtaskFieldFocused: Bool
    
    var body: some View {
        VStack(spacing: 0) {
            // Task note section
            if task.hasNote {
                noteSection
                    .padding(.horizontal, Theme.spacing16)
                    .padding(.top, Theme.spacing12)
            }
            
            // Subtasks section
            subtasksSection
                .padding(.horizontal, Theme.spacing16)
            
            // Add subtask section
            addSubtaskSection
                .padding(.horizontal, Theme.spacing16)
                .padding(.bottom, Theme.spacing12)
            
            // Bottom toolbar
            bottomToolbar
        }
        .background(Theme.tertiaryBackground)
        .onAppear {
            // Auto-focus subtask field if showing
            if showingNewSubtaskField {
                isSubtaskFieldFocused = true
            }
        }
    }
    
    // MARK: - Note Section
    
    private var noteSection: some View {
        VStack(alignment: .leading, spacing: Theme.spacing8) {
            HStack {
                Image(systemName: "note.text")
                    .font(.caption)
                    .foregroundColor(Theme.tertiaryText)
                Text("Note")
                    .font(Theme.caption)
                    .foregroundColor(Theme.tertiaryText)
                Spacer()
            }
            
            Text(task.note)
                .font(Theme.callout)
                .foregroundColor(Theme.primaryText)
                .multilineTextAlignment(.leading)
        }
    }
    
    // MARK: - Subtasks Section
    
    private var subtasksSection: some View {
        VStack(spacing: Theme.spacing4) {
            if task.hasSubtasks {
                ForEach(task.subtasks, id: \.id) { subtask in
                    subtaskRow(subtask)
                }
            }
        }
        .padding(.top, task.hasNote ? Theme.spacing16 : Theme.spacing12)
    }
    
    private func subtaskRow(_ subtask: SubTask) -> some View {
        HStack(spacing: Theme.spacing12) {
            // Completion checkbox
            Button(action: { onToggleSubtask(subtask) }) {
                ZStack {
                    RoundedRectangle(cornerRadius: 4)
                        .stroke(Theme.accentBlue, lineWidth: 2)
                        .frame(width: 18, height: 18)
                    
                    if subtask.isCompleted {
                        Image(systemName: "checkmark")
                            .font(.caption2.weight(.bold))
                            .foregroundColor(Theme.accentBlue)
                    }
                }
            }
            .buttonStyle(PlainButtonStyle())
            
            // Subtask text
            Text(subtask.text)
                .font(Theme.subtaskText)
                .foregroundColor(subtask.isCompleted ? Theme.completedTaskText : Theme.primaryText)
                .strikethrough(subtask.isCompleted)
            
            Spacer()
            
            // Delete button
            Button(action: { onDeleteSubtask(subtask) }) {
                Image(systemName: "minus.circle.fill")
                    .font(.caption)
                    .foregroundColor(.red.opacity(0.7))
            }
            .buttonStyle(PlainButtonStyle())
        }
        .padding(.vertical, Theme.spacing4)
    }
    
    // MARK: - Add Subtask Section
    
    private var addSubtaskSection: some View {
        VStack(spacing: Theme.spacing8) {
            // Add subtask button or field
            if showingNewSubtaskField {
                HStack(spacing: Theme.spacing12) {
                    Button(action: { 
                        withAnimation(Theme.quickAnimation) {
                            showingNewSubtaskField = false
                            newSubtaskText = ""
                        }
                    }) {
                        Image(systemName: "minus.circle.fill")
                            .font(.title3)
                            .foregroundColor(.red.opacity(0.7))
                    }
                    .buttonStyle(PlainButtonStyle())
                    
                    TextField("Add subtask", text: $newSubtaskText)
                        .font(Theme.subtaskText)
                        .textFieldStyle(PlainTextFieldStyle())
                        .focused($isSubtaskFieldFocused)
                        .onSubmit {
                            addSubtask()
                        }
                    
                    Button(action: addSubtask) {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.title3)
                            .foregroundColor(Theme.accentBlue)
                    }
                    .buttonStyle(PlainButtonStyle())
                    .disabled(newSubtaskText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty)
                }
                .padding(.vertical, Theme.spacing8)
                .padding(.horizontal, Theme.spacing12)
                .background(
                    RoundedRectangle(cornerRadius: Theme.cornerRadiusSmall)
                        .fill(Theme.primaryBackground)
                        .stroke(Theme.border, lineWidth: 1)
                )
            } else {
                Button(action: {
                    withAnimation(Theme.quickAnimation) {
                        showingNewSubtaskField = true
                        isSubtaskFieldFocused = true
                    }
                }) {
                    HStack(spacing: Theme.spacing8) {
                        Image(systemName: "plus.circle")
                            .font(.title3)
                            .foregroundColor(Theme.accentBlue)
                        
                        Text("Add subtask")
                            .font(Theme.callout)
                            .foregroundColor(Theme.accentBlue)
                        
                        Spacer()
                    }
                    .padding(.vertical, Theme.spacing8)
                }
                .buttonStyle(PlainButtonStyle())
            }
        }
    }
    
    // MARK: - Bottom Toolbar
    
    private var bottomToolbar: some View {
        HStack(spacing: 0) {
            toolbarButton(
                icon: "trash",
                title: "Delete",
                color: .red,
                action: onDelete
            )
            
            Divider()
                .frame(height: 40)
            
            toolbarButton(
                icon: "pencil",
                title: "Edit",
                color: Theme.accentBlue,
                action: onEdit
            )
            
            Divider()
                .frame(height: 40)
            
            toolbarButton(
                icon: "timer",
                title: "Focus",
                color: Theme.focusRed,
                action: onFocus
            )
            
            Divider()
                .frame(height: 40)
            
            toolbarButton(
                icon: task.isCompleted ? "arrow.counterclockwise" : "checkmark",
                title: task.isCompleted ? "Undo" : "Done",
                color: Theme.accentBlue,
                action: onDone
            )
        }
        .background(
            Rectangle()
                .fill(Theme.primaryBackground)
                .shadow(color: .black.opacity(0.1), radius: 1, x: 0, y: -1)
        )
    }
    
    private func toolbarButton(icon: String, title: String, color: Color, action: @escaping () -> Void) -> some View {
        Button(action: action) {
            VStack(spacing: Theme.spacing4) {
                Image(systemName: icon)
                    .font(.title3)
                    .foregroundColor(color)
                
                Text(title)
                    .font(.caption2)
                    .foregroundColor(color)
            }
            .frame(maxWidth: .infinity)
            .padding(.vertical, Theme.spacing12)
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    // MARK: - Actions
    
    private func addSubtask() {
        let trimmedText = newSubtaskText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedText.isEmpty else { return }
        
        onAddSubtask(trimmedText)
        
        newSubtaskText = ""
        
        // Keep focus for adding more subtasks
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            isSubtaskFieldFocused = true
        }
        
        HapticManager.shared.lightImpact()
    }
}

#Preview {
    let sampleTask = TaskItem(
        text: "Sample task with details",
        note: "This is a detailed note about the task that explains what needs to be done and why it's important.",
        focusedSeconds: 3665
    )
    
    sampleTask.subtasks = [
        SubTask(text: "First subtask", parentTask: sampleTask),
        SubTask(text: "Completed subtask", isCompleted: true, parentTask: sampleTask),
        SubTask(text: "Another subtask", parentTask: sampleTask)
    ]
    
    return TaskExpandedView(
        task: sampleTask,
        onAddSubtask: { _ in },
        onToggleSubtask: { _ in },
        onDeleteSubtask: { _ in },
        onEdit: { },
        onDelete: { },
        onFocus: { },
        onDone: { }
    )
    .padding()
    .background(Color(.systemGroupedBackground))
}