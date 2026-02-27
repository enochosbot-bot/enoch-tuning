import Foundation
import SwiftData

@Model
final class SubTask {
    var id: UUID
    var text: String
    var isCompleted: Bool
    var createdAt: Date
    
    @Relationship
    var parentTask: TaskItem?
    
    init(
        id: UUID = UUID(),
        text: String = "",
        isCompleted: Bool = false,
        createdAt: Date = Date(),
        parentTask: TaskItem? = nil
    ) {
        self.id = id
        self.text = text
        self.isCompleted = isCompleted
        self.createdAt = createdAt
        self.parentTask = parentTask
    }
    
    func toggle() {
        isCompleted.toggle()
    }
}