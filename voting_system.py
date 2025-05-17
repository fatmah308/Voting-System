import tkinter as tk
from tkinter import messagebox, StringVar
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import hashlib
from tkinter import ttk
import datetime
import mysql.connector
from mysql.connector import Error

# Function to get SQL connection
def get_sql_connection(host="localhost", user="root", password="f@%!m@", database="voting_system"):
    try:
        # Establish the connection
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        
        # If the connection is successful
        if connection.is_connected():
            if database:
                print("Connected to database voting_system successfully!")
            else:
                print("Connected to the database successfully!")
            return connection
    except Error as e:
        if database:
            print("Error: Could not connect to database voting_system. Reason: {e}")
        else:
            print("Error: Could not connect. Reason: {e}")
    return None

# Function to open the voter login window
def open_voter_window():
    voter_window = tk.Toplevel(root)
    voter_window.title("E_VOTING")
    voter_window.geometry("500x500")  # Set the same size as the main window
    voter_window.configure(bg="white")
    
    # E-Voting Label (Heading)
    tk.Label(voter_window, text="E-VOTING",  bg="steelblue", fg="white", font=("montserret", 18,"bold")).pack(pady=10)

    # Username Label and Entry
    tk.Label(voter_window, text="Username:", fg="black", bg="white").pack(pady=10)
    username_entry = tk.Entry(voter_window,bg="snow3")
    username_entry.pack(pady=10)
    
    # Password Label and Entry
    tk.Label(voter_window, text="Password:", fg="black", bg="white").pack(pady=10)
    password_entry = tk.Entry(voter_window, show="*",bg="snow3")
    password_entry.pack(pady=10)

    def login():
        username = username_entry.get()
        password = password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Both username and password are required.")
            return

        #if not has_voting_started():
         #   messagebox.showwarning("Input Error", "voting hasn't started yet")
          #  return

        if is_voting_over():
            messagebox.showwarning("Input Error", "voting time is over")
            return
        
        is_valid, co_id = login_voter(username, password)

        if is_valid:
            candidates = get_candidates_from_constituency(co_id)  
            if candidates:
                display_candidates(candidates, username)  
            else:
                messagebox.showwarning("No Candidates", "No candidates found for this constituency.")
            voter_window.destroy()
        else:
            messagebox.showerror("Login Failed", co_id)

    # constituency change button
    def constituency_change_button():
        username = username_entry.get()
        password = password_entry.get()
        constituency = const_var.get()
    
        if not constituency:
            messagebox.showwarning("Input Error", "constituency number is required.")
        else:
            update_voter(username,password,constituency)
            
   
    tk.Button(voter_window, text="Vote", bg="steelblue", fg="white",font=("montserret", 10,"bold"),width=20, height=2, command=login).pack(pady=10)
    tk.Button(voter_window, text="Register as Voter", bg="steelblue", fg="white",font=("montserret", 10,"bold"), width=20, height=2,
              command=open_registration_form_voter).pack(pady=10)
    tk.Button(voter_window, text="Change Constituency", bg="steelblue", fg="white",font=("montserret", 10,"bold"), width=20, height=2,
              command = constituency_change_button).pack(pady=10)
    tk.Label(voter_window,text="Change constituency to ", fg="black", bg="white").pack(pady=10)
    constituencies = get_const()
    const_var = tk.StringVar()  
    const_dropdown = ttk.Combobox(voter_window, textvariable=const_var,state = 'readonly')
    const_dropdown['values'] = constituencies
    const_dropdown.pack(pady=10)

def has_voting_started():

    voting_start_time = datetime.datetime(2025, 1, 2, 13, 15, 0) 
    current_time = datetime.datetime.now()
    return current_time > voting_start_time

def is_voting_over():

    voting_end_time = datetime.datetime(2025, 1, 2, 13, 30, 0) 
    current_time = datetime.datetime.now()
    return current_time > voting_end_time

def display_candidates(candidates, username):
    candidates_window = tk.Toplevel(root)
    candidates_window.title("Candidates List")
    
    # Set the window size and background color
    candidates_window.geometry("600x400")
    candidates_window.config(bg="#f0f0f0")

    # Initialize StringVar to not select any radio button by default
    selected_candidate_username = tk.StringVar(value=None)  # Set initial value as None (no selection)

    # Header Label Styling
    header_font = ("Arial", 14, "bold")
    header_fg = "#333333"
    header_bg = "#e0e0e0"
    
    # Labels for the header with padding and better font
    tk.Label(candidates_window, text="Candidate Name", font=header_font, fg=header_fg, bg=header_bg, padx=10, pady=5).grid(row=0, column=0, sticky="w")
    tk.Label(candidates_window, text="Political Party", font=header_font, fg=header_fg, bg=header_bg, padx=10, pady=5).grid(row=0, column=1, sticky="w")

    # Tooltip for manifesto display with enhanced design
    tooltip = tk.Toplevel(candidates_window)
    tooltip.withdraw()
    tooltip.overrideredirect(True)
    tooltip_label = tk.Label(tooltip, text="", wraplength=200, bg="snow3", fg="black", relief="solid", borderwidth=2, font=("Arial", 10))
    tooltip_label.pack(padx=5, pady=5)

    def show_tooltip(event, manifesto):
        tooltip_label.config(text=f"Manifesto: {manifesto}")
        tooltip.geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
        tooltip.deiconify()

    def hide_tooltip(event):
        tooltip.withdraw()

    # Loop to create candidate list and radiobuttons
    for i, candidate in enumerate(candidates, start=1):
        candidate_id, first_name, last_name, party_name, manifesto, candidate_username = candidate
        full_name = f"{first_name} {last_name}"

        # Radio button for selecting a candidate with color change on hover
        radio_button = tk.Radiobutton(candidates_window,
                                      text=full_name,  # Show candidate name as label in the radio button
                                      variable=selected_candidate_username,
                                      value=candidate_username,  # Unique value for each radio button
                                      bg="#f0f0f0", activebackground="#c1e1f5",
                                      highlightthickness=0, relief="solid")
        radio_button.grid(row=i, column=0, sticky="w", padx=20, pady=10)

        # Political party label with better spacing
        tk.Label(candidates_window, text=party_name, anchor="w", font=("Arial", 12), bg="#f0f0f0").grid(row=i, column=1, padx=20, pady=5, sticky="w")

        # Binding tooltip to radiobutton
        radio_button.bind("<Enter>", lambda e, manifesto=manifesto: show_tooltip(e, manifesto))
        radio_button.bind("<Leave>", hide_tooltip)

    # Function to confirm vote
    def confirm_vote():
        candidate_username = selected_candidate_username.get()
        if not candidate_username:
            messagebox.showwarning("Selection Error", "Please select a candidate.")
        else:
            increment_vote(username, candidate_username)  # Pass voter's username to the increment_vote function
            candidates_window.destroy()

    # Styling the "Confirm Vote" button with a hover effect
    button_font = ("Arial", 12, "bold")
    confirm_button = tk.Button(candidates_window, text="Confirm Vote", command=confirm_vote, font=button_font, bg="#4CAF50", fg="white",
                               relief="raised", height=2,width=20, bd=3)
    confirm_button.grid(row=len(candidates) + 1, column=0, columnspan=2, pady=20)

    # Hover effect for button
    def on_enter_button(event):
        confirm_button.config(bg="#45a049")

    def on_leave_button(event):
        confirm_button.config(bg="#4CAF50")

    confirm_button.bind("<Enter>", on_enter_button)
    confirm_button.bind("<Leave>", on_leave_button)


# Function to open the registration form for voter
def open_registration_form_voter():
    registration_window = tk.Toplevel(root)
    registration_window.title("Register as Voter")
    registration_window.geometry("300x500")
    registration_window.configure(bg="white")

    # Registration Form Title
    tk.Label(registration_window, text="Register as Voter",  bg="steelblue", fg="white",
             font=("montserret", 18,"bold")).grid(row=0, columnspan=2, padx=5, pady=10)

    # First Name Label and Entry
    tk.Label(registration_window, text="First Name:", fg="black", bg="white").grid(row=1, column=0, padx=5, pady=5)
    first_name_entry = tk.Entry(registration_window,bg="snow3")
    first_name_entry.grid(row=1, column=1, padx=5, pady=5)

    # Last Name Label and Entry
    tk.Label(registration_window, text="Last Name:", fg="black", bg="white").grid(row=2, column=0, padx=5, pady=5)
    last_name_entry = tk.Entry(registration_window,bg="snow3")
    last_name_entry.grid(row=2, column=1, padx=5, pady=5)

    # CNIC Label and Entry
    tk.Label(registration_window, text="CNIC:", fg="black", bg="white").grid(row=3, column=0, padx=5, pady=5)
    cnic_entry = tk.Entry(registration_window,bg="snow3")
    cnic_entry.grid(row=3, column=1, padx=5, pady=5)

    # Age Label and Entry
    tk.Label(registration_window, text="Age:", fg="black", bg="white").grid(row=4, column=0, padx=5, pady=5)
    age_entry = tk.Entry(registration_window,bg="snow3")
    age_entry.grid(row=4, column=1, padx=5, pady=5)

    # Gender Label and Radio Buttons
    tk.Label(registration_window, text="Gender:", fg="black", bg="white").grid(row=5, column=0, padx=5, pady=5)
    gender_var = StringVar()
    gender_var.set("M")  
    tk.Radiobutton(registration_window, text="Male", variable=gender_var, value="M", fg="black", bg="white").grid(row=5, column=1, padx=5, pady=5)
    tk.Radiobutton(registration_window, text="Female", variable=gender_var, value="F", fg="black", bg="white").grid(row=6, column=1, padx=5, pady=5)

    # Area Label and Dropdown
    tk.Label(registration_window, text="Area:", fg="black", bg="white").grid(row=7, column=0, padx=5, pady=5)
    areas = get_areas()
    area_var = StringVar()
    area_dropdown = tk.OptionMenu(registration_window, area_var, *areas, command=lambda selected_area: on_area_select(selected_area))
    area_dropdown.grid(row=7, column=1, padx=5, pady=5)

    # Constituency Label and Entry (auto-filled)
    tk.Label(registration_window, text="Constituency:", fg="black", bg="white").grid(row=8, column=0, padx=5, pady=5)
    global constituency_entry  
    constituency_entry = tk.Entry(registration_window, state="readonly",bg="snow3")
    constituency_entry.grid(row=8, column=1, padx=5, pady=5)
    
    # Username Label and Entry
    tk.Label(registration_window, text="Username:", fg="black", bg="white").grid(row=9, column=0, padx=5, pady=5)
    username_entry = tk.Entry(registration_window,bg="snow3")
    username_entry.grid(row=9, column=1, padx=5, pady=5)

    # Password Label and Entry
    tk.Label(registration_window, text="Password:", fg="black", bg="white").grid(row=10, column=0, padx=5, pady=5)
    password_entry = tk.Entry(registration_window, show="*",bg="snow3")
    password_entry.grid(row=10, column=1, padx=5, pady=5)

    # Register Button
    tk.Button(registration_window, text="Register", bg="steelblue", fg="white",font=("montserret",10,"bold"), width=20, height=2,
              command=lambda: validate_registration(first_name_entry.get(),last_name_entry.get(),cnic_entry.get(), age_entry.get(),
                                                    gender_var.get(),area_var.get(), username_entry.get(),password_entry.get()
    )).grid(row=11, columnspan=2, padx=5, pady=20)

# Function to handle area selection and update constituency field
def on_area_select(selected_area):
    try:
        constituency = get_constituency_from_area(selected_area)
        if constituency:
            constituency_entry.config(state="normal")  
            constituency_entry.delete(0, tk.END)
            constituency_entry.insert(tk.END, constituency)
            constituency_entry.config(state="readonly")  
        else:
            constituency_entry.delete(0, tk.END)
            messagebox.showinfo("Information", f"No constituency found for area '{selected_area}'.")
    except Exception as e:
        constituency_entry.delete(0, tk.END)
        messagebox.showerror("Error", f"Error fetching constituency: {e}")

# Validation function for voter registration
def validate_registration(first_name, last_name, cnic, age, gender, area, username, password):
    if not all([first_name, last_name, cnic, age, gender, area, username, password]):
        messagebox.showerror("Error", "All fields are required!")
    else:
        register_voter(first_name, last_name, cnic, age, gender, area, username, password)


# Function to open the candidate login window
def open_candidate_window():
    candidate_window = tk.Toplevel(root)
    candidate_window.title("Candidate registration")
    candidate_window.geometry("500x500")  # Set the same size as the main window
    candidate_window.configure(bg="white")
    
    # E-Voting Label (Heading)
    tk.Label(candidate_window, text="Candidate registration",  bg="steelblue", fg="white", font=("montserret", 18,"bold")).pack(pady=10)

    # Username Label and Entry
    tk.Label(candidate_window, text="Username:", fg="black", bg="white").pack(pady=10)
    username_entry = tk.Entry(candidate_window,bg="snow3")
    username_entry.pack(pady=10)
    
    # Password Label and Entry
    tk.Label(candidate_window, text="Password:", fg="black", bg="white").pack(pady=10)
    password_entry = tk.Entry(candidate_window, show="*",bg="snow3")
    password_entry.pack(pady=10)
    
    # Buttons (stacked vertically)
    tk.Button(candidate_window, text="Register as Candidate", bg="steelblue", fg="white",font=("montserret", 10,"bold"), width=20, height=2,
              command=open_registration_form_candidate).pack(pady=10)
    tk.Button(candidate_window, text="Backout as Candidate", bg="steelblue", fg="white",font=("montserret", 10,"bold"), width=20, height=2,
              command = lambda: delete_candidate(username_entry.get(),password_entry.get())).pack(pady=10)

#Function to open the registration form for candidate
def open_registration_form_candidate():
    registration_window2 = tk.Toplevel(root)
    registration_window2.title("Register as Candidate")
    registration_window2.geometry("400x600")
    registration_window2.configure(bg="white")

    # Registration Form Title
    tk.Label(registration_window2, text="Register as Candidate",  bg="steelblue", fg="white",
             font=("montserret", 18,"bold")).grid(row=0, columnspan=2, padx=5, pady=10)

    # First Name Label and Entry
    tk.Label(registration_window2, text="First Name:", fg="black", bg="white").grid(row=1, column=0, padx=5, pady=5)
    first_name_entry = tk.Entry(registration_window2,bg="snow3")
    first_name_entry.grid(row=1, column=1, padx=5, pady=5)

    # Last Name Label and Entry
    tk.Label(registration_window2, text="Last Name:", fg="black", bg="white").grid(row=2, column=0, padx=5, pady=5)
    last_name_entry = tk.Entry(registration_window2,bg="snow3")
    last_name_entry.grid(row=2, column=1, padx=5, pady=5)

    # CNIC Label and Entry
    tk.Label(registration_window2, text="CNIC:", fg="black", bg="white").grid(row=3, column=0, padx=5, pady=5)
    cnic_entry = tk.Entry(registration_window2,bg="snow3")
    cnic_entry.grid(row=3, column=1, padx=5, pady=5)

    # Age Label and Entry
    tk.Label(registration_window2, text="Age:", fg="black", bg="white").grid(row=4, column=0, padx=5, pady=5)
    age_entry = tk.Entry(registration_window2,bg="snow3")
    age_entry.grid(row=4, column=1, padx=5, pady=5)

    # Qualification Label and Entry
    tk.Label(registration_window2, text="Qualification:", fg="black", bg="white").grid(row=5, column=0, padx=5, pady=5)
    qualifications = ['Matric','Fsc','Bachelors', 'Masters', 'Doctorate']
    qual_var = StringVar()
    qualification_combobox = ttk.Combobox(registration_window2, textvariable=qual_var, values=qualifications,state = 'readonly')
    qualification_combobox.grid(row=5, column=1, padx=5, pady=5)

    # Gender Label and Radio Buttons
    tk.Label(registration_window2, text="Gender:", fg="black", bg="white").grid(row=6, column=0, padx=5, pady=5)
    gender_var = StringVar()
    gender_var.set("M")  # Default value
    tk.Radiobutton(registration_window2, text="Male", variable=gender_var, value="M", fg="black", bg="white").grid(row=6, column=1, padx=5, pady=5)
    tk.Radiobutton(registration_window2, text="Female", variable=gender_var, value="F", fg="black", bg="white").grid(row=7, column=1, padx=5, pady=5)

    # Political Party Label and Dropdown
    tk.Label(registration_window2, text="Political Party:", fg="black", bg="white").grid(row=8, column=0, padx=5, pady=5)
    parties = get_parties()
    party_var = StringVar()
    party_combobox = ttk.Combobox(registration_window2, textvariable=party_var, values=parties,state = 'readonly')
    party_combobox.grid(row=8, column=1, padx=5, pady=5)

    # Constituency Label and Dropdown
    tk.Label(registration_window2, text="Constituency:", fg="black", bg="white").grid(row=9, column=0, padx=5, pady=5)
    constituencies = get_const()
    const_var = StringVar()
    const_combobox = ttk.Combobox(registration_window2, textvariable=const_var, values=constituencies,state = 'readonly')
    const_combobox.grid(row=9, column=1, padx=5, pady=5)

    # Username Label and Entry
    tk.Label(registration_window2, text="Username:", fg="black", bg="white").grid(row=10, column=0, padx=5, pady=5)
    username_entry = tk.Entry(registration_window2,bg="snow3")
    username_entry.grid(row=10, column=1, padx=5, pady=5)

    # Password Label and Entry
    tk.Label(registration_window2, text="Password:", fg="black", bg="white").grid(row=11, column=0, padx=5, pady=5)
    password_entry = tk.Entry(registration_window2, show="*",bg="snow3")
    password_entry.grid(row=11, column=1, padx=5, pady=5)

   # Manifesto Label and Text Widget
    tk.Label(registration_window2, text="Manifesto:", fg="black", bg="white").grid(row=12, column=0, padx=5, pady=5)
    manifesto_text = tk.Text(registration_window2, width=30, height=3, wrap="word",bg="snow3") 
    manifesto_text.grid(row=12, column=1, padx=5, pady=5)

    # Word Count Label
    word_count_label = tk.Label(registration_window2, text="0/90 characters", fg="grey", font=("Arial", 8), bg="white")
    word_count_label.grid(row=13, column=1, sticky="w", padx=5, pady=5)

    # Bind events to the text widget to enforce character limit
    bind_character_limit(manifesto_text, word_count_label)

    # Register Button
    tk.Button(registration_window2, text="Register", bg="steelblue", fg="white",font=("montserret", 10,"bold"), width=20, height=2,
              command=lambda: validate_registration_candidate(first_name_entry.get(), last_name_entry.get(),cnic_entry.get(),age_entry.get(),
                                                              qual_var.get(),gender_var.get(),party_var.get(),const_var.get(),username_entry.get(),
                                                              password_entry.get(),manifesto_text.get("1.0", "end-1c").strip()
    )).grid(row=14, columnspan=2, padx=5, pady=20)

# Function to enforce character limit and update character count dynamically
def enforce_character_limit(event, text_widget, word_count_label):
    content = text_widget.get("1.0", "end-1c")  
    char_count = len(content)

    # Update the character count label
    word_count_label.config(text=f"{char_count}/90 characters")

    # Enforce the character limit
    if char_count > 90:
        text_widget.delete("1.0", "end")  
        text_widget.insert("1.0", content[:90])  
        word_count_label.config(text="90/90 characters")  
        messagebox.showerror("Character Limit Exceeded", "Manifesto cannot exceed 90 characters.")
        return "break"  

# Binding the KeyRelease event to enforce character limit
def bind_character_limit(text_widget, word_count_label):
    text_widget.bind("<KeyRelease>", lambda event: enforce_character_limit(event, text_widget, word_count_label))
    text_widget.bind("<Control-v>", lambda event: enforce_character_limit(event, text_widget, word_count_label))

# Validation function for candidate registration
def validate_registration_candidate(first_name, last_name, cnic, age, qualification, gender, party, constituency, username, password, manifesto):
    if not all([first_name, last_name, cnic, age, qualification, gender, party, constituency, username, password, manifesto]):
        messagebox.showerror("Error", "All fields are required!")
    else:
        register_candidate(first_name, last_name, cnic, age, qualification, gender, party, constituency, username, password, manifesto)


# Function to open the voter login window
def open_admin_window():
    voter_window = tk.Toplevel(root)
    voter_window.title("E_VOTING")
    voter_window.geometry("500x500")  # Set the same size as the main window
    voter_window.configure(bg="white")
    
    # E-Voting Label (Heading)
    tk.Label(voter_window, text="SEE RESULTS",  bg="steelblue", fg="white", font=("montserret", 18,"bold")).pack(pady=10)

    # Username Label and Entry
    tk.Label(voter_window, text="Username:", fg="black", bg="white").pack(pady=10)
    username_entry = tk.Entry(voter_window,bg="snow3")
    username_entry.pack(pady=10)
    
    # Password Label and Entry
    tk.Label(voter_window, text="Password:", fg="black", bg="white").pack(pady=10)
    password_entry = tk.Entry(voter_window, show="*",bg="snow3")
    password_entry.pack(pady=10)

            
    # See party standing button
    def see_party_standing():
        username = username_entry.get()
        password = password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Both username and password are required.")
            return
        
        #if not is_voting_over():
         #   messagebox.showwarning("Voting Not Over", "Results cannot be viewed until voting time is over.")
          #  return

        is_valid, co_id = login_admin(username, password)

        if is_valid:
            print(f"Logged in successfully, Constituency ID: {co_id}")
            party_standing = get_party_standing(co_id)
            if party_standing:
                display_party_standing(party_standing)
            else:
                messagebox.showwarning("No Data", "No data available for party standings.")
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    # See candidate standing button
    def see_candidate_standing():
        username = username_entry.get()
        password = password_entry.get()

        if not username or not password:
            messagebox.showwarning("Input Error", "Both username and password are required.")
            return
        #if not is_voting_over():
         #   messagebox.showwarning("Voting Not Over", "Results cannot be viewed until voting time is over.")
          #  return

        is_valid, co_id = login_admin(username, password)

        if is_valid:
            print(f"Logged in successfully, Constituency ID: {co_id}")
            candidate_standing = get_candidate_standing(co_id)
            if candidate_standing:
                display_candidate_standing(candidate_standing)
            else:
                messagebox.showwarning("No Data", "No data available for candidate standings.")
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
            
    # Buttons (stacked vertically)
    tk.Button(voter_window, text="See party standing",  bg="steelblue", fg="white",font=("montserret", 10,"bold"), width=20, height=2,
              command=see_party_standing).pack(pady=10)
    tk.Button(voter_window, text="See candidate standing", bg="steelblue", fg="white",font=("montserret", 10,"bold"), width=20, height=2,
              command = see_candidate_standing).pack(pady=10)
    

# Function to display party standings as a pie chart
def display_party_standing(party_standing):
    party_window = tk.Toplevel(root)
    party_window.title("Party Standing")

    # Prepare data for the pie chart
    labels = [party_name for party_name, _ in party_standing]
    sizes = [total_votes for _, total_votes in party_standing]
    
    # Create the pie chart
    fig, ax = plt.subplots(figsize=(8, 8))  
    ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, textprops={'fontsize': 10})
    ax.axis('equal')  

    # Display the pie chart in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=party_window)
    canvas.draw()
    canvas.get_tk_widget().pack(pady=20)

# Function to display candidate standings and plot the bar chart in a new window
def display_candidate_standing(candidate_standing):
    candidate_window = tk.Toplevel(root)  # Create a new window for candidate standings
    candidate_window.title("Candidate Standing")
    candidate_window.geometry("800x600")  # Adjust window size as needed

    # Create a bar chart for candidate votes
    names = [f"{first} {last}" for first, last, _ in candidate_standing]
    votes = [votes for _, _, votes in candidate_standing]

    fig, ax = plt.subplots(figsize=(12, 8))  
    ax.bar(names, votes, color='skyblue')
    ax.set_xlabel('Candidates')
    ax.set_ylabel('Votes')
    ax.set_title('Votes per Candidate')

    # Rotate x-axis labels to avoid overlap and ensure they fit
    plt.xticks(rotation=45, ha='right', fontsize=10)

    # Use tight layout to prevent labels from getting cut off
    plt.tight_layout()

    # Display the chart in the Tkinter window
    canvas = FigureCanvasTkAgg(fig, master=candidate_window)  
    canvas.draw()
    canvas.get_tk_widget().pack(pady=20)

def login_voter(username, password):
    conn = get_sql_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT password_hash, co_id, vote_status FROM voter WHERE username = %s", (username,))
    voter = cursor.fetchone()
    
    if voter:
        stored_password_hash = voter[0]
        vote_status = voter[2]

        if vote_status == 'casted':
            return False, "You have already cast your vote."  
        
        hashed_input_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        
        if hashed_input_password == stored_password_hash:  
            return True, voter[1]  
        else:
            return False, "Invalid username or password."  
        
    else:
        return False, "Invalid username or password."  


# Function to check if the admin exists and password matches
def login_admin(username, password):
    conn = get_sql_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password_hash, aid FROM residing_officer WHERE username = %s", (username,))
    admin = cursor.fetchone()
    
    if admin:
        stored_password_hash = admin[0]
        
        hashed_input_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
        
        if hashed_input_password == stored_password_hash:
            aid = admin[1]
            cursor.execute("SELECT co_id FROM constituency WHERE aid = %s", (aid,))
            constituency = cursor.fetchone()
            
            if constituency:
                co_id = constituency[0]
                return True, co_id  
            else:
                return False, None  
        else:
            return False, None 
    else:
        return False, None

def get_party_standing(co_id):
    conn = get_sql_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT p.p_name, SUM(c.vtes) AS total_votes
        FROM candidate c
        JOIN politicalparty p ON c.par_id = p.par_id
        WHERE c.co_id = %s
        GROUP BY p.p_name
    """, (co_id,))
    party_standing = cursor.fetchall()
    conn.close()

    return party_standing

# Function to get the standing of each candidate in the admin's constituency
def get_candidate_standing(co_id):
    conn = get_sql_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.first_name, c.last_name, c.vtes
        FROM candidate c
        WHERE c.co_id = %s
    """, (co_id,))
    candidate_standing = cursor.fetchall()
    conn.close()

    return candidate_standing


# Function to fetch candidates from the voter's constituency
def get_candidates_from_constituency(co_id):
    conn = get_sql_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT c.cid, c.first_name, c.last_name, p.p_name, c.menifesto, c.username "
                   "FROM candidate c "
                   "JOIN politicalparty p ON c.par_id = p.par_id "
                   "WHERE c.co_id = %s", (co_id,))
    candidates = cursor.fetchall()

    print(candidates) 
    return candidates

#Function to fetch constituencies from database
def get_const():
    connection = get_sql_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT co_num FROM constituency")
    const = cursor.fetchall()
    connection.close()
    return [constituency[0] for constituency in const]

#Function to fetch political parties from database
def get_parties():
    connection = get_sql_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT p_name FROM politicalparty")
    parties = cursor.fetchall()
    connection.close()
    return [politicalparty[0] for politicalparty in parties]

# Function to fetch areas from the database
def get_areas():
    connection = get_sql_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT a_name FROM area")
    areas = cursor.fetchall()
    connection.close()
    return [area[0] for area in areas]

# Function to fetch constituency based on area
def get_constituency_from_area(area):
    connection = get_sql_connection()
    cursor = connection.cursor()

    try:
        print("Executing query for area: '{area}'")
        cursor.execute("SELECT co_num FROM constituency c JOIN area a ON c.co_id = a.co_id WHERE a.a_name = %s", (area,))
        result = cursor.fetchone()

        if result:
            print("Constituency found: {result[0]}") 
            return result[0]  
        else:
            print("No constituency found.")
            messagebox.showerror("Error", "No constituency found for area '{area}'.")
            return None 

    except Exception as e:
        print(f"Error fetching constituency:", e)
        messagebox.showerror("Error", f"Error fetching constituency: {e}")
        return None 

    finally:
        connection.close()

# Function to increment the vote count for the selected candidate
def increment_vote(voter_username, candidate_username):
    try:
        connection = get_sql_connection()
        cursor = connection.cursor()

        cursor.callproc('increment_votes', (voter_username, candidate_username))  
        connection.commit()
        
        messagebox.showinfo("Success", "Vote cast successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Error incrementing vote: {e}")
    finally:
        connection.close()

# Function to register a new voter
def register_voter(first_name, last_name, cnic, age, gender, area, username, password):
    try:
        connection = get_sql_connection()
        cursor = connection.cursor()
        cursor.callproc('insert_voter', (username, password, age, cnic, first_name, last_name, gender, area))
        connection.commit()
        messagebox.showinfo("Success", "Voter registered successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Error registering voter: {e}")
    finally:
        connection.close()

def register_candidate(first_name, last_name, cnic, age, qualification, gender, political_party, constituency, username, password, menifesto):
    try:
        connection = get_sql_connection()
        cursor = connection.cursor()
        cursor.callproc('insert_candidate', (first_name, last_name, cnic, age, constituency,political_party, qualification, username, password, menifesto, gender))
        connection.commit()
        messagebox.showinfo("Success", "Candidate registered successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Error registering candidate: {e}")
    finally:
        connection.close()

def update_voter(username,password,constituency):
    try:
        connection = get_sql_connection()
        cursor = connection.cursor()
        cursor.callproc('update_const_v', (username,password,constituency))
        connection.commit()
        messagebox.showinfo("Success", "Constituency updated successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Error updating constituency: {e}")
    finally:
        connection.close()

def delete_candidate(username,password):
    try:
        connection = get_sql_connection()
        cursor = connection.cursor()
        cursor.callproc('remove_candidate', (username,password,))
        connection.commit()
        messagebox.showinfo("Success", "removed successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Error deleting: {e}")
    finally:
        connection.close()


# Main Window        
root = tk.Tk()
root.title("GENERAL ELECTION JAN 2025")
root.geometry("500x500")  # Set the same size as the second window
root.configure(bg="white")

# Title Label in the Main Window
tk.Label(root, text="GENERAL ELECTION JAN 2025", bg="steelblue", fg="white", font=("montserret", 18,"bold")).pack(pady=60)

# Buttons in the Main Window (bigger size)
tk.Button(root, text="VOTER", bg="steelblue", fg="white",font=("montserret", 10,"bold"), width=20, height=2, command=open_voter_window).pack(pady=10)
tk.Button(root, text="CANDIDATE", bg="steelblue", fg="white",font=("montserret", 10,"bold"), width=20, height=2, command=open_candidate_window).pack(pady=10)
tk.Button(root, text="RESIDING OFFICER", bg="steelblue", font=("montserret", 10,"bold"),fg="white", width=20, height=2, command=open_admin_window).pack(pady=10)

# Start the main loop
root.mainloop()
