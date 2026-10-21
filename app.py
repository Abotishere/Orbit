
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

import database


class OrbitApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Orbit — Your Daily Planner")
        self.root.geometry("1050x680")
        self.root.minsize(850, 550)

        self.search_var = tk.StringVar()
        self.status_var = tk.StringVar(value="All")
        self.priority_filter_var = tk.StringVar(value="All")
        self.sort_var = tk.StringVar(value="Due date")

        self.setup_style()
        self.build_ui()
        self.refresh_tasks()

    def setup_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold")
        )
        style.configure("Title.TLabel", font=("Segoe UI", 22, "bold"))
        style.configure("Card.TLabel", font=("Segoe UI", 12, "bold"))

    def build_ui(self):
        main = ttk.Frame(self.root, padding=18)
        main.pack(fill="both", expand=True)

        header = ttk.Frame(main)
        header.pack(fill="x", pady=(0, 16))

        ttk.Label(
            header, text="My To-Do List", style="Title.TLabel"
        ).pack(side="left")

        ttk.Button(
            header, text="+ Add Task", command=self.open_add_dialog
        ).pack(side="right")

        # Dashboard
        dashboard = ttk.Frame(main)
        dashboard.pack(fill="x", pady=(0, 16))

        self.stats = {}
        for key, label in [
            ("total", "Total Tasks"),
            ("pending", "Pending"),
            ("completed", "Completed"),
            ("overdue", "Overdue"),
        ]:
            card = ttk.LabelFrame(dashboard, text=label, padding=12)
            card.pack(side="left", fill="x", expand=True, padx=(0, 8))
            self.stats[key] = ttk.Label(
                card, text="0", style="Card.TLabel"
            )
            self.stats[key].pack(anchor="w")

        self.progress_label = ttk.Label(main, text="Progress: 0%")
        self.progress_label.pack(anchor="w")

        self.progress = ttk.Progressbar(
            main, orient="horizontal", mode="determinate", maximum=100
        )
        self.progress.pack(fill="x", pady=(5, 16))

        # Search and filters
        controls = ttk.Frame(main)
        controls.pack(fill="x", pady=(0, 12))

        ttk.Label(controls, text="Search:").pack(side="left")
        search = ttk.Entry(
            controls, textvariable=self.search_var, width=23
        )
        search.pack(side="left", padx=(5, 12))
        search.bind("<KeyRelease>", lambda event: self.refresh_tasks())

        ttk.Label(controls, text="Status:").pack(side="left")
        status = ttk.Combobox(
            controls, textvariable=self.status_var,
            values=["All", "Pending", "Completed", "Overdue"],
            state="readonly", width=11
        )
        status.pack(side="left", padx=5)
        status.bind("<<ComboboxSelected>>",
                    lambda event: self.refresh_tasks())

        ttk.Label(controls, text="Priority:").pack(side="left")
        priority = ttk.Combobox(
            controls, textvariable=self.priority_filter_var,
            values=["All", "High", "Medium", "Low"],
            state="readonly", width=9
        )
        priority.pack(side="left", padx=5)
        priority.bind("<<ComboboxSelected>>",
                      lambda event: self.refresh_tasks())

        ttk.Label(controls, text="Sort:").pack(side="left", padx=(8, 0))
        sorting = ttk.Combobox(
            controls, textvariable=self.sort_var,
            values=["Due date", "Priority", "Created", "Title"],
            state="readonly", width=11
        )
        sorting.pack(side="left", padx=5)
        sorting.bind("<<ComboboxSelected>>",
                     lambda event: self.refresh_tasks())

        # Task table
        table_frame = ttk.Frame(main)
        table_frame.pack(fill="both", expand=True)

        columns = (
            "id", "title", "priority", "due_date",
            "status", "created_at"
        )
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings",
            selectmode="browse"
        )

        headings = {
            "id": "ID",
            "title": "Task",
            "priority": "Priority",
            "due_date": "Due Date",
            "status": "Status",
            "created_at": "Created",
        }
        widths = {
            "id": 45, "title": 300, "priority": 95,
            "due_date": 110, "status": 100, "created_at": 150
        }

        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(
                column, width=widths[column],
                anchor="w" if column == "title" else "center"
            )

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree.bind(
            "<Double-1>", lambda event: self.open_edit_dialog()
        )

        # Action buttons
        actions = ttk.Frame(main)
        actions.pack(fill="x", pady=(12, 0))

        ttk.Button(
            actions, text="Edit", command=self.open_edit_dialog
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            actions, text="Complete / Reopen",
            command=self.toggle_selected
        ).pack(side="left", padx=(0, 8))

        ttk.Button(
            actions, text="Delete", command=self.delete_selected
        ).pack(side="left")

        ttk.Button(
            actions, text="Refresh", command=self.refresh_tasks
        ).pack(side="right")

    def open_add_dialog(self):
        self.task_dialog()

    def open_edit_dialog(self):
        task_id = self.selected_id()
        if task_id is None:
            messagebox.showwarning("Select task", "Select a task first.")
            return

        task = next(
            (t for t in database.get_tasks() if t["id"] == task_id),
            None
        )
        if task:
            self.task_dialog(task)

    def task_dialog(self, task=None):
        editing = task is not None
        dialog = tk.Toplevel(self.root)
        dialog.title("Edit Task" if editing else "Add Task")
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        frame = ttk.Frame(dialog, padding=18)
        frame.pack(fill="both", expand=True)

        title_var = tk.StringVar(
            value=task["title"] if editing else ""
        )
        priority_var = tk.StringVar(
            value=task["priority"] if editing else "Medium"
        )
        due_var = tk.StringVar(
            value=task["due_date"] if editing else ""
        )

        ttk.Label(frame, text="Title *").grid(
            row=0, column=0, sticky="w", pady=6
        )
        title_entry = ttk.Entry(frame, textvariable=title_var, width=42)
        title_entry.grid(row=0, column=1, sticky="ew", pady=6)

        ttk.Label(frame, text="Description").grid(
            row=1, column=0, sticky="nw", pady=6
        )
        description = tk.Text(frame, width=32, height=5, wrap="word")
        description.grid(row=1, column=1, sticky="ew", pady=6)
        if editing:
            description.insert("1.0", task["description"] or "")

        ttk.Label(frame, text="Priority").grid(
            row=2, column=0, sticky="w", pady=6
        )
        ttk.Combobox(
            frame, textvariable=priority_var,
            values=["Low", "Medium", "High"],
            state="readonly", width=12
        ).grid(row=2, column=1, sticky="w", pady=6)

        ttk.Label(frame, text="Due date").grid(
            row=3, column=0, sticky="w", pady=6
        )
        due_entry = ttk.Entry(frame, textvariable=due_var, width=18)
        due_entry.grid(row=3, column=1, sticky="w", pady=6)
        ttk.Label(
            frame, text="Format: YYYY-MM-DD (optional)"
        ).grid(row=4, column=1, sticky="w")

        def save():
            title = title_var.get().strip()
            due = due_var.get().strip()
            desc = description.get("1.0", "end-1c").strip()
            priority = priority_var.get()

            if not title:
                messagebox.showerror(
                    "Missing title", "Please enter a task title.",
                    parent=dialog
                )
                return

            if due:
                try:
                    datetime.strptime(due, "%Y-%m-%d")
                except ValueError:
                    messagebox.showerror(
                        "Invalid date",
                        "Use a valid date in YYYY-MM-DD format.",
                        parent=dialog
                    )
                    return

            if editing:
                database.update_task(
                    task["id"], title, desc, priority, due
                )
            else:
                database.add_task(title, desc, priority, due)

            dialog.destroy()
            self.refresh_tasks()

        buttons = ttk.Frame(frame)
        buttons.grid(row=5, column=0, columnspan=2, pady=(16, 0))
        ttk.Button(buttons, text="Save", command=save).pack(
            side="left", padx=5
        )
        ttk.Button(
            buttons, text="Cancel", command=dialog.destroy
        ).pack(side="left", padx=5)

        title_entry.focus_set()
        title_entry.bind("<Return>", lambda event: save())
        due_entry.bind("<Return>", lambda event: save())

    def selected_id(self):
        selection = self.tree.selection()
        if not selection:
            return None
        return int(selection[0])

    def toggle_selected(self):
        task_id = self.selected_id()
        if task_id is None:
            messagebox.showwarning("Select task", "Select a task first.")
            return

        task = next(
            (t for t in database.get_tasks() if t["id"] == task_id),
            None
        )
        if task:
            database.toggle_task(task_id, not task["completed"])
            self.refresh_tasks()

    def delete_selected(self):
        task_id = self.selected_id()
        if task_id is None:
            messagebox.showwarning("Select task", "Select a task first.")
            return

        if messagebox.askyesno(
            "Confirm deletion", "Delete the selected task?"
        ):
            database.delete_task(task_id)
            self.refresh_tasks()

    def refresh_tasks(self):
        tasks = database.get_tasks()
        today = date.today().isoformat()

        # Dashboard uses all tasks, regardless of current filters.
        total = len(tasks)
        completed = sum(bool(t["completed"]) for t in tasks)
        pending = total - completed
        overdue = sum(
            1 for t in tasks
            if not t["completed"] and t["due_date"]
            and t["due_date"] < today
        )

        for key, value in [
            ("total", total), ("pending", pending),
            ("completed", completed), ("overdue", overdue)
        ]:
            self.stats[key].config(text=str(value))

        percent = round(completed / total * 100) if total else 0
        self.progress["value"] = percent
        self.progress_label.config(text=f"Progress: {percent}%")

        query = self.search_var.get().strip().casefold()
        status_filter = self.status_var.get()
        priority_filter = self.priority_filter_var.get()

        def matches(task):
            is_overdue = (
                not task["completed"] and task["due_date"]
                and task["due_date"] < today
            )
            searchable = (
                (task["title"] or "") + " " +
                (task["description"] or "")
            ).casefold()

            if query and query not in searchable:
                return False
            if priority_filter != "All" and task["priority"] != priority_filter:
                return False
            if status_filter == "Pending" and task["completed"]:
                return False
            if status_filter == "Completed" and not task["completed"]:
                return False
            if status_filter == "Overdue" and not is_overdue:
                return False
            return True

        tasks = [t for t in tasks if matches(t)]

        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        sort_by = self.sort_var.get()

        if sort_by == "Due date":
            tasks.sort(key=lambda t: (not bool(t["due_date"]),
                                      t["due_date"] or ""))
        elif sort_by == "Priority":
            tasks.sort(key=lambda t: priority_order.get(t["priority"], 3))
        elif sort_by == "Created":
            tasks.sort(key=lambda t: t["created_at"] or "", reverse=True)
        elif sort_by == "Title":
            tasks.sort(key=lambda t: t["title"].casefold())

        for item in self.tree.get_children():
            self.tree.delete(item)

        for task in tasks:
            is_overdue = (
                not task["completed"] and task["due_date"]
                and task["due_date"] < today
            )
            status = (
                "Completed" if task["completed"]
                else "Overdue" if is_overdue
                else "Pending"
            )
            self.tree.insert(
                "", "end", iid=str(task["id"]),
                values=(
                    task["id"], task["title"], task["priority"],
                    task["due_date"] or "—", status, task["created_at"]
                )
            )


if __name__ == "__main__":
    database.initialize_db()
    root = tk.Tk()
    app = OrbitApp(root)
    root.mainloop()
