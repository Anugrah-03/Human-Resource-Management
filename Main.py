import customtkinter as ctk
from tkinter import messagebox, StringVar, Text, Scrollbar, END
from tkinter.ttk import Treeview
import psycopg2

# PostgreSQL database configuration
DB_CONFIG = {
    "dbname": "HumanResourceManagement",
    "user": "postgres",
    "password": "postgres",
    "host": "127.0.0.1",
    "port": "5432",
}

# Define the table schemas as a dictionary
tables = {
    "Address": [
        ("AddressID", "SERIAL PRIMARY KEY"),
        ("Street", "VARCHAR(255)"),
        ("City", "VARCHAR(100)"),
        ("ZipCode", "VARCHAR(20)"),
        ("Country", "VARCHAR(50)"),
    ],
    "Employee": [
        ("EmployeeID", "SERIAL PRIMARY KEY"),
        ("FirstName", "VARCHAR(100)"),
        ("LastName", "VARCHAR(100)"),
        ("DateOfBirth", "DATE"),
        ("Gender", "VARCHAR(10)"),
        ("HireDate", "DATE"),
        ("Salary", "DECIMAL(10, 2)"),
        ("ContactNumber", "VARCHAR(20)"),
        ("Email", "VARCHAR(100)"),
        ("AddressID", "INT"),
    ],
    "Manager": [("EmployeeID", "SERIAL PRIMARY KEY"), ("TeamSize", "INT")],
    "NonManager": [
        ("EmployeeID", "SERIAL PRIMARY KEY"),
        ("Shift", "VARCHAR(20)"),
        ("ManagerID", "INT"),
    ],
    "Review": [
        ("ReviewID", "SERIAL PRIMARY KEY"),
        ("EmployeeID", "INT"),
        ("ReviewDate", "DATE"),
        ("Rating", "INT"),
        ("Comments", "TEXT"),
    ],
    "Training": [
        ("TrainingID", "SERIAL PRIMARY KEY"),
        ("TrainingName", "VARCHAR(100)"),
        ("TrainingDescription", "TEXT"),
        ("StartDate", "DATE"),
        ("EndDate", "DATE"),
    ],
    "EmployeeTraining": [
        ("EmployeeID", "INT"),
        ("TrainingID", "INT"),
        "PRIMARY KEY(EmployeeID, TrainingID)",
    ],
    "Job": [
        ("JobID", "SERIAL PRIMARY KEY"),
        ("JobTitle", "VARCHAR(100)"),
        ("JobDescription", "TEXT"),
        ("JobMinSalary", "DECIMAL(10, 2)"),
        ("JobMaxSalary", "DECIMAL(10, 2)"),
    ],
    "EmployeeJob": [
        ("EmployeeID", "INT"),
        ("JobID", "INT"),
        "PRIMARY KEY(EmployeeID, JobID)",
    ],
    "Department": [
        ("DepartmentID", "SERIAL PRIMARY KEY"),
        ("DepartmentName", "VARCHAR(100)"),
    ],
    "EmployeeDepartment": [
        ("EmployeeID", "INT"),
        ("DepartmentID", "INT"),
        "PRIMARY KEY(EmployeeID, DepartmentID)",
    ],
    "Project": [
        ("ProjectID", "SERIAL PRIMARY KEY"),
        ("ProjectName", "VARCHAR(100)"),
        ("ProjectStartDate", "DATE"),
        ("ProjectEndDate", "DATE"),
        ("ProjectBudget", "DECIMAL(15, 2)"),
    ],
    "EmployeeProject": [
        ("EmployeeID", "INT"),
        ("ProjectID", "INT"),
        "PRIMARY KEY(EmployeeID, ProjectID)",
    ],
}


class HRManagementApp:
    def init(self, root):
        self.root = root
        self.root.title("Human Resource Management System")
        ctk.set_appearance_mode("light")  # Modes: system (default), light, dark
        ctk.set_default_color_theme("blue")  # Themes: blue (default), dark-blue, green

        # Define styles
        self.style = {
            "font": ("Helvetica", 12),
            "bg_color": "#f2f2f2",
            "btn_color": "#4CAF50",
            "btn_font": ("Helvetica", 12, "bold"),
            "label_font": ("Helvetica", 12, "bold"),
            "entry_font": ("Helvetica", 12),
        }

        # Create the main frames
        self.left_frame = ctk.CTkFrame(root, width=200, height=600)
        self.left_frame.pack(side="left", fill="y")

        self.right_frame = ctk.CTkFrame(root, width=600, height=600)
        self.right_frame.pack(side="right", fill="both", expand=True)

        # Right frame - top section for table selection
        self.top_right_frame = ctk.CTkFrame(self.right_frame)
        self.top_right_frame.pack(side="top", fill="x")

        # Right frame - middle section for form
        self.form_frame = ctk.CTkFrame(self.right_frame)
        self.form_frame.pack(side="top", fill="both", expand=True, pady=20)

        # Right frame - bottom section for displaying results
        self.bottom_right_frame = ctk.CTkFrame(self.right_frame)
        self.bottom_right_frame.pack(side="bottom", fill="both", expand=True)

        # Connect to PostgreSQL database
        try:
            self.conn = psycopg2.connect(
                dbname=DB_CONFIG["dbname"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                host=DB_CONFIG["host"],
                port=DB_CONFIG["port"],
            )
            self.cursor = self.conn.cursor()
            print("Connected to PostgreSQL database.")
        except psycopg2.Error as e:
            messagebox.showerror(
                "Database Connection Error",
                f"Error connecting to PostgreSQL database:\n{str(e)}",
            )
            root.quit()

        # Left frame widgets
        ctk.CTkLabel(
            self.left_frame,
            text="CRUD Operations",
            font=self.style["label_font"],
        ).pack(pady=10)

        button_width = 15  # Set the width for all buttons
        button_padding = {"padx": 10, "pady": 10}  # Set padding for all buttons

        self.create_btn = ctk.CTkButton(
            self.left_frame,
            text="Create",
            width=button_width,
            command=self.create_record,
            fg_color=self.style["btn_color"],
            font=self.style["btn_font"],
        )
        self.create_btn.pack(**button_padding)

        self.read_btn = ctk.CTkButton(
            self.left_frame,
            text="Read",
            width=button_width,
            command=self.read_record,
            fg_color=self.style["btn_color"],
            font=self.style["btn_font"],
        )
        self.read_btn.pack(**button_padding)

        self.update_btn = ctk.CTkButton(
            self.left_frame,
            text="Update",
            width=button_width,
            command=self.update_record,
            fg_color=self.style["btn_color"],
            font=self.style["btn_font"],
        )
        self.update_btn.pack(**button_padding)

        self.delete_btn = ctk.CTkButton(
            self.left_frame,
            text="Delete",
            width=button_width,
            command=self.delete_record,
            fg_color=self.style["btn_color"],
            font=self.style["btn_font"],
        )
        self.delete_btn.pack(**button_padding)

        self.advanced_btn = ctk.CTkButton(
            self.left_frame,
            text="Advanced Options",
            width=button_width,
            command=self.show_advanced_options,
            fg_color=self.style["btn_color"],
            font=self.style["btn_font"],
        )
        self.advanced_btn.pack(**button_padding)

        # Top right frame widgets
        self.table_selection = StringVar()
        self.table_selection.set("Select Table")

        self.table_label = ctk.CTkLabel(
            self.top_right_frame,
            text="Select Table",
            font=self.style["label_font"],
        )
        self.table_label.pack(pady=10)

        self.table_menu = ctk.CTkOptionMenu(
            self.top_right_frame,
            variable=self.table_selection,
            values=list(tables.keys()),
            command=self.display_table_fields,
        )
        self.table_menu.pack(pady=10)

        # Bottom right frame widgets for displaying results
        self.tree = Treeview(
            self.bottom_right_frame,
            columns=[column[0] for column in tables["Employee"]],
            show="headings",
        )
        self.tree.pack(side="left", fill="both", expand=True)

        self.scrollbar = Scrollbar(
            self.bottom_right_frame, orient="vertical", command=self.tree.yview
        )
        self.scrollbar.pack(side="right", fill="y")
        self.tree.config(yscrollcommand=self.scrollbar.set)

        for column in tables["Employee"]:
            self.tree.heading(column[0], text=column[0])
            self.tree.column(column[0], width=100)

    def clear_form_frame(self):
        for widget in self.form_frame.winfo_children():
            widget.destroy()

    def display_table_fields(self, selected_table):
        self.clear_form_frame()  # Clear previous form fields

        if selected_table == "Select Table":
            return

        self.entries = {}
        for i, (column, column_type) in enumerate(tables[selected_table]):
            ctk.CTkLabel(
                self.form_frame, text=column, font=self.style["label_font"]
            ).grid(row=i, column=0, pady=5, padx=5, sticky="e")
            entry = ctk.CTkEntry(self.form_frame, font=self.style["entry_font"])
            entry.grid(row=i, column=1, pady=5, padx=5, sticky="w")
            self.entries[column] = entry

        # Update Treeview columns based on the selected table
        self.tree["columns"] = [column[0] for column in tables[selected_table]]
        for column in self.tree["columns"]:
            self.tree.heading(column, text=column)
            self.tree.column(column, width=100)

        # Clear existing treeview items
        for item in self.tree.get_children():
            self.tree.delete(item)

    def get_form_data(self):
        return {column: entry.get() for column, entry in self.entries.items()}

    def create_record(self):
        selected_table = self.table_selection.get()
        if selected_table == "Select Table":
            messagebox.showerror("Error", "Please select a table.")
            return

        data = self.get_form_data()
        columns = ", ".join(data.keys())
        values = ", ".join(f"'{value}'" for value in data.values())

        query = f"INSERT INTO {selected_table} ({columns}) VALUES ({values})"
        try:
            self.cursor.execute(query)
            self.conn.commit()
            messagebox.showinfo("Success", "Record created successfully.")
        except psycopg2.Error as e:
            messagebox.showerror("Error", f"Error creating record:\n{str(e)}")
            self.conn.rollback()

    def read_record(self):
        selected_table = self.table_selection.get()
        if selected_table == "Select Table":
            messagebox.showerror("Error", "Please select a table.")
            return

        query = f"SELECT * FROM {selected_table}"
        try:
            self.cursor.execute(query)
            records = self.cursor.fetchall()

            # Clear existing treeview items
            for item in self.tree.get_children():
                self.tree.delete(item)

            for record in records:
                self.tree.insert("", "end", values=record)
        except psycopg2.Error as e:
            messagebox.showerror("Error", f"Error reading records:\n{str(e)}")

    def update_record(self):
        selected_table = self.table_selection.get()
        if selected_table == "Select Table":
            messagebox.showerror("Error", "Please select a table.")
            return

        data = self.get_form_data()
        set_clause = ", ".join(
            f"{column} = '{value}'" for column, value in data.items()
        )
        primary_key_column = tables[selected_table][0][0]
        primary_key_value = data[primary_key_column]

        query = f"UPDATE {selected_table} SET {set_clause} WHERE {primary_key_column} = {primary_key_value}"
        try:
            self.cursor.execute(query)
            self.conn.commit()
            messagebox.showinfo("Success", "Record updated successfully.")
        except psycopg2.Error as e:
            messagebox.showerror("Error", f"Error updating record:\n{str(e)}")
            self.conn.rollback()

    def delete_record(self):
        selected_table = self.table_selection.get()
        if selected_table == "Select Table":
            messagebox.showerror("Error", "Please select a table.")
            return

        data = self.get_form_data()
        primary_key_column = tables[selected_table][0][0]
        primary_key_value = data[primary_key_column]

        query = f"DELETE FROM {selected_table} WHERE {primary_key_column} = {primary_key_value}"
        try:
            self.cursor.execute(query)
            self.conn.commit()
            messagebox.showinfo("Success", "Record deleted successfully.")
        except psycopg2.Error as e:
            messagebox.showerror("Error", f"Error deleting record:\n{str(e)}")
            self.conn.rollback()

    def show_advanced_options(self):
        self.advanced_window = ctk.CTkToplevel(self.root)
        self.advanced_window.title("Advanced Options")

        self.query_label = ctk.CTkLabel(
            self.advanced_window,
            text="Enter your SQL query:",
            font=self.style["label_font"],
        )
        self.query_label.pack(pady=10)

        self.query_text = Text(
            self.advanced_window, height=10, font=self.style["entry_font"]
        )
        self.query_text.pack(pady=10)

        self.execute_query_btn = ctk.CTkButton(
            self.advanced_window,
            text="Execute Query",
            command=self.execute_query,
            fg_color=self.style["btn_color"],
            font=self.style["btn_font"],
        )
        self.execute_query_btn.pack(pady=10)

        self.result_text = Text(
            self.advanced_window, height=10, font=self.style["entry_font"]
        )
        self.result_text.pack(pady=10)

    def execute_sql_query(self, query):
        try:
            self.cursor.execute(query)
            self.conn.commit()
            if query.strip().upper().startswith("SELECT"):
                return self.cursor.fetchall()
            return True
        except psycopg2.Error as e:
            self.conn.rollback()
            self.result_text.insert(END, f"Error executing query:\n{str(e)}\n")
            return False

    def execute_query(self):
        query = self.query_text.get("1.0", END).strip()
        if not query:
            messagebox.showerror("Error", "Query cannot be empty")
            return

        self.result_text.insert(END, f"Executing query: {query}\n")
        results = self.execute_sql_query(query)
        if results is not False:
            self.result_text.insert(END, "Query executed successfully.\n")
            if isinstance(results, list):
                # Display results in the treeview
                if results:
                    columns = [desc[0] for desc in self.cursor.description]
                    self.tree["columns"] = columns
                    for column in columns:
                        self.tree.heading(column, text=column)
                        self.tree.column(column, width=100)

                    # Clear existing treeview items
                    for item in self.tree.get_children():
                        self.tree.delete(item)

                    # Insert fetched records into the treeview
                    for row in results:
                        self.tree.insert("", "end", values=row)
                else:
                    self.result_text.insert(END, "No results found.\n")


if name == "main":
    root = ctk.CTk()
    app = HRManagementApp(root)
    root.mainloop()