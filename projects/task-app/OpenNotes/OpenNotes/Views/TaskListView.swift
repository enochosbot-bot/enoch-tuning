import SwiftUI
import SwiftData

struct TaskListView: View {
    @Environment(\.modelContext) private var modelContext
    @StateObject private var viewModel = TaskListViewModel()
    @StateObject private var focusViewModel = FocusTimerViewModel()
    
    @Query(sort: [
        SortDescriptor(\TaskItem.isCompleted),
        SortDescriptor(\TaskItem.sortOrder),
        SortDescriptor(\TaskItem.createdAt, order: .reverse)
    ]) private var allTasks: [TaskItem]
    
    @State private var showingTaskEditor = false
    @State private var showingCompletedArchive = false
    @State private var showingDeleteConfirmation = false
    @State private var taskToDelete: TaskItem?
    @State private var editingTask: TaskItem?
    @State private var showingFocusTimer = false
    @State private var focusTask: TaskItem?
    
    private var filteredTasks: [TaskItem] {
        viewModel.filteredTasks(from: allTasks)
    }
    
    private var activeTasks: [TaskItem] {
        filteredTasks.filter { !$0.isCompleted }
    }
    
    private var completedTasks: [TaskItem] {
        filteredTasks.filter { $0.isCompleted }
    }
    
    var body: some View {
        NavigationView {
            ZStack {
                Theme.primaryBackground.ignoresSafeArea()
                
                VStack(spacing: 0) {
                    // Pull-to-add area
                    pullToAddArea
                    
                    // Main task list
                    ScrollView {
                        LazyVStack(spacing: 0) {
                            // Active tasks
                            ForEach(activeTasks) { task in
                                TaskRowView(
                                    task: task,
                                    isExpanded: viewModel.expandedTaskId == task.id,
                                    onTap: { viewModel.toggleTaskExpansion(task) },
                                    onToggleComplete: { viewModel.toggleTaskCompletion(task) },
                                    onDelete: { deleteTask(task) },
                                    onEdit: { editTask(task) },
                                    onFocus: { startFocus(task) }
                                )
                                
                                if viewModel.expandedTaskId == task.id {
                                    TaskExpandedView(
                                        task: task,
                                        onAddSubtask: { text in
                                            viewModel.addSubtaskToTask(task, text: text)
                                        },
                                        onToggleSubtask: { subtask in
                                            viewModel.toggleSubtask(subtask)
                                        },
                                        onDeleteSubtask: { subtask in
                                            viewModel.deleteSubtask(subtask, from: task)
                                        },
                                        onEdit: { editTask(task) },
                                        onDelete: { deleteTask(task) },
                                        onFocus: { startFocus(task) },
                                        onDone: { viewModel.toggleTaskCompletion(task) }
                                    )
                                    .transition(.opacity.combined(with: .scale))
                                }
                            }
                            
                            // Completed tasks separator
                            if !completedTasks.isEmpty && viewModel.showingCompletedTasks {
                                completedTasksSeparator
                            }
                            
                            // Completed tasks
                            if viewModel.showingCompletedTasks {
                                ForEach(completedTasks) { task in
                                    TaskRowView(
                                        task: task,
                                        isExpanded: false,
                                        onTap: { },
                                        onToggleComplete: { viewModel.toggleTaskCompletion(task) },
                                        onDelete: { deleteTask(task) },
                                        onEdit: { editTask(task) },
                                        onFocus: { startFocus(task) }
                                    )
                                }
                            }
                        }
                        .padding(.horizontal, Theme.spacing16)
                    }
                    .refreshable {
                        // Refresh gesture - could sync with cloud in future
                        HapticManager.shared.lightImpact()
                    }
                }
            }
            .navigationBarHidden(true)
            .onAppear {
                viewModel.setModelContext(modelContext)
            }
            .sheet(isPresented: $showingTaskEditor) {
                TaskEditorView(
                    task: editingTask,
                    onSave: { text, note in
                        if let editingTask = editingTask {
                            viewModel.updateTask(editingTask, text: text, note: note)
                        } else {
                            viewModel.createTask(text: text, note: note)
                        }
                        self.editingTask = nil
                    },
                    onCancel: {
                        self.editingTask = nil
                    }
                )
            }
            .fullScreenCover(isPresented: $showingFocusTimer) {
                FocusTimerView(
                    task: focusTask!,
                    viewModel: focusViewModel,
                    onComplete: { focusedSeconds in
                        if let task = focusTask {
                            viewModel.addFocusTime(to: task, seconds: focusedSeconds)
                        }
                        focusTask = nil
                        showingFocusTimer = false
                    }
                )
            }
            .sheet(isPresented: $showingCompletedArchive) {
                CompletedArchiveView(tasks: completedTasks)
            }
            .alert("Delete Task", isPresented: $showingDeleteConfirmation) {
                Button("Cancel", role: .cancel) {
                    taskToDelete = nil
                }
                Button("Delete", role: .destructive) {
                    if let task = taskToDelete {
                        viewModel.deleteTask(task)
                    }
                    taskToDelete = nil
                }
            } message: {
                Text("Are you sure you want to remove this task?")
            }
        }
    }
    
    // MARK: - Pull to Add Area
    
    private var pullToAddArea: some View {
        Rectangle()
            .fill(Theme.primaryBackground)
            .frame(height: 44)
            .overlay(
                HStack {
                    Spacer()
                    Button(action: { showTaskEditor() }) {
                        Image(systemName: "plus")
                            .font(.title2)
                            .foregroundColor(Theme.accentBlue)
                    }
                    .padding(.trailing, Theme.spacing16)
                }
            )
            .onTapGesture {
                showTaskEditor()
            }
    }
    
    // MARK: - Completed Tasks Separator
    
    private var completedTasksSeparator: some View {
        HStack {
            Text("Completed (\(completedTasks.count))")
                .font(Theme.caption)
                .foregroundColor(Theme.tertiaryText)
                .padding(.leading, Theme.spacing16)
            
            Spacer()
            
            Button(action: {
                viewModel.toggleCompletedTasksVisibility()
            }) {
                Image(systemName: viewModel.showingCompletedTasks ? "chevron.up" : "chevron.down")
                    .font(.caption)
                    .foregroundColor(Theme.tertiaryText)
                    .padding(.trailing, Theme.spacing16)
            }
        }
        .padding(.vertical, Theme.spacing8)
        .background(Theme.groupedBackground)
    }
    
    // MARK: - Actions
    
    private func showTaskEditor() {
        editingTask = nil
        showingTaskEditor = true
        HapticManager.shared.lightImpact()
    }
    
    private func editTask(_ task: TaskItem) {
        editingTask = task
        showingTaskEditor = true
        viewModel.collapseTask()
        HapticManager.shared.lightImpact()
    }
    
    private func deleteTask(_ task: TaskItem) {
        taskToDelete = task
        showingDeleteConfirmation = true
        viewModel.collapseTask()
    }
    
    private func startFocus(_ task: TaskItem) {
        focusTask = task
        showingFocusTimer = true
        viewModel.collapseTask()
    }
}

#Preview {
    TaskListView()
        .modelContainer(for: [TaskItem.self, SubTask.self, TaskList.self])
}