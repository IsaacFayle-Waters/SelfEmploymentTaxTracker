import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import date
import os

CSV_FILE = "income_total2.csv"

class FinanceApp:
    """
    Main App Class

    """
    def __init__(self, root):
        self.root = root
        self.root.title("Finance Tracker For Self-Employment")

        self.columns = ["Amount", "Date", "Source"]
        self.df = self.load_data(CSV_FILE)
        #Get tax year pairs present in CSV file
        #tax_year_list = sorted(set(i.year for i in self.df.Date))
        #self.tax_years = ["All"] + [f"{tax_year_list[i]}/{tax_year_list[i + 1]}" for i in range(len(tax_year_list) - 1)]
        self.get_tax_years(self.df)

        self.create_widgets()
        self.populate_table_all()

    def load_data(self,CSV_FILE):
        """
        Loads data from CSV FILE.

        TODO: ADAPT FOR CHOOSING USER FILES

        """
        if os.path.exists(CSV_FILE):
            df = pd.read_csv(CSV_FILE)
            if set(self.columns).issubset(df.columns):
                #Convert to datetime
                df['Date'] = pd.to_datetime(df['Date'], format='%d/%m/%y',errors='coerce')
                return df[self.columns]
            else:
                messagebox.showerror("Error", f"{CSV_FILE} has incorrect columns.")
                return pd.DataFrame(columns=self.columns)
        else:
            return pd.DataFrame(columns=self.columns)

    def save_data(self):
        self.df.to_csv(CSV_FILE, index=False)

    def create_widgets(self):
        """
        Initialize widgets. I.e. Buttons, tables, etc.

        """
        self.frame = tk.Frame(self.root)
        self.frame.pack(pady=10)

        #Adding new data
        '''self.fields = {}
        for idx, label in enumerate(["Amount", "Date (YYYY-MM-DD)", "Source"]):
            tk.Label(frame, text=label).grid(row=0, column=idx)
            entry = tk.Entry(frame, width=20)
            entry.grid(row=1, column=idx, padx=5)
            self.fields[label] = entry

        self.fields["Date (YYYY-MM-DD)"].insert(0, date.today().isoformat())'''

        #Buttons
        #tk.Button(frame, text="Add Entry", command=self.add_entry).grid(row=1, column=3, padx=10)
        tk.Button(self.frame, text="Load CSV: Income", command=self.select_file).grid(row=0, column=4)#pady=10)
        
        #Dropdown
        self.create_load_dropdown()
        
        #Main table
        self.tree = ttk.Treeview(self.root, columns=self.columns, show="headings")
        for col in self.columns:
            self.tree.heading(col, text=col.capitalize())
            self.tree.column(col, width=150)
        self.tree.pack(pady=10, fill="both", expand=True)

        self.create_summary_table()
        
    def populate_table_all(self):
        """
        Initialises main table.

        """
        for row in self.tree.get_children():
            self.tree.delete(row)  # Clear any existing rows

        for row in self.df.itertuples(index=False):
            self.tree.insert("", "end", values=row)

    def populate_table_by_tax_year(self,df):
        """
        Populates the main table according to the specific tax year selection.

        Args:
            df(DataFrame)

        """
        for row in self.tree.get_children():
            self.tree.delete(row) #Clear rows

        for row in df.itertuples(index=False):
            self.tree.insert("","end",values=row) 
    
    def create_summary_table(self):
        """
        Creates a seperate table for total summations.

        """
        self.summary_tree = ttk.Treeview(self.root, columns=("label", "value"), show="headings", height=3)
        self.summary_tree.heading("label", text="Summary")
        self.summary_tree.heading("value", text="Amount")
        self.summary_tree.column("label", width=200)
        self.summary_tree.column("value", width=150)
        self.summary_tree.pack(pady=(0, 10), fill="x")

    def update_summary(self,df):
        """
        Populates and updates summary table.

        Args:
            df(DataFrame)
        """
        for row in self.summary_tree.get_children():
            self.summary_tree.delete(row)

        total_income = df['Amount'].sum()
        #other_stuff = 35096
        summary_data = [
            ("Total Income", f"£{total_income:,.2f}"),
            #("Other stuff", f"£{other_stuff:,.2f}") 

        ]

        for key, value in summary_data:
            self.summary_tree.insert("","end",values=(key,value))

    def get_tax_years(self,df):
        tax_year_list = sorted(set(i.year for i in self.df.Date))
        self.tax_years = ["All"] + [f"{tax_year_list[i]}/{tax_year_list[i + 1]}" for i in range(len(tax_year_list) - 1)]

    def create_load_dropdown(self):
        """
        Creates and loads the dropdown tax year selector.

        Args:
            frame(Frame)
        """
        self.view_option = tk.StringVar(value="Tax Year")
        #tk.Label(frame,text="View Tax Year: ").grid(row=0,column=0,sticky="e")
        self.option_menu = tk.OptionMenu(self.frame,self.view_option,*self.tax_years, command=self.on_view_change_main)
        self.option_menu.grid(row=0, column=1, sticky="w") 

    def update_dropdown(self):
        # Clear existing options from the OptionMenu's menu
        self.option_menu['menu'].delete(0, 'end')

        # Repopulate the menu with updated tax_years
        for year in self.tax_years:
            self.option_menu['menu'].add_command(
                label=year,
                command=lambda value=year: self.on_view_change_main(value)
            )

        # Reset the selected value
        self.view_option.set("Tax Year")
  

    def on_view_change_main(self, selection):
        """
        This function filters the contents of the main table based on 
        the selected tax year, which is supplied by the dropdown menu.
        Also updates summary table with relevent data.

        Args:
            selection(str)

        """
        if selection == "All":
            
            filtered_df = self.df
            
        elif "/" in selection:#Extract start and end dates of UK tax year
            first_year,second_year = selection.split('/')
            start_date = pd.Timestamp(f'{first_year}-04-06')
            end_date = pd.Timestamp(f'{second_year}-04-05')
            #print(start_date)
            #print(end_date)
            #Filter data based on tax year
            filtered_df = self.df[(self.df['Date'] >= start_date) & (self.df['Date'] <= end_date)]
        else:
            filtered_df = self.df

        self.populate_table_by_tax_year(filtered_df)
        self.update_summary(filtered_df)

    def select_file(self):
        file_path = filedialog.askopenfilename(
            title="Open CSV file",
            filetypes=[("CSV files", "*.csv")]
        )
        if file_path:
            self.df = self.load_data(file_path)
            self.get_tax_years(self.df)
            self.update_dropdown()
            self.populate_table_all()
            
            self.update_summary(self.df)


    #Add new enties #AS YET UNEXAMINED CODE FROM CHATBOT
    def add_entry(self):
        values = [self.fields["Amount"].get().strip(),
                  self.fields["Date (YYYY-MM-DD)"].get().strip(),
                  self.fields["Source"].get().strip()]

        if not all(values):
            messagebox.showerror("Error", "Please fill in all fields.")
            return

        try:
            amount = float(values[0])  # Validate amount
        except ValueError:
            messagebox.showerror("Error", "Amount must be a number.")
            return

        new_entry = pd.DataFrame([{
            "Amount": amount,
            "Date": values[1],
            "Source": values[2]
        }])

        self.df = pd.concat([self.df, new_entry], ignore_index=True)
        self.save_data()

        self.tree.insert("", "end", values=[amount, values[1], values[2]])

        for entry in self.fields.values():
            entry.delete(0, tk.END)
        self.fields["Date (YYYY-MM-DD)"].insert(0, date.today().isoformat())

if __name__ == "__main__":
    root = tk.Tk()
    app = FinanceApp(root)
    root.mainloop()
