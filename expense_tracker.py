import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from ttkthemes import ThemedTk

class ExpenseTrackerApp:
    def __init__(self, master):
        self.master = master
        master.title("Expense Tracker")
        master.geometry("360x640")  # Set window dimensions similar to a mobile phone

        self.expense_tracker = ExpenseTracker()

        self.style = ttk.Style(master)
        self.style.theme_use("equilux")  # Set the theme to "equilux" (dark theme)

        # Custom styling
        self.style.configure('.', background='#292929', foreground='white')  # Set background to dark gray and text to white
        self.style.configure('TLabel', font=('Arial', 14))  # Set font for labels
        self.style.map('TButton', background=[('active', '#0078d7')])  # Set button color on active state

        self.notebook = ttk.Notebook(master)
        self.notebook.pack(fill='both', expand=True)

        self.add_expense_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.add_expense_frame, text='Add Expense')

        self.view_expenses_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.view_expenses_frame, text='View Expenses')

        self.total_expenses_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.total_expenses_frame, text='Total Expenses')

        self.create_add_expense_frame()
        self.create_view_expenses_frame()
        self.create_total_expenses_frame()

        # Load expenses from file
        self.load_expenses()

    def create_add_expense_frame(self):
        label = ttk.Label(self.add_expense_frame, text="Add Expense")
        label.pack(pady=10)

        description_label = ttk.Label(self.add_expense_frame, text="Description:")
        description_label.pack()
        self.description_entry = ttk.Entry(self.add_expense_frame)
        self.description_entry.pack()

        amount_label = ttk.Label(self.add_expense_frame, text="Amount:")
        amount_label.pack()
        self.amount_entry = ttk.Entry(self.add_expense_frame)
        self.amount_entry.pack()

        submit_button = ttk.Button(self.add_expense_frame, text="Submit", command=self.add_expense)
        submit_button.pack(pady=10)

    def create_view_expenses_frame(self):
        label = ttk.Label(self.view_expenses_frame, text="View Expenses")
        label.pack(pady=10)

        self.text = tk.Text(self.view_expenses_frame, background='#292929', foreground='white')
        self.text.pack(fill='both', expand=True)

        scrollbar = ttk.Scrollbar(self.view_expenses_frame, orient=tk.VERTICAL, command=self.text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.text.config(yscrollcommand=scrollbar.set)

        self.display_expenses()

        # Add buttons for downloading and copying expenses
        download_button = ttk.Button(self.view_expenses_frame, text="Download Expenses (PDF)", command=self.download_expenses_pdf)
        download_button.pack(pady=5)

        copy_button = ttk.Button(self.view_expenses_frame, text="Copy Expenses", command=self.copy_expenses)
        copy_button.pack(pady=5)

    def create_total_expenses_frame(self):
        label = ttk.Label(self.total_expenses_frame, text="Total Expenses")
        label.pack(pady=10)

        self.total_text = tk.Text(self.total_expenses_frame, background='#292929', foreground='white')
        self.total_text.pack(fill='both', expand=True)

        self.display_total()

    def add_expense(self):
        description = self.description_entry.get()
        amount = float(self.amount_entry.get())
        self.expense_tracker.add_expense(description, amount)
        self.display_expenses()
        self.display_total()
        self.save_expenses()  # Save expenses to file after adding

        # Clear the entry fields after submitting
        self.description_entry.delete(0, tk.END)
        self.amount_entry.delete(0, tk.END)

    def display_expenses(self):
        self.text.delete("1.0", tk.END)
        for index, expense in enumerate(self.expense_tracker.get_expenses(), start=1):
            self.text.insert(tk.END, f"{index}. {expense['description']}: ${expense['amount']:.2f}\n")
             # Add a delete button for each expense
            delete_button = ttk.Button(self.view_expenses_frame, text="Delete", command=lambda i=index: self.delete_expense(i))
            self.text.window_create(tk.END, window=delete_button)
            self.text.insert(tk.END, "\n")
            
    def display_total(self):
        total = self.expense_tracker.calculate_total()
        self.total_text.delete("1.0", tk.END)
        self.total_text.insert(tk.END, f"Total Expenses: ${total:.2f}")

    def save_expenses(self):
        with open("expenses.json", "w") as f:
            json.dump(self.expense_tracker.get_expenses(), f)

    def load_expenses(self):
        try:
            with open("expenses.json", "r") as f:
                expenses = json.load(f)
                for expense in expenses:
                    self.expense_tracker.add_expense(expense['description'], expense['amount'])
                self.display_expenses()
                self.display_total()
        except FileNotFoundError:
            pass  # If file not found, do nothing
    
    def delete_expense(self, index):
        self.expense_tracker.delete_expense(index)
        self.display_expenses()
        self.display_total()
        self.save_expenses()  # Save expenses to file after deleting

    def download_expenses_pdf(self):
        # Get all expenses as a string
        all_expenses = "\n".join(f"{index}. {expense['description']}: ${expense['amount']:.2f}" for index, expense in enumerate(self.expense_tracker.get_expenses(), start=1))

        # Add total expenses
        total_expenses = f"\n\nTotal Expenses: ${self.expense_tracker.calculate_total():.2f}"
        all_expenses += total_expenses

        # Prompt user to choose location to save the PDF
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if file_path:
            # Create a PDF document
            c = canvas.Canvas(file_path, pagesize=letter)
            text = c.beginText(100, 750)
            text.setFont("Helvetica", 12)
            text.textLines(all_expenses)
            c.drawText(text)
            c.save()
            messagebox.showinfo("Download Expenses (PDF)", "Expenses saved to PDF successfully.")

    def copy_expenses(self):
        # Get all expenses as a string
        all_expenses = "\n".join(f"{index}. {expense['description']}: ${expense['amount']:.2f}" for index, expense in enumerate(self.expense_tracker.get_expenses(), start=1))

        # Add total expenses
        total_expenses = f"\n\nTotal Expenses: ${self.expense_tracker.calculate_total():.2f}"
        all_expenses += total_expenses

        # Copy expenses to clipboard
        self.master.clipboard_clear()
        self.master.clipboard_append(all_expenses)
        messagebox.showinfo("Copy Expenses", "Expenses copied to clipboard.")


class ExpenseTracker:
    def __init__(self):
        self.expenses = []

    def add_expense(self, description, amount):
        self.expenses.append({"description": description, "amount": amount})

    def get_expenses(self):
        return self.expenses

    def calculate_total(self):
        return sum(expense['amount'] for expense in self.expenses)
    
    def delete_expense(self, index):
        del self.expenses[index - 1]  # Subtract 1 because index starts from 1 in the display

def main():
    root = ThemedTk(theme="equilux")
    app = ExpenseTrackerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
