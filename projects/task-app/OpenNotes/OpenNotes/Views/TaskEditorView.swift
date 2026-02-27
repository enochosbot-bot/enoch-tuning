import SwiftUI

struct TaskEditorView: View {
    let task: TaskItem?
    let onSave: (String, String) -> Void
    let onCancel: () -> Void
    
    @State private var taskText: String
    @State private var noteText: String
    @State private var newSubtaskText = ""
    @State private var subtasks: [SubTask] = []
    
    @FocusState private var isTaskTextFocused: Bool
    @FocusState private var isNoteTextFocused: Bool
    @FocusState private var isSubtaskFieldFocused: Bool
    
    @Environment(\.dismiss) private var dismiss
    
    init(task: TaskItem?, onSave: @escaping (String, String) -> Void, onCancel: @escaping () -> Void) {
        self.task = task
        self.onSave = onSave
        self.onCancel = onCancel
        
        // Initialize state
        _taskText = State(initialValue: task?.text ?? "")
        _noteText = State(initialValue: task?.note ?? "")
        _subtasks = State(initialValue: task?.subtasks ?? [])
    }
    
    private var isNewTask: Bool {
        task == nil
    }
    
    private var canSave: Bool {
        !taskText.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }
    
    var body: some View {
        NavigationView {
            ZStack {
                Theme.primaryBackground.ignoresSafeArea()
                
                ScrollView {
                    VStack(spacing: Theme.spacing20) {
                        // Task text input
                        taskTextSection
                        
                        // Note input
                        noteSection
                        
                        // Subtasks section (only for existing tasks)
                        if !isNewTask {
                            subtasksSection
                        }
                    }
                    .padding(.horizontal, Theme.spacing16)
                    .padding(.top, Theme.spacing20)
                }
            }
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Cancel") {
                        handleCancel()
                    }
                    .foregroundColor(Theme.secondaryText)
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button("Save") {
                        handleSave()
                    }
                    .foregroundColor(canSave ? Theme.accentBlue : Theme.tertiaryText)
                    .disabled(!canSave)
                }
                
                // Keyboard toolbar
                ToolbarItemGroup(placement: .keyboard) {
                    keyboardToolbar
                }
            }
            .onAppear {
                if isNewTask {
                    isTaskTextFocused = true
                }
            }
        }
    }
    
    // MARK: - Task Text Section
    
    private var taskTextSection: some View {
        VStack(alignment: .leading, spacing: Theme.spacing8) {
            Text(isNewTask ? "New Task" : "Edit Task")
                .font(Theme.title)
                .foregroundColor(Theme.primaryText)
            
            TextField("What needs to be done?", text: $taskText, axis: .vertical)
                .font(Theme.body)
                .textFieldStyle(PlainTextFieldStyle())
                .focused($isTaskTextFocused)
                .padding(.vertical, Theme.spacing12)
                .padding(.horizontal, Theme.spacing16)
                .background(
                    RoundedRectangle(cornerRadius: Theme.cornerRadiusMedium)
                        .fill(Theme.secondaryBackground)
                        .stroke(isTaskTextFocused ? Theme.accentBlue : Theme.border, lineWidth: 1)
                )
        }
    }
    
    // MARK: - Note Section
    
    private var noteSection: some View {
        VStack(alignment: .leading, spacing: Theme.spacing8) {
            HStack {
                Image(systemName: "note.text")
                    .font(.caption)
                    .foregroundColor(Theme.tertiaryText)
                Text("Add Note")
                    .font(Theme.callout)
                    .foregroundColor(Theme.primaryText)
                Spacer()
            }
            
            TextField("Optional details...", text: $noteText, axis: .vertical)
                .font(Theme.callout)
                .textFieldStyle(PlainTextFieldStyle())
                .focused($isNoteTextFocused)
                .padding(.vertical, Theme.spacing12)
                .padding(.horizontal, Theme.spacing16)
                .frame(minHeight: 80)
                .background(
                    RoundedRectangle(cornerRadius: Theme.cornerRadiusMedium)
                        .fill(Theme.secondaryBackground)
                        .stroke(isNoteTextFocused ? Theme.accentBlue : Theme.border, lineWidth: 1)
                )
        }
    }
    
    // MARK: - Subtasks Section
    
    private var subtasksSection: some View {
        VStack(alignment: .leading, spacing: Theme.spacing12) {
            HStack {
                Image(systemName: "checkmark.square")
                    .font(.caption)
                    .foregroundColor(Theme.tertiaryText)
                Text("Subtasks")
                    .font(Theme.callout)
                    .foregroundColor(Theme.primaryText)
                Spacer()
            }
            
            // Existing subtasks
            ForEach(subtasks, id: \.id) { subtask in
                subtaskRow(subtask)
            }
            
            // Add new subtask field
            HStack(spacing: Theme.spacing12) {
                Image(systemName: "plus.circle")
                    .font(.title3)
                    .foregroundColor(Theme.accentBlue)
                
                TextField("Add subtask", text: $newSubtaskText)
                    .font(Theme.callout)
                    .textFieldStyle(PlainTextFieldStyle())
                    .focused($isSubtaskFieldFocused)
                    .onSubmit {
                        addSubtask()
                    }
                
                if !newSubtaskText.isEmpty {
                    Button(action: addSubtask) {
                        Image(systemName: "checkmark.circle.fill")
                            .font(.title3)
                            .foregroundColor(Theme.accentBlue)
                    }
                }
            }
            .padding(.vertical, Theme.spacing8)
            .padding(.horizontal, Theme.spacing16)
            .background(
                RoundedRectangle(cornerRadius: Theme.cornerRadiusMedium)
                    .fill(Theme.secondaryBackground)
                    .stroke(isSubtaskFieldFocused ? Theme.accentBlue : Theme.border, lineWidth: 1)
            )
        }
    }
    
    private func subtaskRow(_ subtask: SubTask) -> some View {
        HStack(spacing: Theme.spacing12) {
            Button(action: { toggleSubtask(subtask) }) {
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
            
            Text(subtask.text)
                .font(Theme.callout)
                .foregroundColor(subtask.isCompleted ? Theme.completedTaskText : Theme.primaryText)
                .strikethrough(subtask.isCompleted)
            
            Spacer()
            
            Button(action: { removeSubtask(subtask) }) {
                Image(systemName: "minus.circle.fill")
                    .font(.caption)
                    .foregroundColor(.red.opacity(0.7))
            }
        }
        .padding(.vertical, Theme.spacing8)
        .padding(.horizontal, Theme.spacing16)
        .background(
            RoundedRectangle(cornerRadius: Theme.cornerRadiusMedium)
                .fill(Theme.secondaryBackground)
        )
    }
    
    // MARK: - Keyboard Toolbar
    
    private var keyboardToolbar: some View {
        HStack {
            // Quick action buttons
            Button(action: { /* TODO: Reminder */ }) {
                VStack(spacing: 2) {
                    Image(systemName: "bell")
                        .font(.title3)
                    Text("Remind")
                        .font(.caption2)
                }
                .foregroundColor(Theme.tertiaryText)
            }
            
            Button(action: { /* TODO: Star */ }) {
                VStack(spacing: 2) {
                    Image(systemName: "star")
                        .font(.title3)
                    Text("Star")
                        .font(.caption2)
                }
                .foregroundColor(Theme.tertiaryText)
            }
            
            Button(action: { /* TODO: Repeat */ }) {
                VStack(spacing: 2) {
                    Image(systemName: "repeat")
                        .font(.title3)
                    Text("Repeat")
                        .font(.caption2)
                }
                .foregroundColor(Theme.tertiaryText)
            }
            
            Button(action: { /* TODO: Focus */ }) {
                VStack(spacing: 2) {
                    Image(systemName: "timer")
                        .font(.title3)
                    Text("Focus")
                        .font(.caption2)
                }
                .foregroundColor(Theme.focusRed)
            }
            
            Button(action: { /* TODO: Notification */ }) {
                VStack(spacing: 2) {
                    Image(systemName: "app.badge")
                        .font(.title3)
                    Text("Notify")
                        .font(.caption2)
                }
                .foregroundColor(Theme.tertiaryText)
            }
            
            Spacer()
            
            // Save button (blue checkmark)
            Button(action: handleSave) {
                VStack(spacing: 2) {
                    Image(systemName: "checkmark.circle.fill")
                        .font(.title2)
                    Text("Save")
                        .font(.caption2)
                }
                .foregroundColor(canSave ? Theme.accentBlue : Theme.tertiaryText)
            }
            .disabled(!canSave)
        }
        .padding(.horizontal, Theme.spacing16)
    }
    
    // MARK: - Actions
    
    private func handleSave() {
        let trimmedTaskText = taskText.trimmingCharacters(in: .whitespacesAndNewlines)
        let trimmedNoteText = noteText.trimmingCharacters(in: .whitespacesAndNewlines)
        
        guard !trimmedTaskText.isEmpty else { return }
        
        onSave(trimmedTaskText, trimmedNoteText)
        dismiss()
        HapticManager.shared.successFeedback()
    }
    
    private func handleCancel() {
        onCancel()
        dismiss()
    }
    
    private func addSubtask() {
        let trimmedText = newSubtaskText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmedText.isEmpty else { return }
        
        let newSubtask = SubTask(text: trimmedText)
        subtasks.append(newSubtask)
        newSubtaskText = ""
        
        HapticManager.shared.lightImpact()
        
        // Maintain focus for adding more subtasks
        DispatchQueue.main.asyncAfter(deadline: .now() + 0.1) {
            isSubtaskFieldFocused = true
        }
    }
    
    private func toggleSubtask(_ subtask: SubTask) {
        subtask.toggle()
        HapticManager.shared.lightImpact()
    }
    
    private func removeSubtask(_ subtask: SubTask) {
        subtasks.removeAll { $0.id == subtask.id }
        HapticManager.shared.lightImpact()
    }
}

#Preview {
    TaskEditorView(
        task: nil,
        onSave: { text, note in
            print("Save: \(text), \(note)")
        },
        onCancel: {
            print("Cancel")
        }
    )
}