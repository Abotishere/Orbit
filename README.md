# 🪐 Orbit — Your Day, in Motion

**Orbit** is a desktop To-Do List application built with Python, Tkinter, and SQLite. It helps you organize daily tasks, manage priorities, track deadlines, and monitor your progress through a simple graphical interface.

The goal is to make everyday task management straightforward, organized, and accessible — right from your desktop.

## ✨ Features

- **Task Management** — Create, edit, delete, and reopen tasks.
- **Priority Levels** — Categorize tasks as Low, Medium, or High priority.
- **Deadline Tracking** — Set due dates and identify overdue tasks.
- **Search** — Find tasks by title or description.
- **Filters** — Filter tasks by completion status, overdue status, and priority.
- **Sorting** — Organize tasks by due date, priority, creation date, or title.
- **Progress Dashboard** — View total, pending, completed, and overdue tasks, along with your completion percentage.
- **Local Data Storage** — Store tasks persistently using SQLite.
- **Desktop Interface** — Use a native Python GUI built with Tkinter and themed `ttk` widgets.

## 🛠️ Tech Stack

| Technology    | Purpose                               |
| ------------- | ------------------------------------- |
| Python 3      | Application logic                     |
| Tkinter / ttk | Desktop graphical interface           |
| SQLite        | Local database                        |
| `datetime`    | Date validation and deadline tracking |

No third-party Python packages are required for the current version.

## 📁 Project Structure

```text
Orbit/
├── app.py          # Main application and GUI
├── database.py     # Database operations
├── README.md       # Project documentation
├── .gitignore      # Files excluded from Git
└── tasks.db        # Generated locally at runtime
```

The database file is generated automatically when the application starts. It is intended to remain local and should not be committed to Git.

## 🚀 Getting Started

### Prerequisites

- Python 3 installed on your computer
- Tkinter available in your Python installation
- Git (optional, for cloning and version control)

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Orbit.git
cd Orbit
```

Replace `YOUR_USERNAME` with your GitHub username.

### 2. Create a virtual environment

**Windows — PowerShell or Git Bash:**

```bash
python -m venv .venv
```

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or activate it in Git Bash:

```bash
source .venv/Scripts/activate
```

If PowerShell blocks activation scripts, you can use Git Bash or Command Prompt instead.

### 3. Run the application

```bash
python app.py
```

Orbit's desktop window should open, and the SQLite database will be initialized automatically if it does not already exist.

## 📖 How to Use

1. Launch Orbit using `python app.py`.
2. Select **Add Task** to create a task.
3. Enter a title, optional description, priority, and due date.
4. Select a task to edit, complete or reopen, or delete it.
5. Use the search bar and filters to find specific tasks.
6. Change the sorting option to organize your task list.
7. Monitor overall progress using the dashboard.

Due dates should be entered in `YYYY-MM-DD` format, for example, `2026-12-31`.

## 🗃️ Data Storage

Orbit uses SQLite to save tasks locally in `tasks.db`. Your data persists between application sessions on the same computer.

Because the database is local, it is not automatically synchronized between devices. Back up the database separately if you need to preserve your task data.

## 🛣️ Roadmap

Potential future improvements include:

- A more polished, modern desktop interface
- Calendar-based date selection
- Task completion notifications and reminders
- CSV export and data backup options
- Keyboard shortcuts
- Improved visual indicators for priorities and overdue tasks
- Packaging as a standalone Windows executable

## 🤝 Contributing

Suggestions, bug reports, and improvements are welcome. Feel free to fork the repository, experiment with new features, and submit a pull request.

## 📄 License

No license has been selected yet. All rights are reserved by default until a license is added.&#x20;

---

*Orbit — Keep your day in motion.* 🪐
