import SwiftUI
import SwiftData

@main
struct OpenNotesApp: App {
    var body: some Scene {
        WindowGroup {
            TaskListView()
        }
        .modelContainer(for: [TaskItem.self, SubTask.self, TaskList.self])
    }
}