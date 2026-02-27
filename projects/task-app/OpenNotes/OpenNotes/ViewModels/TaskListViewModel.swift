import Foundation
import SwiftData
import SwiftUI

@MainActor
class TaskListViewModel: ObservableObject {
    @Published var searchText = ""
    @Published var showingCompletedTasks = true
    @Published var expandedTaskId: UUID?
    
    private var modelContext: ModelContext?
    
    func setModelContext(_ context: ModelContext) {
        self.modelContext = context
    }
    
    // MARK: - Task Operations
    
    func createTask(text: String, note: String = "") {
        guard let context = modelContext else { return }
        
        let maxSortOrder = getMaxSortOrder()
        let newTask = TaskItem(
            text: text.trimmingCharacters(in: .whitespacesAndNewlines),
            note: note.trimmingCharacters(in: .whitespacesAndNewlines),
            sortOrder: maxSortOrder + 1
        )
        
        context.insert(newTask)
        saveContext()
        HapticManager.shared.lightImpact()
    }
    
    func updateTask(_ task: TaskItem, text: String, note: String) {
        task.text = text.trimmingCharacters(in: .whitespacesAndNewlines)
        task.note = note.trimmingCharacters(in: .whitespacesAndNewlines)
        saveContext()
    }
    
    func deleteTask(_ task: TaskItem) {
        guard let context = modelContext else { return }
        
        context.delete(task)
        saveContext()
        HapticManager.shared.taskDeleted()
        
        // Clear expanded state if this task was expanded
        if expandedTaskId == task.id {
            expandedTaskId = nil
        }
    }
    
    func toggleTaskCompletion(_ task: TaskItem) {
        task.toggle()
        
        if task.isCompleted {
            // Move to bottom by setting sortOrder to max + 1
            let maxSortOrder = getMaxSortOrder()
            task.sortOrder = maxSortOrder + 1
            HapticManager.shared.taskCompleted()
        } else {
            // Move back to top for active tasks
            task.sortOrder = 0
            reorderActiveTasks()
            HapticManager.shared.lightImpact()
        }
        
        saveContext()
        
        // Collapse task if it was expanded
        if expandedTaskId == task.id {
            expandedTaskId = nil
        }
    }
    
    func addSubtaskToTask(_ task: TaskItem, text: String) {
        let subtask = SubTask(text: text, parentTask: task)
        task.subtasks.append(subtask)
        saveContext()
    }
    
    func toggleSubtask(_ subtask: SubTask) {
        subtask.toggle()
        saveContext()
        HapticManager.shared.lightImpact()
    }
    
    func deleteSubtask(_ subtask: SubTask, from task: TaskItem) {
        guard let context = modelContext else { return }
        
        if let index = task.subtasks.firstIndex(of: subtask) {
            task.subtasks.remove(at: index)
        }
        context.delete(subtask)
        saveContext()
        HapticManager.shared.lightImpact()
    }
    
    // MARK: - Focus Time
    
    func addFocusTime(to task: TaskItem, seconds: Int) {
        task.focusedSeconds += seconds
        saveContext()
    }
    
    // MARK: - Task Expansion
    
    func toggleTaskExpansion(_ task: TaskItem) {
        withAnimation(Theme.standardAnimation) {
            if expandedTaskId == task.id {
                expandedTaskId = nil
            } else {
                expandedTaskId = task.id
                HapticManager.shared.taskSelected()
            }
        }
    }
    
    func collapseTask() {
        withAnimation(Theme.standardAnimation) {
            expandedTaskId = nil
        }
    }
    
    // MARK: - Task Reordering
    
    func moveTask(from source: IndexSet, to destination: Int, in tasks: [TaskItem]) {
        var reorderedTasks = tasks
        reorderedTasks.move(fromOffsets: source, toOffset: destination)
        
        // Update sortOrder for all affected tasks
        for (index, task) in reorderedTasks.enumerated() {
            task.sortOrder = index
        }
        
        saveContext()
    }
    
    private func reorderActiveTasks() {
        guard let context = modelContext else { return }
        
        let activeTasks = try? context.fetch(
            FetchDescriptor<TaskItem>(
                predicate: #Predicate<TaskItem> { !$0.isCompleted },
                sortBy: [SortDescriptor(\TaskItem.createdAt, order: .forward)]
            )
        )
        
        activeTasks?.enumerated().forEach { index, task in
            task.sortOrder = index
        }
    }
    
    private func getMaxSortOrder() -> Int {
        guard let context = modelContext else { return 0 }
        
        do {
            let allTasks = try context.fetch(FetchDescriptor<TaskItem>())
            return allTasks.map(\.sortOrder).max() ?? 0
        } catch {
            return 0
        }
    }
    
    // MARK: - Search & Filter
    
    func filteredTasks(from tasks: [TaskItem]) -> [TaskItem] {
        var filtered = tasks
        
        // Apply search filter
        if !searchText.isEmpty {
            filtered = filtered.filter { task in
                task.text.localizedCaseInsensitiveContains(searchText) ||
                task.note.localizedCaseInsensitiveContains(searchText) ||
                task.subtasks.contains { subtask in
                    subtask.text.localizedCaseInsensitiveContains(searchText)
                }
            }
        }
        
        // Apply completion filter
        if !showingCompletedTasks {
            filtered = filtered.filter { !$0.isCompleted }
        }
        
        return filtered
    }
    
    func toggleCompletedTasksVisibility() {
        withAnimation(Theme.standardAnimation) {
            showingCompletedTasks.toggle()
        }
    }
    
    // MARK: - Statistics
    
    func getCompletedTasksCount(from tasks: [TaskItem]) -> Int {
        tasks.filter(\.isCompleted).count
    }
    
    func getTotalFocusTime(from tasks: [TaskItem]) -> Int {
        tasks.reduce(0) { $0 + $1.focusedSeconds }
    }
    
    func getFormattedFocusTime(from tasks: [TaskItem]) -> String {
        let totalSeconds = getTotalFocusTime(from: tasks)
        let hours = totalSeconds / 3600
        let minutes = (totalSeconds % 3600) / 60
        
        if hours > 0 {
            return "\(hours)h \(minutes)m"
        } else {
            return "\(minutes)m"
        }
    }
    
    // MARK: - Private Helpers
    
    private func saveContext() {
        guard let context = modelContext else { return }
        
        do {
            try context.save()
        } catch {
            print("Failed to save context: \(error)")
        }
    }
}