package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"os"
	"time"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"
)

// Paths
const LogFile = "../dat/json/changes_log.json"

// Styles
var (
	titleStyle = lipgloss.NewStyle().
		Bold(true).
		Foreground(lipgloss.Color("#7D56F4")).
		Padding(0, 1)
	
	itemStyle = lipgloss.NewStyle().
		PaddingLeft(2)

	selectedItemStyle = lipgloss.NewStyle().
		PaddingLeft(0).
		Foreground(lipgloss.Color("#EE6FF8")).
		Bold(true).
		SetString("> ")
)

// LogEntry represents a line in the JSON log
type LogEntry struct {
	Timestamp string `json:"timestamp"`
	File      string `json:"file"`
	Change    string `json:"change"`
}

// Model for Bubble Tea
type model struct {
	logs     []LogEntry
	cursor   int
	selected map[int]struct{}
	err      error
}

func initialModel() model {
	logs, err := loadLogs()
	if err != nil {
		return model{err: err}
	}
	return model{
		logs:     logs,
		selected: make(map[int]struct{}),
	}
}

func loadLogs() ([]LogEntry, error) {
	file, err := os.Open(LogFile)
	if err != nil {
		if os.IsNotExist(err) {
			return []LogEntry{}, nil 
		}
		return nil, err
	}
	defer file.Close()

	var logs []LogEntry
	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		var entry LogEntry
		if err := json.Unmarshal(scanner.Bytes(), &entry); err == nil {
			logs = append(logs, entry)
		}
	}
	// Reverse to show newest first
	for i, j := 0, len(logs)-1; i < j; i, j = i+1, j-1 {
		logs[i], logs[j] = logs[j], logs[i]
	}
	return logs, nil
}

func (m model) Init() tea.Cmd {
	return nil
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case tea.KeyMsg:
		switch msg.String() {
		case "ctrl+c", "q":
			return m, tea.Quit
		case "up", "k":
			if m.cursor > 0 {
				m.cursor--
			}
		case "down", "j":
			if m.cursor < len(m.logs)-1 {
				m.cursor++
			}
		case "enter":
			// Select/Deselect
			if _, ok := m.selected[m.cursor]; ok {
				delete(m.selected, m.cursor)
			} else {
				m.selected[m.cursor] = struct{}{}
			}
		case "r":
			// Refresh logs
			logs, err := loadLogs()
			if err == nil {
				m.logs = logs
				m.cursor = 0
			}
		}
	}
	return m, nil
}

func (m model) View() string {
	if m.err != nil {
		return fmt.Sprintf("Error: %v", m.err)
	}

	if len(m.logs) == 0 {
		return "No logs found in " + LogFile + ".\nRun the C++ monitor first!\n\nPress 'q' to quit."
	}

	s := titleStyle.Render("Acto-Sphere Log Monitor") + "\n\n"
	s += "Keys: ↑/↓ to move • Enter to select • 'r' to reload • 'q' to quit\n\n"

	// Simple pagination or limit view to prevent overflow
	start, end := 0, len(m.logs)
	if end > 20 {
		end = 20 // Show only top 20 for this simple demo
	}

	for i := start; i < end; i++ {
		log := m.logs[i]
		cursor := "  "
		line := fmt.Sprintf("[%s] %s - %s", log.Timestamp, log.Change, log.File)
		
		st := itemStyle
		if m.cursor == i {
			cursor = "> "
			st = selectedItemStyle
		}

		if _, ok := m.selected[i]; ok {
			line = "[x] " + line
		} else {
			line = "[ ] " + line
		}

		s += st.Render(cursor + line) + "\n"
	}

	return s
}

func main() {
	p := tea.NewProgram(initialModel())
	if _, err := p.Run(); err != nil {
		fmt.Printf("Alas, there's been an error: %v", err)
		os.Exit(1)
	}
}
