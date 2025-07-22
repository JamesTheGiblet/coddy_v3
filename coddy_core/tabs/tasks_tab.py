import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import os
import re
import threading
from .. import subscription

class TasksTab(tk.Frame):
    """
    The UI for the Tasks tab, which visually displays the project roadmap.
    """
    def __init__(self, master, colors, app_logic, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.colors = colors
        self.app_logic = app_logic # MainApplication instance
        self.config(bg=self.colors['bg'])
        self.roadmap_data = []
        self.roadmap_preamble = ""

        self._create_widgets()
        self.load_and_display_roadmap()

    def _create_widgets(self):
        """Creates the main widgets for the tab."""
        # Main frame with a scrollbar
        main_frame = tk.Frame(self, bg=self.colors['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(main_frame, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas, bg=self.colors['bg'])

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Container for the actual roadmap content
        self.tasks_container = tk.Frame(self.scrollable_frame, bg=self.colors['bg'])
        self.tasks_container.pack(fill='both', expand=True, padx=20, pady=10)

        # Bottom frame for action buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        self.autoplan_button = ttk.Button(button_frame, text="🤖 Auto-plan New Roadmap", command=self.auto_plan_roadmap)
        self.autoplan_button.pack(side="left", padx=(0, 5))

        self.summarize_button = ttk.Button(button_frame, text="📝 Summarize Session", command=self.get_ai_summary)
        self.summarize_button.pack(side="right")

    def load_and_display_roadmap(self):
        """Loads roadmap.md, parses it, and displays it."""
        for widget in self.tasks_container.winfo_children():
            widget.destroy()

        roadmap_path = os.path.join(self.app_logic.project_path, "roadmap.md")
        if not os.path.exists(roadmap_path):
            tk.Label(self.tasks_container, text="roadmap.md not found in project.", bg=self.colors['bg'], fg=self.colors['fg']).pack()
            return

        try:
            with open(roadmap_path, 'r', encoding='utf-8') as f:
                content = f.read()
            self.roadmap_preamble, self.roadmap_data = self._parse_roadmap(content)
            self._render_roadmap()
        except Exception as e:
            tk.Label(self.tasks_container, text=f"Error reading roadmap.md:\n{e}", bg=self.colors['bg'], fg=self.colors['fg']).pack()

    def _parse_roadmap(self, content):
        """Parses the markdown content into a preamble and a structured list of phases."""
        preamble_lines = []
        phases = []
        current_phase = None
        task_regex = re.compile(r"-\s*\[([x\s])\]\s*(.*)")
        in_preamble = True

        for line in content.splitlines():
            stripped_line = line.strip()
            if stripped_line.startswith("### Phase"):
                in_preamble = False
                if current_phase:
                    phases.append(current_phase)
                current_phase = {"title": stripped_line.replace("###", "").strip(), "tasks": []}
            elif in_preamble:
                preamble_lines.append(line)
            elif stripped_line.startswith("- [") and current_phase:
                match = task_regex.match(stripped_line)
                if match:
                    completed = match.group(1).lower() == 'x'
                    task_text = match.group(2).strip()
                    current_phase["tasks"].append({"text": task_text, "completed": completed})
        
        if current_phase:
            phases.append(current_phase)
        
        return "\n".join(preamble_lines), phases

    def _render_roadmap(self):
        """Renders the parsed roadmap data into the UI."""
        # Clear existing widgets before re-rendering
        for widget in self.tasks_container.winfo_children():
            widget.destroy()

        for phase_idx, phase in enumerate(self.roadmap_data):
            phase_label = tk.Label(self.tasks_container, text=phase['title'], font=("Segoe UI", 16, "bold"), bg=self.colors['bg'], fg=self.colors['accent'])
            phase_label.pack(anchor='w', pady=(20, 10))

            for task_idx, task in enumerate(phase['tasks']):
                task_frame = ttk.Frame(self.tasks_container)
                task_frame.pack(fill='x', padx=20, pady=2)

                var = tk.BooleanVar(value=task['completed'])
                check = ttk.Checkbutton(
                    task_frame,
                    variable=var,
                    text=task['text'],
                    command=lambda p_idx=phase_idx, t_idx=task_idx: self._on_task_toggle(p_idx, t_idx)
                )
                check.pack(side='left', anchor='w')

                gen_button = ttk.Button(
                    task_frame, text="⚡ Gen Code",
                    command=lambda t=task['text']: self._on_generate_code_for_task(t)
                )
                gen_button.pack(side='right', anchor='e')

                # Disable button if user doesn't have the required feature
                if not subscription.is_feature_enabled(self.app_logic.active_tier, subscription.Feature.AI_SUGGESTION):
                    gen_button.config(state="disabled")

    def _on_task_toggle(self, phase_index, task_index):
        """Called when a task checkbox is toggled. Updates data and saves the file."""
        task = self.roadmap_data[phase_index]['tasks'][task_index]
        task['completed'] = not task['completed']
        self._save_roadmap_to_file()

    def _on_generate_code_for_task(self, task_text):
        """Primes the Edit tab with the selected task."""
        self.app_logic.execute_code_generation_for_task(task_text)

    def complete_task_by_text(self, task_text_to_complete):
        """Finds a task by its text and marks it as complete."""
        task_found = False
        for phase in self.roadmap_data:
            for task in phase['tasks']:
                if task['text'] == task_text_to_complete:
                    task['completed'] = True
                    task_found = True
                    break
            if task_found:
                self._save_roadmap_to_file()
                self._render_roadmap()
                break

    def _get_roadmap_content_as_string(self):
        """Constructs the full roadmap markdown content from the internal data structure."""
        output_str = ""
        if self.roadmap_preamble:
            output_str += self.roadmap_preamble.strip() + "\n\n"
        for i, phase in enumerate(self.roadmap_data):
            output_str += f"### {phase['title']}\n"
            for task in phase['tasks']:
                checkbox = "[x]" if task['completed'] else "[ ]"
                output_str += f"- {checkbox} {task['text']}\n"
            if i < len(self.roadmap_data) - 1:
                output_str += "\n"
        return output_str

    def _save_roadmap_to_file(self):
        """Writes the current state of the roadmap back to roadmap.md."""
        roadmap_path = os.path.join(self.app_logic.project_path, "roadmap.md")
        content_to_save = self._get_roadmap_content_as_string()
        try:
            with open(roadmap_path, 'w', encoding='utf-8') as f:
                f.write(content_to_save)
        except Exception as e:
            print(f"Error saving roadmap.md: {e}")
            messagebox.showerror("Save Error", f"Could not save roadmap.md:\n{e}")

    def _toggle_buttons(self, enabled):
        """Helper to enable/disable action buttons."""
        state = "normal" if enabled else "disabled"
        self.autoplan_button.config(state=state)
        self.summarize_button.config(state=state)

    def auto_plan_roadmap(self):
        """Handles the 'Auto-plan New Roadmap' button click."""
        if not subscription.is_feature_enabled(self.app_logic.active_tier, subscription.Feature.AUTO_TASK_PLANNING):
            messagebox.showinfo(
                "Upgrade Required",
                f"The 'Auto-plan' feature is available for {subscription.SubscriptionTier.VISIONARY.value}+ subscribers.\n\n"
                f"You can change your tier in the Settings tab for testing."
            )
            return

        if not messagebox.askyesno("Confirm Overwrite", "This will generate a new roadmap and overwrite your existing roadmap.md file. Are you sure you want to continue?"):
            return

        project_goal = simpledialog.askstring("New Roadmap Goal", "Describe your project goal in one or two sentences:", parent=self)

        if not project_goal or not project_goal.strip():
            return # User cancelled or entered nothing

        self._toggle_buttons(enabled=False)
        threading.Thread(target=self._run_ai_autoplan_thread, args=(project_goal,), daemon=True).start()

    def _run_ai_autoplan_thread(self, project_goal):
        """Worker thread to call the AI for auto-planning."""
        try:
            new_roadmap_content = self.app_logic.ai_engine.get_auto_planned_roadmap(project_goal)
            self.after(0, self._handle_autoplan_result, new_roadmap_content)
        except Exception as e:
            self.after(0, messagebox.showerror, "AI Error", f"An error occurred during auto-planning:\n{e}")
        finally:
            self.after(0, self._toggle_buttons, True)

    def _handle_autoplan_result(self, new_content):
        """Saves the new roadmap and refreshes the UI."""
        if new_content:
            self.app_logic.save_roadmap(new_content)
            self.load_and_display_roadmap()
            messagebox.showinfo("Success", "New roadmap has been generated and saved!")
        else:
            messagebox.showwarning("AI Response", "The AI returned an empty roadmap. Please try again.")

    def get_ai_summary(self):
        """Handles the 'Summarize Session' button click."""
        if not subscription.is_feature_enabled(self.app_logic.active_tier, subscription.Feature.AI_SESSION_SUMMARY):
            messagebox.showinfo(
                "Upgrade Required",
                f"The 'AI Summary' feature is available for {subscription.SubscriptionTier.ARCHITECT.value}+ subscribers.\n\n"
                f"You can change your tier in the Settings tab for testing."
            )
            return

        self._toggle_buttons(enabled=False)
        roadmap_content = self._get_roadmap_content_as_string()
        threading.Thread(target=self._run_ai_summary_thread, args=(roadmap_content,), daemon=True).start()

    def _run_ai_summary_thread(self, roadmap_content):
        """Worker thread to call the AI and display the result."""
        try:
            summary = self.app_logic.ai_engine.get_session_summary(roadmap_content)
            self.after(0, messagebox.showinfo, "Session Summary", summary)
        except Exception as e:
            self.after(0, messagebox.showerror, "AI Error", f"An error occurred while generating the summary:\n{e}")
        finally:
            self.after(0, self._toggle_buttons, True)

    def apply_colors(self, colors):
        """Applies a new color theme."""
        self.colors = colors
        self.config(bg=colors['bg'])
        # Re-render with new colors
        self.load_and_display_roadmap()
