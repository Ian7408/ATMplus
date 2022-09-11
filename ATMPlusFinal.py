#   ATM+ Application
#   SDEV 265
#   Group 1
#
#   Application to work as a banking app connected to an AWS database
#
#   Version 1.0
#       connected to local database
#   Version 1.2
#       struggled with pymysql as a db connector
#   Version 1.3
#       Replaced pymysql with mysql.connector
#   Version 1.4
#       Added sql injection defenses
#       Corrected an issue with the withdraw method
#       Comments added
#   Version 1.5
#       Added checking and savings options and connected to DB
#   Version 1.5.1
#       Fixed mysql query in signup email --> cust_email
#   Version 1.6
#       Added current checking/savings balances to deposit/withdraw screens
#       Added the ability to switch between checking/savings accounts without logging out
#       Fixed input of negative amount in textboxes for deposit and withdrawal

from email.errors import MessageDefect
from select import select
import mysql.connector
from sqlite3 import Error
import tkinter as tk
from tkinter import GROOVE, messagebox
import re


####-----Verify valid email syntax------####
regex = re.compile(r"([A-Za-z0-9]+[.-_])*[A-Za-z0-9]+@[A-Za-z0-9-]+(\.[A-Z|a-z]{2,})+")


def isValid(email):
    if re.fullmatch(regex, email):
        print("Valid email")
        return True
    else:
        print("Invalid email")
        return False


####------Connect to Database Method------####
def db_connection():
    conn = None
    try:
        conn = mysql.connector.connect(
            user="admin",
            password="M6ygN18UbWNbkSmVT3rS",
            host="database-1.cfs3uth9dhhf.us-east-1.rds.amazonaws.com",
            database="ATM",
        )
        print("database connected")
    except Error as e:
        print(e)

    return conn


def sign_up(conn):
    global global_email
    entered_email = register_frame_email_entry.get()
    entered_password = register_frame_password_entry.get()
    first_name = register_frame_fname_entry.get()
    last_name = register_frame_lname_entry.get()
    dob = register_frame_dob_entry.get()
    pin = register_frame_pin_entry.get()
    checking_balance = 0.0
    savings_balance = 0.0

    cur = conn.cursor()

    cur.execute(
        """SELECT cust_email FROM CUSTOMER_LOGIN WHERE cust_email= %s""",
        (entered_email,),
    )
    data = cur.fetchall()

    print(data)

    if not data:
        try:
            check_pin = int(pin)

            if len(str(check_pin)) == 4:
                cur.execute(
                    f"""INSERT INTO CUSTOMER_INFO(first_name, last_name, checking_balance, savings_balance, email, dob) VALUES(\"{first_name}\", \"{last_name}\", \"{checking_balance}\", \"{savings_balance}\", \"{entered_email}\", \"{dob}\")"""
                )
                cur.execute(
                    f"""INSERT INTO CUSTOMER_LOGIN(cust_email, password, pin) VALUES(\"{entered_email}\", \"{entered_password}\", \"{pin}\")"""
                )

                conn.commit()

                messagebox.showinfo(
                    "Success!", "Congratulations and welcome to our ATM Machine App!"
                )
                raise_frame(select_account_frame)
                global_email = register_frame_email_entry.get()
            else:
                messagebox.showerror(
                    "Registration Error", "Your pin must be a 4 digit number!"
                )
        except:
            messagebox.messagebox.showerror(
                "Registration Error", "Your pin must be a 4 digit number!"
            )

    else:
        messagebox.showerror(
            "Registration Error",
            "The email you are trying to use already exists or you need to enter proper values in all of the fields.",
        )


def sign_in(conn):
    global global_email
    entered_email = login_frame_email_entry.get()
    entered_password = login_frame_password_entry.get()

    cur = conn.cursor()

    # Verify valid email syntax
    if not isValid(entered_email):
        messagebox.showerror("Registration Error", "Please enter a valid Email Address")

    else:
        cur.execute(
            """SELECT cust_email FROM CUSTOMER_LOGIN WHERE cust_email = %s""",
            (entered_email,),
        )
    data = cur.fetchall()

    if not data:
        messagebox.showerror(
            "Login Error",
            "This email does not exist in our database! Please try again!",
        )
    else:
        cur.execute(
            """SELECT password FROM CUSTOMER_LOGIN WHERE cust_email=%s""",
            (entered_email,),
        )
        password = cur.fetchone()

    if entered_password == password[0]:
        raise_frame(select_account_frame)
        global_email = login_frame_email_entry.get()
    else:
        messagebox.showerror("Login Error", "Incorrect password. Please try again!")


def check_savings_balance(conn):
    cur = conn.cursor()
    cur.execute(
        """SELECT savings_balance FROM CUSTOMER_INFO WHERE email=%s""", (global_email,)
    )

    cur_balance = cur.fetchone()

    if cur_balance == None:
        balance = 0
    else:
        balance = cur_balance[0]

    savings_balance_frame_balance = tk.Label(savings_balance_frame, text=f"${balance}")
    savings_balance_frame_balance.place(rely=0.4, relx=0.51, width=100)

    savings_withdraw_frame_balance = tk.Label(
        savings_withdraw_frame, text=f"${balance}"
    )
    savings_withdraw_frame_balance.place(rely=0.3, relx=0.48, width=100)

    savings_deposit_frame_balance = tk.Label(savings_deposit_frame, text=f"${balance}")
    savings_deposit_frame_balance.place(rely=0.3, relx=0.48, width=100)


def check_checking_balance(conn):
    cur = conn.cursor()
    cur.execute(
        """SELECT checking_balance FROM CUSTOMER_INFO WHERE email=%s""", (global_email,)
    )

    cur_balance = cur.fetchone()

    if cur_balance == None:
        balance = 0
    else:
        balance = cur_balance[0]

    checking_balance_frame_balance = tk.Label(
        checking_balance_frame, text=f"${balance}"
    )
    checking_balance_frame_balance.place(rely=0.4, relx=0.51, width=100)

    checking_withdraw_frame_balance = tk.Label(
        checking_withdraw_frame, text=f"${balance}"
    )
    checking_withdraw_frame_balance.place(rely=0.3, relx=0.48, width=100)

    checking_deposit_frame_balance = tk.Label(
        checking_deposit_frame, text=f"${balance}"
    )
    checking_deposit_frame_balance.place(rely=0.3, relx=0.48, width=100)


def savings_deposit(conn):
    try:
        amount = int(savings_deposit_frame_amount_entry.get())
        if amount > 0:
            cur = conn.cursor()

            try:
                cur.execute(
                    """SELECT savings_balance FROM CUSTOMER_INFO WHERE email= %s""",
                    (global_email,),
                )
            except:
                print("error on select savings_balance from Customer_info statement")

            bal_list = cur.fetchone()
            current_balance = bal_list[0]

            new_balance = current_balance + amount

            cur.execute(
                f"""UPDATE CUSTOMER_INFO SET savings_balance = \"{new_balance}\" WHERE email = \"{global_email}\""""
            )

            conn.commit()
            savings_deposit_frame_amount_entry.delete(0, "end")
            messagebox.showinfo(
                "Successfully deposited!",
                "Thank you for banking with us & have a nice day!",
            )
        else:
            messagebox.showerror(
                "Invalid Entry!", "Please only enter full positive numeric values."
            )
    except:
        messagebox.showerror(
            "Invalid Entry!", "Please only enter full positive numeric values."
        )


def checking_deposit(conn):
    try:
        amount = int(checking_deposit_frame_amount_entry.get())
        if amount > 0:
            cur = conn.cursor()

            try:
                cur.execute(
                    """SELECT checking_balance FROM CUSTOMER_INFO WHERE email= %s""",
                    (global_email,),
                )
            except:
                print("error on select checking_balance from Customer_info statement")

            bal_list = cur.fetchone()
            current_balance = bal_list[0]

            new_balance = current_balance + amount

            cur.execute(
                f"""UPDATE CUSTOMER_INFO SET checking_balance = \"{new_balance}\" WHERE email = \"{global_email}\""""
            )

            conn.commit()
            checking_deposit_frame_amount_entry.delete(0, "end")
            messagebox.showinfo(
                "Successfully deposited!",
                "Thank you for banking with us & have a nice day!",
            )
        else:
            messagebox.showerror(
                "Invalid Entry!", "Please only enter full positive numeric values."
            )
    except:
        messagebox.showerror(
            "Invalid Entry!", "Please only enter full positive numeric values."
        )


def savings_withdraw(conn):
    try:
        amount = int(savings_withdraw_frame_amount_entry.get())
        if amount > 0:
            cur = conn.cursor()

            try:
                cur.execute(
                    """SELECT savings_balance FROM CUSTOMER_INFO WHERE email= %s""",
                    (global_email,),
                )
            except:
                print("error on select savings_balance from Customer_info statement")

            bal_list = cur.fetchone()
            current_balance = bal_list[0]

            if current_balance < amount:
                messagebox.showerror(
                    "Insufficient funds!",
                    "Your current savings balance is: $" + str(current_balance),
                )
            else:
                new_balance = current_balance - amount
                cur.execute(
                    f"""UPDATE CUSTOMER_INFO SET savings_balance = \"{new_balance}\" WHERE email = \"{global_email}\""""
                )
                conn.commit()
                savings_withdraw_frame_amount_entry.delete(0, "end")
                messagebox.showinfo(
                    "Successfully withdrawn!",
                    "Thank you for banking with us & have a nice day!",
                )
        else:
            messagebox.showerror(
                "Invalid Entry!", "Please only enter full positive numeric values."
            )
    except:
        messagebox.showerror(
            "Invalid Entry!", "Please only enter full positive numeric values."
        )


def checking_withdraw(conn):
    try:
        amount = int(checking_withdraw_frame_amount_entry.get())
        if amount > 0:
            cur = conn.cursor()

            try:
                cur.execute(
                    """SELECT checking_balance FROM CUSTOMER_INFO WHERE email= %s""",
                    (global_email,),
                )
            except:
                print("error on select checking_balance from Customer_info statement")

            bal_list = cur.fetchone()
            current_balance = bal_list[0]

            if current_balance < amount:
                messagebox.showerror(
                    "Insufficient funds!",
                    "Your current checking balance is: $" + str(current_balance),
                )
            else:
                new_balance = current_balance - amount
                cur.execute(
                    f"""UPDATE CUSTOMER_INFO SET checking_balance = \"{new_balance}\" WHERE email = \"{global_email}\""""
                )
                conn.commit()
                checking_withdraw_frame_amount_entry.delete(0, "end")
                messagebox.showinfo(
                    "Successfully withdrawn!",
                    "Thank you for banking with us & have a nice day!",
                )
        else:
            messagebox.showerror(
                "Invalid Entry!", "Please only enter full positive numeric values."
            )
    except:
        messagebox.showerror(
            "Invalid Entry!", "Please only enter full positive numeric values."
        )


def sign_out():
    global global_email
    register_frame_fname_entry.delete(0, "end")
    register_frame_lname_entry.delete(0, "end")
    register_frame_email_entry.delete(0, "end")
    register_frame_password_entry.delete(0, "end")
    register_frame_dob_entry.delete(0, "end")
    register_frame_pin_entry.delete(0, "end")
    login_frame_email_entry.delete(0, "end")
    login_frame_password_entry.delete(0, "end")
    global_email = ""


def raise_frame(frame):
    frame.tkraise()


if __name__ == "__main__":
    global global_email
    conn = db_connection()

    root = tk.Tk()
    root.title("ATM Machine App")

    root.resizable(False, False)

    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    root.geometry("600x600")

    starting_frame = tk.Frame(root)
    login_frame = tk.Frame(root)
    register_frame = tk.Frame(root)
    select_account_frame = tk.Frame(root)
    main_savings_frame = tk.Frame(root)
    main_checking_frame = tk.Frame(root)
    checking_deposit_frame = tk.Frame(root)
    checking_withdraw_frame = tk.Frame(root)
    checking_balance_frame = tk.Frame(root)
    savings_deposit_frame = tk.Frame(root)
    savings_withdraw_frame = tk.Frame(root)
    savings_balance_frame = tk.Frame(root)

    for frame in (
        starting_frame,
        login_frame,
        register_frame,
        select_account_frame,
        main_savings_frame,
        main_checking_frame,
        checking_deposit_frame,
        checking_withdraw_frame,
        checking_balance_frame,
        savings_deposit_frame,
        savings_withdraw_frame,
        savings_balance_frame,
    ):
        frame.grid(row=0, column=0, sticky="nsew")

    raise_frame(starting_frame)

    ############################### STARTING FRAME ########################################
    starting_frame_title = tk.Label(
        starting_frame, text="Welcome to our ATM Machine App!"
    )
    starting_frame_title.place(relx=0.33)

    starting_frame_login_button = tk.Button(
        starting_frame, text="Login", command=lambda: raise_frame(login_frame)
    )
    starting_frame_login_button.place(rely=0.5, relx=0.4, width=100)

    starting_frame_register_button = tk.Button(
        starting_frame, text="Register", command=lambda: raise_frame(register_frame)
    )
    starting_frame_register_button.place(rely=0.6, relx=0.4, width=100)

    ############################### LOGIN FRAME ########################################
    login_frame_title = tk.Label(
        login_frame, text="Please login with your email and password!"
    )
    login_frame_title.place(relx=0.33)

    login_frame_email_label = tk.Label(login_frame, text="Email")
    login_frame_email_entry = tk.Entry(login_frame)
    login_frame_email_label.place(rely=0.5, relx=0.28)

    login_frame_password_label = tk.Label(login_frame, text="Password")
    login_frame_password_entry = tk.Entry(login_frame, show="*")
    login_frame_password_label.place(rely=0.6, relx=0.28)

    login_frame_email_entry.place(rely=0.5, relx=0.4)
    login_frame_password_entry.place(rely=0.6, relx=0.4)

    login_frame_signin_button = tk.Button(
        login_frame, text="Sign In", command=lambda: sign_in(conn), relief=GROOVE
    )
    login_frame_signin_button.place(rely=0.7, relx=0.4, width=50)

    login_frame_return_button = tk.Button(
        login_frame,
        text="Exit",
        command=lambda: raise_frame(starting_frame),
        relief=GROOVE,
    )
    login_frame_return_button.place(rely=0.7, relx=0.52, width=50)

    ############################### REGISTER FRAME ########################################
    register_frame_title = tk.Label(
        register_frame, text="Please register below with accurate information!"
    )
    register_frame_title.place(relx=0.33)

    register_frame_email_label = tk.Label(register_frame, text="Email")
    register_frame_email_entry = tk.Entry(register_frame)
    register_frame_email_label.place(rely=0.3, relx=0.28)

    register_frame_password_label = tk.Label(register_frame, text="Password")
    register_frame_password_entry = tk.Entry(register_frame, show="*")
    register_frame_password_label.place(rely=0.4, relx=0.28)

    register_frame_fname_label = tk.Label(register_frame, text="First Name")
    register_frame_fname_entry = tk.Entry(register_frame)
    register_frame_fname_label.place(rely=0.1, relx=0.28)

    register_frame_lname_label = tk.Label(register_frame, text="Last Name")
    register_frame_lname_entry = tk.Entry(register_frame)
    register_frame_lname_label.place(rely=0.2, relx=0.28)

    register_frame_dob_label = tk.Label(register_frame, text="Date of Birth")
    register_frame_dob_entry = tk.Entry(register_frame)
    register_frame_dob_label.place(rely=0.5, relx=0.28)

    register_frame_pin_label = tk.Label(register_frame, text="Pin")
    register_frame_pin_entry = tk.Entry(register_frame, show="*")
    register_frame_pin_label.place(rely=0.6, relx=0.28)

    register_frame_fname_entry.place(rely=0.1, relx=0.4)
    register_frame_lname_entry.place(rely=0.2, relx=0.4)
    register_frame_email_entry.place(rely=0.3, relx=0.4)
    register_frame_password_entry.place(rely=0.4, relx=0.4)
    register_frame_dob_entry.place(rely=0.5, relx=0.4)
    register_frame_pin_entry.place(rely=0.6, relx=0.4)

    register_frame_register_button = tk.Button(
        register_frame, text="Register", command=lambda: sign_up(conn), relief=GROOVE
    )
    register_frame_register_button.place(rely=0.7, relx=0.4, width=50)

    register_frame_return_button = tk.Button(
        register_frame,
        text="Exit",
        command=lambda: raise_frame(starting_frame),
        relief=GROOVE,
    )
    register_frame_return_button.place(rely=0.7, relx=0.52, width=50)

    ############################### SELECT ACCOUNT FRAME ########################################
    select_acc_frame_title = tk.Label(
        select_account_frame,
        text="Welcome to our ATM Machine App! Please select which account you would like to access.",
    )
    select_acc_frame_title.place(relx=0.13)

    select_acc_frame_checking_button = tk.Button(
        select_account_frame,
        text="Checking",
        command=lambda: raise_frame(main_checking_frame),
        relief=GROOVE,
    )
    select_acc_frame_checking_button.place(rely=0.4, relx=0.4, width=100)

    select_acc_frame_savings_button = tk.Button(
        select_account_frame,
        text="Savings",
        command=lambda: raise_frame(main_savings_frame),
        relief=GROOVE,
    )
    select_acc_frame_savings_button.place(rely=0.5, relx=0.4, width=100)

    select_acc_frame_sign_out_button = tk.Button(
        select_account_frame,
        text="Sign Out",
        command=lambda: [raise_frame(starting_frame), sign_out()],
        relief=GROOVE,
    )
    select_acc_frame_sign_out_button.place(rely=0.6, relx=0.4, width=100)

    ############################### MAIN SAVINGS FRAME ########################################
    main_s_frame_title = tk.Label(
        main_savings_frame,
        text="Welcome to our ATM Machine App! You have accessed your SAVINGS account.",
    )
    main_s_frame_title.place(relx=0.13)

    main_s_frame_check_bal_button = tk.Button(
        main_savings_frame,
        text="Check Balance",
        command=lambda: [
            raise_frame(savings_balance_frame),
            check_savings_balance(conn),
        ],
        relief=GROOVE,
    )
    main_s_frame_check_bal_button.place(rely=0.3, relx=0.3, width=100)

    main_s_frame_deposit_button = tk.Button(
        main_savings_frame,
        text="Deposit",
        command=lambda: [
            raise_frame(savings_deposit_frame),
            check_savings_balance(conn),
        ],
        relief=GROOVE,
    )
    main_s_frame_deposit_button.place(rely=0.3, relx=0.5, width=100)

    main_s_frame_withdraw_button = tk.Button(
        main_savings_frame,
        text="Withdraw",
        command=lambda: [
            raise_frame(savings_withdraw_frame),
            check_savings_balance(conn),
        ],
        relief=GROOVE,
    )
    main_s_frame_withdraw_button.place(rely=0.5, relx=0.3, width=100)

    main_s_frame_account_button = tk.Button(
        main_savings_frame,
        text="Accounts",
        command=lambda: raise_frame(select_account_frame),
        relief=GROOVE,
    )
    main_s_frame_account_button.place(rely=0.5, relx=0.5, width=100)

    main_s_frame_sign_out_button = tk.Button(
        main_savings_frame,
        text="Sign Out",
        command=lambda: [raise_frame(starting_frame), sign_out()],
        relief=GROOVE,
    )
    main_s_frame_sign_out_button.place(rely=0.7, relx=0.3, width=225)

    ############################### SAVINGS DEPOSIT FRAME ########################################
    savings_deposit_frame_title = tk.Label(
        savings_deposit_frame,
        text="Enter an amount to deposit into your savings account.",
    )
    savings_deposit_frame_title.place(relx=0.3)

    savings_deposit_frame_balance_label = tk.Label(
        savings_deposit_frame, text="Savings Balance"
    )
    savings_deposit_frame_balance_label.place(rely=0.3, relx=0.28)

    savings_deposit_frame_amount_entry = tk.Entry(savings_deposit_frame)
    savings_deposit_frame_amount_entry.place(rely=0.4, relx=0.4, width=110)

    savings_deposit_frame_amount_label = tk.Label(savings_deposit_frame, text="Amount")
    savings_deposit_frame_amount_label.place(rely=0.4, relx=0.28)

    savings_deposit_frame_deposit_button = tk.Button(
        savings_deposit_frame,
        text="Submit",
        command=lambda: savings_deposit(conn),
        relief=GROOVE,
    )
    savings_deposit_frame_deposit_button.place(rely=0.5, relx=0.4, width=50)

    savings_deposit_frame_exit_button = tk.Button(
        savings_deposit_frame,
        text="Menu",
        command=lambda: raise_frame(main_savings_frame),
        relief=GROOVE,
    )
    savings_deposit_frame_exit_button.place(rely=0.5, relx=0.5, width=50)

    ############################### SAVINGS WITHDRAW FRAME ########################################
    savings_withdraw_frame_title = tk.Label(
        savings_withdraw_frame,
        text="Enter an amount to be withdrawn from your savings account.",
    )
    savings_withdraw_frame_title.place(relx=0.3)

    savings_withdraw_frame_balance_label = tk.Label(
        savings_withdraw_frame, text="Savings Balance"
    )
    savings_withdraw_frame_balance_label.place(rely=0.3, relx=0.28)

    savings_withdraw_frame_amount_entry = tk.Entry(savings_withdraw_frame)
    savings_withdraw_frame_amount_entry.place(rely=0.4, relx=0.4, width=110)

    savings_withdraw_frame_amount_label = tk.Label(
        savings_withdraw_frame, text="Amount"
    )
    savings_withdraw_frame_amount_label.place(rely=0.4, relx=0.28)

    savings_withdraw_frame_withdraw_button = tk.Button(
        savings_withdraw_frame,
        text="Submit",
        command=lambda: savings_withdraw(conn),
        relief=GROOVE,
    )
    savings_withdraw_frame_withdraw_button.place(rely=0.5, relx=0.4, width=50)

    savings_withdraw_frame_exit_button = tk.Button(
        savings_withdraw_frame,
        text="Menu",
        command=lambda: raise_frame(main_savings_frame),
        relief=GROOVE,
    )
    savings_withdraw_frame_exit_button.place(rely=0.5, relx=0.5, width=50)

    ############################### SAVINGS BALANCE FRAME ########################################
    savings_balance_frame_title = tk.Label(
        savings_balance_frame, text="Thank you for using our ATM Machine App!"
    )
    savings_balance_frame_title.place(relx=0.3)

    savings_balance_frame_amount_label = tk.Label(
        savings_balance_frame, text="Savings Balance"
    )
    savings_balance_frame_amount_label.place(rely=0.4, relx=0.35)

    savings_balance_frame_exit_button = tk.Button(
        savings_balance_frame,
        text="Main Menu",
        command=lambda: raise_frame(main_savings_frame),
        relief=GROOVE,
    )
    savings_balance_frame_exit_button.place(rely=0.5, relx=0.35, width=150)

    ############################### MAIN CHECKING FRAME ########################################
    main_c_frame_title = tk.Label(
        main_checking_frame,
        text="Welcome to our ATM Machine App! You have accessed your CHECKING account.",
    )
    main_c_frame_title.place(relx=0.13)

    main_c_frame_check_bal_button = tk.Button(
        main_checking_frame,
        text="Check Balance",
        command=lambda: [
            raise_frame(checking_balance_frame),
            check_checking_balance(conn),
        ],
        relief=GROOVE,
    )
    main_c_frame_check_bal_button.place(rely=0.3, relx=0.3, width=100)

    main_c_frame_deposit_button = tk.Button(
        main_checking_frame,
        text="Deposit",
        command=lambda: [
            raise_frame(checking_deposit_frame),
            check_checking_balance(conn),
        ],
        relief=GROOVE,
    )
    main_c_frame_deposit_button.place(rely=0.3, relx=0.5, width=100)

    main_c_frame_withdraw_button = tk.Button(
        main_checking_frame,
        text="Withdraw",
        command=lambda: [
            raise_frame(checking_withdraw_frame),
            check_checking_balance(conn),
        ],
        relief=GROOVE,
    )
    main_c_frame_withdraw_button.place(rely=0.5, relx=0.3, width=100)

    main_c_frame_account_button = tk.Button(
        main_checking_frame,
        text="Accounts",
        command=lambda: raise_frame(select_account_frame),
        relief=GROOVE,
    )
    main_c_frame_account_button.place(rely=0.5, relx=0.5, width=100)

    main_c_frame_sign_out_button = tk.Button(
        main_checking_frame,
        text="Sign Out",
        command=lambda: [raise_frame(starting_frame), sign_out()],
        relief=GROOVE,
    )
    main_c_frame_sign_out_button.place(rely=0.7, relx=0.3, width=225)

    ############################### CHECKING DEPOSIT FRAME ########################################
    checking_deposit_frame_title = tk.Label(
        checking_deposit_frame,
        text="Enter an amount to deposit into your checking account.",
    )
    checking_deposit_frame_title.place(relx=0.25)

    checking_deposit_frame_balance_label = tk.Label(
        checking_deposit_frame, text="Checking Balance"
    )
    checking_deposit_frame_balance_label.place(rely=0.3, relx=0.28)

    checking_deposit_frame_amount_entry = tk.Entry(checking_deposit_frame)
    checking_deposit_frame_amount_entry.place(rely=0.4, relx=0.4, width=110)

    checking_deposit_frame_amount_label = tk.Label(
        checking_deposit_frame, text="Amount"
    )
    checking_deposit_frame_amount_label.place(rely=0.4, relx=0.28)

    checking_deposit_frame_deposit_button = tk.Button(
        checking_deposit_frame,
        text="Submit",
        command=lambda: checking_deposit(conn),
        relief=GROOVE,
    )
    checking_deposit_frame_deposit_button.place(rely=0.5, relx=0.4, width=50)

    checking_deposit_frame_exit_button = tk.Button(
        checking_deposit_frame,
        text="Menu",
        command=lambda: raise_frame(main_checking_frame),
        relief=GROOVE,
    )
    checking_deposit_frame_exit_button.place(rely=0.5, relx=0.5, width=50)

    ############################### CHECKING WITHDRAW FRAME ########################################
    checking_withdraw_frame_title = tk.Label(
        checking_withdraw_frame,
        text="Enter an amount to be withdrawn from your checking account.",
    )
    checking_withdraw_frame_title.place(relx=0.25)

    checking_withdraw_frame_balance_label = tk.Label(
        checking_withdraw_frame, text="Checking Balance"
    )
    checking_withdraw_frame_balance_label.place(rely=0.3, relx=0.28)

    checking_withdraw_frame_amount_entry = tk.Entry(checking_withdraw_frame)
    checking_withdraw_frame_amount_entry.place(rely=0.4, relx=0.4, width=110)

    checking_withdraw_frame_amount_label = tk.Label(
        checking_withdraw_frame, text="Amount"
    )
    checking_withdraw_frame_amount_label.place(rely=0.4, relx=0.28)

    checking_withdraw_frame_withdraw_button = tk.Button(
        checking_withdraw_frame,
        text="Submit",
        command=lambda: checking_withdraw(conn),
        relief=GROOVE,
    )
    checking_withdraw_frame_withdraw_button.place(rely=0.5, relx=0.4, width=50)

    checking_withdraw_frame_exit_button = tk.Button(
        checking_withdraw_frame,
        text="Menu",
        command=lambda: raise_frame(main_checking_frame),
        relief=GROOVE,
    )
    checking_withdraw_frame_exit_button.place(rely=0.5, relx=0.5, width=50)

    ############################### CHECKING BALANCE FRAME ########################################
    checking_balance_frame_title = tk.Label(
        checking_balance_frame, text="Thank you for using our ATM Machine App!"
    )
    checking_balance_frame_title.place(relx=0.3)

    checking_balance_frame_amount_label = tk.Label(
        checking_balance_frame, text="Checking Balance"
    )
    checking_balance_frame_amount_label.place(rely=0.4, relx=0.35)

    checking_balance_frame_exit_button = tk.Button(
        checking_balance_frame,
        text="Main Menu",
        command=lambda: raise_frame(main_checking_frame),
        relief=GROOVE,
    )
    checking_balance_frame_exit_button.place(rely=0.5, relx=0.35, width=150)

    root.mainloop()
