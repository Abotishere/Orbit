
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date, datetime

import database


class OrbitApp:
    PALETTE = {
        "canvas": "#F3F6FC",
        "surface": "#FFFFFF",
        "ink": "#172B4D",
        "muted": "#667085",
        "border": "#D9E2F0",
        "accent": "#5168E8",
        "accent_hover": "#4055D6",
        "heading": "#E8EDF7",
        "overdue_bg": "#FEF0EF",
        "overdue_fg": "#B42318",
        "completed_bg": "#EAF7F0",
        "completed_fg": "#26734D",
        "high_bg": "#FFF4E5",
        "high_fg": "#8A4B08",
        "low_bg": "#FFFFFF",
        "low_fg": "#172B4D",
    }

    def __init__(self, root):
        self.root = root
        self.root.title("Orbit — Your Daily Planner")
        self.root.geometry("1050x680")
        self.root.minsize(850, 550)
        self.root.configure(background=self.PALETTE["canvas"])

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
        p = self.PALETTE

        style.configure(".", font=("Segoe UI", 10), foreground=p["ink"])
        style.configure("TFrame", background=p["canvas"])
        style.configure("TLabel", background=p["canvas"], foreground=p["ink"])
        style.configure("Title.TLabel", background=p["canvas"],
                        foreground=p["ink"], font=("Segoe UI", 22, "bold"))
        style.configure("Card.TLabel", background=p["surface"],
                        foreground=p["ink"], font=("Segoe UI", 15, "bold"))
        style.configure("Card.TLabelframe", background=p["surface"],
                        bordercolor=p["border"], relief="solid", borderwidth=1)
        style.configure("Card.TLabelframe.Label", background=p["surface"],
                        foreground=p["muted"], font=("Segoe UI", 9, "bold"))

        style.configure("TButton", background=p["surface"],
                        foreground=p["ink"], bordercolor=p["border"],
                        focuscolor=p["accent"], padding=(12, 8),
                        font=("Segoe UI", 10, "bold"))
        style.map("TButton",
                  background=[("pressed", "#E2E8F3"), ("active", "#F7F9FC")],
                  bordercolor=[("focus", p["accent"])])
        style.configure("Accent.TButton", background=p["accent"],
                        foreground=p["surface"], bordercolor=p["accent"],
                        focuscolor=p["surface"], padding=(14, 8),
                        font=("Segoe UI", 10, "bold"))
        style.map("Accent.TButton",
                  background=[("pressed", p["accent_hover"]),
                              ("active", p["accent_hover"])],
                  bordercolor=[("active", p["accent_hover"])])

        style.configure("TEntry", fieldbackground=p["surface"],
                        foreground=p["ink"], bordercolor=p["border"],
                        padding=7)
        style.configure("TCombobox", fieldbackground=p["surface"],
                        background=p["surface"], foreground=p["ink"],
                        bordercolor=p["border"], padding=6, arrowsize=13)
        style.map("TCombobox",
                  fieldbackground=[("readonly", p["surface"])],
                  selectbackground=[("readonly", p["surface"])],
                  selectforeground=[("readonly", p["ink"])])

        style.configure("Treeview", rowheight=34, font=("Segoe UI", 10),
                        background=p["surface"], fieldbackground=p["surface"],
                        foreground=p["ink"], bordercolor=p["border"],
                        relief="flat")
        style.configure(
            "Treeview.Heading",
            font=("Segoe UI", 10, "bold"), background=p["heading"],
            foreground=p["muted"], padding=(10, 9), relief="flat"
        )
        style.map("Treeview.Heading", background=[("active", "#DCE4F4")])
        style.map("Treeview", background=[("selected", p["accent"])],
                  foreground=[("selected", p["surface"])])
        style.configure("Horizontal.TProgressbar", troughcolor=p["border"],
                        background=p["accent"], bordercolor=p["canvas"],
                        lightcolor=p["accent"], darkcolor=p["accent"])

    def build_ui(self):
        main = ttk.Frame(self.root, padding=18)
        main.pack(fill="both", expand=True)

        header = ttk.Frame(main)
        header.pack(fill="x", pady=(0, 16))

        ttk.Label(
            header, text="My To-Do List", style="Title.TLabel"
        ).pack(side="left")

        ttk.Button(
            header, text="+ Add Task", command=self.open_add_dialog,
            style="Accent.TButton"
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
            card = ttk.LabelFrame(
                dashboard, text=label, padding=12, style="Card.TLabelframe"
            )
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
            "number", "title", "description", "priority", "due_date",
            "status", "created_at"
        )
        self.tree = ttk.Treeview(
            table_frame, columns=columns, show="headings",
            selectmode="browse"
        )
        self.tree.tag_configure(
            "overdue", background=self.PALETTE["overdue_bg"],
            foreground=self.PALETTE["overdue_fg"]
        )
        self.tree.tag_configure(
            "completed", background=self.PALETTE["completed_bg"],
            foreground=self.PALETTE["completed_fg"]
        )
        self.tree.tag_configure(
            "priority_high", background=self.PALETTE["high_bg"],
            foreground=self.PALETTE["high_fg"]
        )
        self.tree.tag_configure(
            "priority_low", background=self.PALETTE["low_bg"],
            foreground=self.PALETTE["low_fg"]
        )

        headings = {
            "number": "#",
            "title": "Task",
            "description": "Description",
            "priority": "Priority",
            "due_date": "Due Date",
            "status": "Status",
            "created_at": "Created",
        }
        widths = {
            "number": 40, "title": 160, "description": 160,
            "priority": 85, "due_date": 95, "status": 90,
            "created_at": 120
        }

        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(
                column, width=widths[column],
                anchor="w" if column in ("title", "description") else "center"
            )

        scrollbar = ttk.Scrollbar(
            table_frame, orient="vertical", command=self.tree.yview
        )
        self.tree.configure(yscrollcommand=scrollbar.set)
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.bind("<Button-1>", self.toggle_row_selection)
        self.root.bind("<Escape>", self.deselect_task)

        # Action buttons
        actions = ttk.Frame(main)
        actions.pack(fill="x", pady=(12, 0))

        ttk.Button(
            actions, text="View Description", command=self.view_description
        ).pack(side="left", padx=(0, 8))

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

    def view_description(self):
        task_id = self.selected_id()
        if task_id is None:
            messagebox.showwarning("Select task", "Select a task first.")
            return

        task = next(
            (t for t in database.get_tasks() if t["id"] == task_id),
            None
        )
        if task is None:
            return

        dialog = tk.Toplevel(self.root)
        dialog.title("Task Description")
        dialog.transient(self.root)
        dialog.geometry("560x400")
        dialog.minsize(420, 300)

        frame = ttk.Frame(dialog, padding=18)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text=task["title"], style="Title.TLabel").pack(
            anchor="w"
        )
        due_date = task["due_date"] or "No due date"
        ttk.Label(
            frame,
            text=f"{task['priority']} priority  ·  {due_date}",
            foreground=self.PALETTE["muted"]
        ).pack(anchor="w", pady=(4, 12))

        text_frame = ttk.Frame(frame)
        text_frame.pack(fill="both", expand=True)
        description = tk.Text(
            text_frame, wrap="word", font=("Calibri", 11),
            background=self.PALETTE["surface"],
            foreground=self.PALETTE["ink"],
            padx=12, pady=10, relief="solid", borderwidth=1,
            highlightthickness=1,
            highlightbackground=self.PALETTE["border"]
        )
        scrollbar = ttk.Scrollbar(
            text_frame, orient="vertical", command=description.yview
        )
        description.configure(yscrollcommand=scrollbar.set)
        description.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        description.insert(
            "1.0", task["description"] or "No description provided."
        )
        description.configure(state="disabled")

        ttk.Button(
            frame, text="Close", command=dialog.destroy
        ).pack(anchor="e", pady=(12, 0))

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
        description.configure(
            font=("Calibri", 11), background=self.PALETTE["surface"],
            foreground=self.PALETTE["ink"],
            insertbackground=self.PALETTE["ink"],
            selectbackground=self.PALETTE["accent"]
        )
        description.grid(row=1, column=1, sticky="nsew", pady=6)
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

        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        title_entry.focus_set()
        title_entry.bind("<Return>", lambda event: save())
        due_entry.bind("<Return>", lambda event: save())
        dialog.update_idletasks()
        width = int(dialog.winfo_reqwidth() * 1.3)
        height = int(dialog.winfo_reqheight() * 1.3)
        dialog.geometry(f"{width}x{height}")

    def selected_id(self):
        selection = self.tree.selection()
        if not selection:
            return None
        return int(selection[0])

    def toggle_row_selection(self, event):
        row_id = self.tree.identify_row(event.y)
        if row_id and row_id in self.tree.selection():
            self.tree.selection_remove(row_id)
            return "break"

    def deselect_task(self, event=None):
        selection = self.tree.selection()
        if selection:
            self.tree.selection_remove(*selection)
        return "break"

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

        for row_number, task in enumerate(tasks, start=1):
            description_words = (task["description"] or "").split()
            description_preview = " ".join(description_words[:5]) or "—"
            if len(description_words) > 5:
                description_preview += "…"

            is_overdue = (
                not task["completed"] and task["due_date"]
                and task["due_date"] < today
            )
            status = (
                "Completed" if task["completed"]
                else "Overdue" if is_overdue
                else "Pending"
            )
            priority_tag = {
                "High": "priority_high", "Low": "priority_low"
            }.get(task["priority"], "")
            if task["completed"]:
                row_tag = "completed"
            elif is_overdue:
                row_tag = "overdue"
            else:
                row_tag = priority_tag
            self.tree.insert(
                "", "end", iid=str(task["id"]),
                values=(
                    row_number, task["title"], description_preview,
                    task["priority"], task["due_date"] or "—",
                    status, task["created_at"]
                ), tags=(row_tag,) if row_tag else ()
            )


if __name__ == "__main__":
    database.initialize_db()
    root = tk.Tk()
    app = OrbitApp(root)
    root.mainloop()
