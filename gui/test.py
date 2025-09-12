from tkinter import N, W, E, S, StringVar, Tk
from tkinter import ttk


def calculate() -> None:
    """Convert feet to meters and update the meters StringVar."""
    try:
        value: float = float(feet.get())
        meters.set(str(round(value * 0.3048, 4)))  # round to 4 decimal places
    except ValueError:
        meters.set("")  # clear meters if input is invalid


# Create main window
root: Tk = Tk()
root.title("Feet to Meters")

# Create main frame with padding
mainframe: ttk.Frame = ttk.Frame(master=root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=N + W + E + S)

# Make the grid expandable
root.columnconfigure(index=0, weight=1)
root.rowconfigure(index=0, weight=1)

# Input variable
feet: StringVar = StringVar()
feet_entry: ttk.Entry = ttk.Entry(master=mainframe, width=7, textvariable=feet)
feet_entry.grid(column=2, row=1, sticky=W + E)

# Output variable
meters: StringVar = StringVar()
ttk.Label(master=mainframe, textvariable=meters).grid(column=2, row=2, sticky=W + E)

# Buttons and labels
ttk.Button(master=mainframe, text="Calculate", command=calculate).grid(
    column=3, row=3, sticky=W
)
ttk.Label(master=mainframe, text="feet").grid(column=3, row=1, sticky=W)
ttk.Label(master=mainframe, text="is equivalent to").grid(column=1, row=2, sticky=E)
ttk.Label(master=mainframe, text="meters").grid(column=3, row=2, sticky=W)

# Add padding to all children
for child in mainframe.winfo_children():
    child.grid_configure(padx=5, pady=5)

# Set focus and bind Return key
feet_entry.focus()
root.bind(sequence="<Return>", func=lambda event: calculate())

# Start the main event loop
root.mainloop()
