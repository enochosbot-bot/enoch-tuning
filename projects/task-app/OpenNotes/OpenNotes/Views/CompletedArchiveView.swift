import SwiftUI

struct CompletedArchiveView: View {
    let tasks: [TaskItem]
    
    @Environment(\.dismiss) private var dismiss
    @State private var searchText = ""
    @State private var selectedFilter = "All"
    
    private let filters = ["All", "Today", "Yesterday", "This Week", "This Month"]
    
    private var filteredTasks: [TaskItem] {
        var filtered = tasks.filter(\.isCompleted)
        
        // Apply search filter
        if !searchText.isEmpty {
            filtered = filtered.filter { task in
                task.text.localizedCaseInsensitiveContains(searchText) ||
                task.note.localizedCaseInsensitiveContains(searchText)
            }
        }
        
        // Apply date filter
        let now = Date()
        let calendar = Calendar.current
        
        switch selectedFilter {
        case "Today":
            filtered = filtered.filter { task in
                guard let completedAt = task.completedAt else { return false }
                return calendar.isDate(completedAt, inSameDayAs: now)
            }
        case "Yesterday":
            filtered = filtered.filter { task in
                guard let completedAt = task.completedAt else { return false }
                return calendar.isDate(completedAt, inSameDayAs: calendar.date(byAdding: .day, value: -1, to: now) ?? now)
            }
        case "This Week":
            filtered = filtered.filter { task in
                guard let completedAt = task.completedAt else { return false }
                return calendar.isDate(completedAt, equalTo: now, toGranularity: .weekOfYear)
            }
        case "This Month":
            filtered = filtered.filter { task in
                guard let completedAt = task.completedAt else { return false }
                return calendar.isDate(completedAt, equalTo: now, toGranularity: .month)
            }
        default:
            break // "All" - no additional filtering
        }
        
        return filtered
    }
    
    private var groupedTasks: [(String, [TaskItem])] {
        let calendar = Calendar.current
        let grouped = Dictionary(grouping: filteredTasks) { task -> String in
            guard let completedAt = task.completedAt else { return "Unknown" }
            
            if calendar.isDateInToday(completedAt) {
                return "Today"
            } else if calendar.isDateInYesterday(completedAt) {
                return "Yesterday"
            } else if calendar.isDate(completedAt, equalTo: Date(), toGranularity: .weekOfYear) {
                let formatter = DateFormatter()
                formatter.dateFormat = "EEEE" // Day of week
                return formatter.string(from: completedAt)
            } else {
                let formatter = DateFormatter()
                formatter.dateStyle = .medium
                return formatter.string(from: completedAt)
            }
        }
        
        // Sort groups by most recent first
        return grouped.sorted { lhs, rhs in
            let lhsDate = lhs.value.compactMap(\.completedAt).max() ?? Date.distantPast
            let rhsDate = rhs.value.compactMap(\.completedAt).max() ?? Date.distantPast
            return lhsDate > rhsDate
        }
    }
    
    private var totalCompletedCount: Int {
        tasks.filter(\.isCompleted).count
    }
    
    private var totalFocusTime: String {
        let totalSeconds = tasks.filter(\.isCompleted).reduce(0) { $0 + $1.focusedSeconds }
        let hours = totalSeconds / 3600
        let minutes = (totalSeconds % 3600) / 60
        
        if hours > 0 {
            return "\(hours)h \(minutes)m"
        } else {
            return "\(minutes)m"
        }
    }
    
    var body: some View {
        NavigationView {
            VStack(spacing: 0) {
                // Header with search and filter
                headerSection
                
                // Task list
                ScrollView {
                    LazyVStack(spacing: Theme.spacing12) {
                        ForEach(groupedTasks, id: \.0) { groupName, groupTasks in
                            taskGroupSection(title: groupName, tasks: groupTasks)
                        }
                        
                        if filteredTasks.isEmpty {
                            emptyStateView
                        }
                    }
                    .padding(.horizontal, Theme.spacing16)
                    .padding(.top, Theme.spacing16)
                }
                
                // Stats footer
                statsFooter
            }
            .background(Theme.groupedBackground)
            .navigationTitle("Completed")
            .navigationBarTitleDisplayMode(.inline)
            .toolbar {
                ToolbarItem(placement: .navigationBarLeading) {
                    Button("Close") {
                        dismiss()
                    }
                    .foregroundColor(Theme.accentBlue)
                }
                
                ToolbarItem(placement: .navigationBarTrailing) {
                    Button(action: {
                        // TODO: Settings
                    }) {
                        Image(systemName: "gearshape")
                            .foregroundColor(Theme.secondaryText)
                    }
                }
            }
        }
    }
    
    // MARK: - Header Section
    
    private var headerSection: some View {
        VStack(spacing: Theme.spacing12) {
            // Search bar
            HStack {
                Image(systemName: "magnifyingglass")
                    .foregroundColor(Theme.tertiaryText)
                
                TextField("Search completed tasks", text: $searchText)
                    .textFieldStyle(PlainTextFieldStyle())
                
                if !searchText.isEmpty {
                    Button(action: { searchText = "" }) {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundColor(Theme.tertiaryText)
                    }
                }
            }
            .padding(.horizontal, Theme.spacing16)
            .padding(.vertical, Theme.spacing12)
            .background(Theme.secondaryBackground)
            .cornerRadius(Theme.cornerRadiusMedium)
            
            // Filter dropdown
            ScrollView(.horizontal, showsIndicators: false) {
                HStack(spacing: Theme.spacing12) {
                    ForEach(filters, id: \.self) { filter in
                        filterButton(filter)
                    }
                }
                .padding(.horizontal, Theme.spacing16)
            }
        }
        .padding(.horizontal, Theme.spacing16)
        .padding(.vertical, Theme.spacing16)
        .background(Theme.primaryBackground)
    }
    
    private func filterButton(_ filter: String) -> some View {
        Button(action: {
            selectedFilter = filter
            HapticManager.shared.selectionChanged()
        }) {
            Text(filter)
                .font(Theme.callout)
                .foregroundColor(selectedFilter == filter ? .white : Theme.primaryText)
                .padding(.horizontal, Theme.spacing16)
                .padding(.vertical, Theme.spacing8)
                .background(
                    RoundedRectangle(cornerRadius: Theme.cornerRadiusLarge)
                        .fill(selectedFilter == filter ? Theme.accentBlue : Theme.tertiaryBackground)
                )
        }
        .buttonStyle(PlainButtonStyle())
    }
    
    // MARK: - Task Group Section
    
    private func taskGroupSection(title: String, tasks: [TaskItem]) -> some View {
        VStack(alignment: .leading, spacing: Theme.spacing8) {
            // Group header
            HStack {
                Text(title)
                    .font(Theme.headline)
                    .foregroundColor(Theme.primaryText)
                
                Spacer()
                
                Text("\(tasks.count)")
                    .font(Theme.caption)
                    .foregroundColor(Theme.tertiaryText)
                    .padding(.horizontal, Theme.spacing8)
                    .padding(.vertical, Theme.spacing4)
                    .background(Theme.tertiaryBackground)
                    .cornerRadius(Theme.cornerRadiusSmall)
            }
            
            // Tasks in group
            VStack(spacing: 0) {
                ForEach(tasks.sorted { ($0.completedAt ?? Date.distantPast) > ($1.completedAt ?? Date.distantPast) }) { task in
                    completedTaskRow(task)
                }
            }
            .background(Theme.primaryBackground)
            .cornerRadius(Theme.cornerRadiusMedium)
        }
    }
    
    private func completedTaskRow(_ task: TaskItem) -> some View {
        VStack(alignment: .leading, spacing: Theme.spacing8) {
            HStack(spacing: Theme.spacing12) {
                // Checkmark
                Image(systemName: "checkmark.circle.fill")
                    .font(.title3)
                    .foregroundColor(Theme.accentBlue)
                
                // Task content
                VStack(alignment: .leading, spacing: Theme.spacing4) {
                    Text(task.text)
                        .font(Theme.body)
                        .foregroundColor(Theme.completedTaskText)
                        .strikethrough()
                    
                    if task.hasNote {
                        Text(task.note)
                            .font(Theme.caption)
                            .foregroundColor(Theme.tertiaryText)
                            .lineLimit(2)
                    }
                    
                    // Completion info
                    HStack(spacing: Theme.spacing16) {
                        if let completedAt = task.completedAt {
                            HStack(spacing: Theme.spacing4) {
                                Image(systemName: "clock")
                                    .font(.caption2)
                                Text(formatCompletionTime(completedAt))
                                    .font(.caption2)
                            }
                            .foregroundColor(Theme.tertiaryText)
                        }
                        
                        if task.focusedSeconds > 0 {
                            HStack(spacing: Theme.spacing4) {
                                Image(systemName: "timer")
                                    .font(.caption2)
                                Text(task.formattedFocusTime)
                                    .font(.caption2)
                            }
                            .foregroundColor(Theme.focusRed)
                        }
                        
                        if task.hasSubtasks {
                            HStack(spacing: Theme.spacing4) {
                                Image(systemName: "checkmark.square")
                                    .font(.caption2)
                                Text("\(task.completedSubtasksCount)/\(task.subtasks.count)")
                                    .font(.caption2)
                            }
                            .foregroundColor(Theme.tertiaryText)
                        }
                    }
                }
                
                Spacer()
            }
            .padding(.horizontal, Theme.spacing16)
            .padding(.vertical, Theme.spacing12)
            
            if task != tasks.last {
                Divider()
                    .padding(.leading, Theme.spacing52)
            }
        }
    }
    
    // MARK: - Empty State
    
    private var emptyStateView: some View {
        VStack(spacing: Theme.spacing16) {
            Image(systemName: "checkmark.circle")
                .font(.system(size: 64))
                .foregroundColor(Theme.tertiaryText)
            
            Text("No completed tasks")
                .font(Theme.headline)
                .foregroundColor(Theme.primaryText)
            
            Text("Tasks you complete will appear here")
                .font(Theme.callout)
                .foregroundColor(Theme.secondaryText)
                .multilineTextAlignment(.center)
        }
        .padding(.top, Theme.spacing48)
    }
    
    // MARK: - Stats Footer
    
    private var statsFooter: some View {
        HStack {
            VStack(alignment: .leading, spacing: Theme.spacing4) {
                Text("Total Completed")
                    .font(Theme.caption2)
                    .foregroundColor(Theme.tertiaryText)
                Text("\(totalCompletedCount)")
                    .font(Theme.headline)
                    .foregroundColor(Theme.primaryText)
            }
            
            Spacer()
            
            VStack(alignment: .trailing, spacing: Theme.spacing4) {
                Text("Total Focus Time")
                    .font(Theme.caption2)
                    .foregroundColor(Theme.tertiaryText)
                Text(totalFocusTime)
                    .font(Theme.headline)
                    .foregroundColor(Theme.focusRed)
            }
            
            Spacer()
            
            Button(action: {
                // TODO: More stats/export
            }) {
                VStack(spacing: Theme.spacing4) {
                    Image(systemName: "chevron.right")
                        .font(.caption)
                    Text("More")
                        .font(Theme.caption2)
                }
                .foregroundColor(Theme.accentBlue)
            }
        }
        .padding(.horizontal, Theme.spacing16)
        .padding(.vertical, Theme.spacing16)
        .background(Theme.primaryBackground)
    }
    
    // MARK: - Helpers
    
    private func formatCompletionTime(_ date: Date) -> String {
        let formatter = DateFormatter()
        formatter.timeStyle = .short
        return formatter.string(from: date)
    }
}

#Preview {
    let sampleTasks = [
        TaskItem(text: "Completed task 1", isCompleted: true, completedAt: Date()),
        TaskItem(text: "Completed task 2", note: "With a note", isCompleted: true, completedAt: Calendar.current.date(byAdding: .hour, value: -2, to: Date())!, focusedSeconds: 1800),
        TaskItem(text: "Yesterday's task", isCompleted: true, completedAt: Calendar.current.date(byAdding: .day, value: -1, to: Date())!)
    ]
    
    return CompletedArchiveView(tasks: sampleTasks)
}