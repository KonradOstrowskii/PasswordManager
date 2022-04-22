
from tkinter import *
from tkinter import messagebox
from functools import partial
from tkinter import ttk
import tkinter
import uuid
import pyperclip
import base64
from popUp import *
from datebase import *
from hash import *
import random

window = Tk()
window.update()

window.title("Password Vault")
def firstTimeScreen():
    for widget in window.winfo_children():
        widget.destroy()

    window.geometry('250x125')
    lbl = Label(window, text="Choose a Master Password")
    lbl.config(anchor=CENTER)
    lbl.pack()

    txt = Entry(window, width=20, show="*")
    txt.pack()
    txt.focus()

    lbl1 = Label(window, text="Re-enter password")
    lbl1.config(anchor=CENTER)
    lbl1.pack()

    txt1 = Entry(window, width=20, show="*")
    txt1.pack()

    def savePassword():
        if txt.get() == txt1.get():
            sql = "DELETE FROM masterpassword WHERE id = 1"

            cursor.execute(sql)

            hashedPassword = hashPassword(txt.get().encode('utf-8'))
            key = str(uuid.uuid4().hex)
            recoveryKey = hashPassword(key.encode('utf-8'))

            global encryptionKey
            encryptionKey = base64.urlsafe_b64encode(kdf.derive(txt.get().encode()))
            
            insert_password = """INSERT INTO masterpassword(password, recoveryKey)
            VALUES(?, ?) """
            cursor.execute(insert_password, ((hashedPassword), (recoveryKey)))
            db.commit()

            recoveryScreen(key)
        else:
            lbl.config(text="Passwords aint correct")

    btn = Button(window, text="Save", command=savePassword)
    btn.pack(pady=5)

def resetScreen():
    for widget in window.winfo_children():
        widget.destroy()

    window.geometry('250x125')
    lbl = Label(window, text="Enter Recovery Key")
    lbl.config(anchor=CENTER)
    lbl.pack()

    txt = Entry(window, width=20)
    txt.pack()
    txt.focus()

    lbl1 = Label(window)
    lbl1.config(anchor=CENTER)
    lbl1.pack()

    def getRecoveryKey():
        recoveryKeyCheck = hashPassword(str(txt.get()).encode('utf-8'))
        cursor.execute('SELECT * FROM masterpassword WHERE id = 1 AND recoveryKey = ?', [(recoveryKeyCheck)])
        return cursor.fetchall()

    def alert():
       messagebox.showwarning("Alert","Wrong Key")

    def checkRecoveryKey():
        checked = getRecoveryKey()

        if checked:
            firstTimeScreen()
        else:
            txt.delete(0, 'end')
            alert()

    btn = Button(window, text="Check Key", command=checkRecoveryKey)
    btn.pack(pady=5)

def recoveryScreen(key):
    for widget in window.winfo_children():
        widget.destroy()

    window.geometry('250x125')
    lbl = Label(window, text="Save this key to be able to recover account")
    lbl.config(anchor=CENTER)
    lbl.pack()

    lbl1 = Label(window, text=key)
    lbl1.config(anchor=CENTER)
    lbl1.pack()

    def copyKey():
        pyperclip.copy(lbl1.cget("text"))

    btn = Button(window, text="Copy Key", command=copyKey)
    btn.pack(pady=5)

    def done():
        vaultScreen()

    btn = Button(window, text="Done", command=done)
    btn.pack(pady=5)

def loginScreen():
        for widget in window.winfo_children():
            widget.destroy()

        window.geometry('250x125')

        lbl = Label(window, text="Enter  Master Password")
        lbl.config(anchor=CENTER)
        lbl.pack()

        txt = Entry(window, width=20, show="*")
        txt.pack()
        txt.focus()

        lbl1 = Label(window)
        lbl1.config(anchor=CENTER)
        lbl1.pack(side=TOP)

        def getMasterPassword():
            checkHashedPassword = hashPassword(txt.get().encode('utf-8'))
            global encryptionKey
            encryptionKey = base64.urlsafe_b64encode(kdf.derive(txt.get().encode()))
            cursor.execute('SELECT * FROM masterpassword WHERE id = 1 AND password = ?', [(checkHashedPassword)])
            return cursor.fetchall()

        def checkPassword():
            password = getMasterPassword()

            if password:
                vaultScreen()
            else:
                txt.delete(0, 'end')
                lbl1.config(text="Wrong Password")
        
        def resetPassword():
            resetScreen()

        btn = Button(window, text="Submit", command=checkPassword)
        btn.pack(pady=5)

        btn = Button(window, text="Reset Password", command=resetPassword)
        btn.pack(pady=5)

def vaultScreen():
    for widget in window.winfo_children():
        widget.destroy()

    def addEntry():
        text1 = "Website"
        text2 = "Username"
        text3 = "Password"
        website = encrypt(popUpWeb(text1).encode(), encryptionKey)
        username = encrypt(popUpUser(text2).encode(), encryptionKey)
        password = encrypt(popUpPass(text3).encode(), encryptionKey)

        insert_fields = """INSERT INTO vault(website, username, password) 
        VALUES(?, ?, ?) """
        cursor.execute(insert_fields, (website, username, password))
        db.commit()

        vaultScreen()

    def removeEntry(input):
        cursor.execute("DELETE FROM vault WHERE id = ?", (input,))
        db.commit()
        vaultScreen()

    def passwordGenerator():
            inints = range(32, 127)

            password = ''

            for i in range(15):
                password += chr(random.choice(inints))

            lbl = Label(window, text=password)
            lbl.config(anchor=CENTER)
            lbl.grid()

            def copyPw():
                pyperclip.copy(lbl.cget("text"))

            btn = Button(window, text="Copy", command=copyPw)
            btn.grid(pady=5)

    def info():
        tkinter.messagebox.showinfo(title="information", message="Automatically generate password from 15 char")

    window.geometry('800x550')
    notebook = ttk.Notebook(window)
    window.resizable(height=None, width=None)
    lbl = Label(window, text="Password Vault",anchor=CENTER)
    lbl.grid(column=0)
    tab1 = Frame(notebook)
    notebook.add(tab1,text="BLOCKCHAIN")
   
    notebook.grid()

    btn = Button(window, text="Add Information", command=addEntry)
    btn.grid(column=0 ,row=0)

    btn = Button(window, text="PwGenerator", command=passwordGenerator)
    btn.grid(column=2 ,row=1)
    btn = Button(window, text="?", command=info)
    btn.grid(column=3 ,row=1)


    lbl = Label(tab1, text="Website")
    lbl.grid(row=2, column=0, padx=80)
    lbl = Label(tab1, text="Username")
    lbl.grid(row=2, column=1, padx=80)
    lbl = Label(tab1, text="Password")
    lbl.grid(row=2, column=2, padx=80)

    cursor.execute('SELECT * FROM vault')
    if (cursor.fetchall() != None):
        i = 0
        while True:
            cursor.execute('SELECT * FROM vault')
            array = cursor.fetchall()

            if (len(array) == 0):
                break

            lbl1 = Label(tab1, text=(decrypt(array[i][1], encryptionKey)), font=("Helvetica", 12))
            lbl1.grid(column=0, row=(i+3))
            lbl2 = Label(tab1, text=(decrypt(array[i][2], encryptionKey)), font=("Helvetica", 12))
            lbl2.grid(column=1, row=(i+3))
            lbl3 = Label(tab1, text=(decrypt(array[i][3], encryptionKey)), font=("Helvetica", 12))
            lbl3.grid(column=2, row=(i+3))

            btn = Button(tab1, text="Delete", command=  partial(removeEntry, array[i][0]))
            btn.grid(column=3, row=(i+3), pady=10)

            i = i +1

            cursor.execute('SELECT * FROM vault')
            if (len(cursor.fetchall()) <= i):
                break


cursor.execute('SELECT * FROM masterpassword')
if (cursor.fetchall()):
    loginScreen()
else:
    firstTimeScreen()
window.mainloop()