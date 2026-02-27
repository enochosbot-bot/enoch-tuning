import Foundation
import SwiftData

@Model
final class TaskItem {
    var id: UUID
    var text: String
    var note: String
    var isCompleted: Bool
    var completedAt: Date?
    var createdAt: Date
    var sortOrder: Int
    var focusedSeconds: Int
    var listId: UUID?
    
    @Relationship(deleteRule: .cascade, inverse: \SubTask.parentTask)
    var subtasks: [SubTask]
    
    init(
        id: UUID = UUID(),
        text: String = "",
        note: String = "",
        isCompleted: Bool = false,
        completedAt: Date? = nil,
        createdAt: Date = Date(),
        sortOrder: Int = 0,
        focusedSeconds: Int = 0,
        listId: UUID? = nil,
        subtasks: [SubTask] = []
    ) {
        self.id = id
        self.text = text
        self.note = note
        self.isCompleted = isCompleted
        self.completedAt = completedAt
        self.createdAt = createdAt
        self.sortOrder = sortOrder
        self.focusedSeconds = focusedSeconds
        self.listId = listId
        self.subtasks = subtasks
    }
    
    func toggle() {
        isCompleted.toggle()
        completedAt = isCompleted ? Date() : nil
    }
    
    var hasNote: Bool {
        !note.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
    }
    
    var hasSubtasks: Bool {
        !subtasks.isEmpty
    }
    
    var completedSubtasksCount: Int {
        subtasks.filter(\.isCompleted).count
    }
    
    var formattedFocusTime: String {
        let hours = focusedSeconds / 3600
        let minutes = (focusedSeconds % 3600) / 60
        let seconds = focusedSeconds % 60
        
        if hours > 0 {
            return String(format: "%02d:%02d:%02d", hours, minutes, seconds)
        } else {
            return String(format: "%02d:%02d", minutes, seconds)
        }
    }
}