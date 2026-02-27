import Foundation
import SwiftData

@Model
final class TaskList {
    var id: UUID
    var name: String
    var createdAt: Date
    
    init(
        id: UUID = UUID(),
        name: String = "Default",
        createdAt: Date = Date()
    ) {
        self.id = id
        self.name = name
        self.createdAt = createdAt
    }
}