from tkinter import *
from settings import *
from state_manager import *
from game_class import *
from cryptohash import sha256
import sqlite3

username=""
password=""

# WINDOW_SIZE/2 = 340
#font sizes
fs_title1=30
fs_title2=20
fs_title3=15
fs_title4=10
fs_entry=8

win2 = None
menu = None
lb = None

def add_state(state):
   state_manager.states.append(state)

def back_state():
   state_manager.states.pop()

def tohexstr(rgb):
   return '#%02x%02x%02x' % rgb

# def createpage(root, wind, title, yoffset, xoffset):
#    wind.resizable(False,False)
#    l1 = Label(wind, text=title, font=(MENUFONT, fs_title1))
#    if title == "Register":
#       wind.geometry(str(600)+"x"+str(420))
#       l1.place(x=WINDOW_SIZE/2, y=255, anchor="center")
#    elif title == "Main Menu":
#       wind.geometry(str(WINDOW_SIZE)+"x"+str(WINDOW_SIZE))
#       l1.pack(padx=10, pady=10)
#       wind.protocol("WM_DELETE_WINDOW", lambda: close_page(root))

def new_default_page(root, wind, isTerminal, title, width, height, titlepos):
   wind.resizable(False,False)
   wind.geometry(str(width)+"x"+str(height))
   wind["bg"] = tohexstr(DARKGREY)
   l1 = Label(wind, text=title, font=(MENUFONT, fs_title1), bg=tohexstr(DARKGREY), fg=tohexstr(WHITE))
   l1.place(x=titlepos[0], y=titlepos[1], anchor="center")
   if isTerminal:
      wind.protocol("WM_DELETE_WINDOW", lambda: close_page(root))
   
def showmenu(r):
   r.deiconify()

def create_register_page(root):
   global win2
   win2 = Toplevel()
   pagewidth = 600
   pageheight = 420

   new_default_page(root, win2, False, "Register", pagewidth, pageheight, [pagewidth/2, 105])

   # register page specific code here
   l1 = Label(win2, text="Username:", font=(MENUFONT, fs_entry), bg=tohexstr(DARKGREY), fg=tohexstr(WHITE))
   l1.place(x=201, y=147)

   l2 = Label(win2, text="Password:", font=(MENUFONT, fs_entry), bg=tohexstr(DARKGREY), fg=tohexstr(WHITE))
   l2.place(x=200, y=168)

   l3 = Label(win2, text="Re-enter password:", font=(MENUFONT, fs_entry), bg=tohexstr(DARKGREY), fg=tohexstr(WHITE))
   l3.place(x=154, y=189)

   e1 = Entry(win2, width=24, font=(MENUFONT, fs_entry), bg=tohexstr(LIGHTGREY), border=0)
   e1.place(x=261, y=148)

   e2 = Entry(win2, width=24, font=(MENUFONT, fs_entry), bg=tohexstr(LIGHTGREY), border=0)
   e2.place(x=261, y=169)

   e3 = Entry(win2, width=24, font=(MENUFONT, fs_entry), bg=tohexstr(LIGHTGREY) , border=0)
   e3.place(x=261, y=191)

   status = Label(win2, text="Enter your desired username and password", font=(MENUFONT, fs_entry), fg=tohexstr(RED), bg=tohexstr(DARKGREY))
   status.place(x=295, y=225, anchor="center")


   b1 = Button(win2, text="Register",command= lambda: [check_details(root, "Register", status, e1, e2, e3), add_state("register")])
   b1.place(x=295, y=255, anchor="center")

   exit = Button(win2, text="Back", command= lambda: close_page(win2))
   exit.place(x=295, y=290, anchor="center")   
             
def check_details(root, page, statuslabel, user, pas, conf):
   encryptpw = sha256(pas.get())
   if page == "Login":
      with sqlite3.connect("useraccounts.db") as db: 
         cursor = db.cursor() 
      search_user = ("SELECT * FROM accounts WHERE username = ? AND password = ?")
      cursor.execute(search_user,[(user.get()),(encryptpw)]) 
      search_results = cursor.fetchall() 

      if search_results or (user.get() == "admin" and pas.get() == "admin"):
         # hide root window(login menu window)
         root.withdraw()

         # go to main menu
         add_state("main menu")
         create_main_menu(root, user.get())
      else:
         statuslabel.config(text= "Invalid username and/or password")

   elif page == "Register":
      invalidchlist = [" ", "  ", ",", "#", "@", "[", "]", "=", "+", "(", ")", "!"]

      if pas.get() == "" or user.get() == "" or conf.get() == "":
         statuslabel.config(text= "Enter your username and password")

      elif len(user.get()) < 5:
         statuslabel.config(text= "Username is too short")
      elif len(pas.get()) < 5:
         statuslabel.config(text= "Password is too short")

      elif invalidchars(invalidchlist, user.get()) or invalidchars(invalidchlist, pas.get()):
         statuslabel.config(text= "Invalid characters in username or password")
      elif pas.get() != conf.get():
         statuslabel.config(text= "Passwords do not match")

      else:
         createAccount(user.get(), encryptpw, statuslabel)


def invalidchars(invlist, teststr):
   for char in invlist:
      if char in teststr:
         return True

def close_page(window):
   window.destroy()
   back_state()

def create_main_menu(root, un):

   global menu
   menu = Toplevel()
   menu.resizable(False,False)

   new_default_page(root, menu, True, "Main Menu", WINDOW_SIZE, WINDOW_SIZE, [WINDOW_SIZE/2, 40])

   b1 = Button(menu, text="Play", font=(MENUFONT, 17), command= lambda: [start_new_game(), add_state("game")], width=22, height=5, border=7, fg=tohexstr(DARKGREY), bg=tohexstr(GREY))
   b1.place(x=(WINDOW_SIZE/2), y=250, anchor="center")
   b2 = Button(menu, text="Leaderboard", font=(MENUFONT, 17), command= lambda: [create_leaderboard(root, un), add_state("leaderboard")], width=22, height=5, border=7, fg=tohexstr(DARKGREY), bg=tohexstr(GREY))
   b2.place(x=(WINDOW_SIZE/2), y=460, anchor="center")
   exit = Button(menu, text="Log out", command=lambda: [close_page(menu), showmenu(root)])
   exit.place(x=0, y=0)




def create_leaderboard(root, un):
   global lb
   xspace = 160
   yspace = 2
   numnames = 10


   lb = Toplevel()
   lb.resizable(False, False)
   

   new_default_page(root, lb, False, "Leader Board", WINDOW_SIZE, WINDOW_SIZE, [WINDOW_SIZE/2, 60])

   lb.protocol("WM_DELETE_WINDOW", lambda: [close_page(lb)])
   
   subtitle = Label(lb, text="Top 10 scores", font=(MENUFONT, fs_title2), bg=tohexstr(DARKGREYHIGHLIGHT), fg=tohexstr(WHITE), border=10)
   subtitle.place(anchor="center", x=WINDOW_SIZE/2, y= 160)

   unframe = Frame(lb, bg=tohexstr(DARKGREY))
   unframe.place(anchor="nw", x=300 - xspace, y=205)

   pwframe = Frame(lb, bg=tohexstr(DARKGREY))
   pwframe.place(anchor="nw", x=300 + xspace, y=205)

   with sqlite3.connect("useraccounts.db") as db: 
      cursor = db.cursor() 
   search_user = ("SELECT * FROM accounts ORDER BY highscore DESC;")
   cursor.execute(search_user) 
   search_results = cursor.fetchall()

   for count, record in enumerate(search_results):
      if count < numnames:   
         details = list(record)
         n = Label(unframe, text=details[0], font=(MENUFONT, fs_title3), fg=tohexstr(WHITE), bg=tohexstr(DARKGREY))
         n.pack(anchor="nw", pady=yspace)

   for count, record in enumerate(search_results):
      if count < numnames:
         details = list(record)
         s = Label(pwframe, text=details[2], font=(MENUFONT, fs_title3), fg=tohexstr(WHITE), bg=tohexstr(DARKGREY), anchor="e")
         s.pack(anchor="ne", pady=yspace)

   avgscore = ("SELECT AVG(highscore) FROM accounts")
   cursor.execute(avgscore)
   avg = cursor.fetchone()
   currentuser = ("SELECT highscore FROM accounts WHERE username = ?")
   cursor.execute(currentuser, [un])
   userhighscore = cursor.fetchone()

   msg = ""
   
   try:
      perc = (list(userhighscore)[0]/list(avg)[0]) * 100

      if perc == 100:
         msg = "Your highscore is higher than 50 % of players on this device"
      elif perc > 100:
         msg = "Your highscore is " + str(int(perc) - 100) + " % higher than the average player on this device"
      elif perc < 100:
         msg = "Your highscore is " + str(round((100 - perc), 2)) + " % lower than the average player on this device"
   except:
      pass

   
   
   message = Label(unframe, text = msg, font=(MENUFONT, fs_title4), fg=tohexstr(DEEPORANGE), bg=tohexstr(DARKGREY), wraplength=400)
   message.pack(side="top", pady=40, padx=3)

   
      

  
# updates the states stack and runs the code for the new top state
# def switch_state(isGoingBack, stateToGo):
#    if isGoingBack:
#       state_manager.states.pop()
#    else:
#       state_manager.states.append(stateToGo)

#    if state_manager.states[-1] == "login":
#       # run instance of menu
#       pass
#    elif state_manager.states[-1] == "register":
#       # run instance of register menu
#       pass
#    elif state_manager.states[-1] == "leaderboard":
#       # run instance of leaderboard menu
#       pass
#    elif state_manager.states[-1] == "main menu":
#       # run instance of main menu
#       pass
#    elif state_manager.states[-1] == "game":
#       a = Game()
#       a.run()


def start_new_game():
   Game()
   

def initDB(): 
   with sqlite3.connect("useraccounts.db") as db: 
       cursor = db.cursor()
   cursor.execute(''' 
   CREATE TABLE IF NOT EXISTS accounts(
     username TEXT, 
     password TEXT,
     highscore INT)
   ''')

def createAccount(name, pw, statuslabel):
   with sqlite3.connect("useraccounts.db") as db: 
       cursor = db.cursor()
   cursor.execute("SELECT username FROM accounts WHERE username = ?",(name,)) 
   if cursor.fetchone() != None: 
       statuslabel.config(text= "Username taken")
       #createAccount(name, pw) 
   else: 
       cursor.execute(""" 
       INSERT INTO accounts(username,password,highscore) 
       VALUES(?,?,0) 
       """,(name,pw,)) 
       statuslabel.config(text="Account successfully created")
       db.commit() 
       db.close() 


def main():
   initDB()
   root = Tk()
   root["bg"] = tohexstr(DARKGREY)
   root.bind('<Escape>', lambda e: root.destroy())
   root.title("Tower Breach")
   root.geometry(str(WINDOW_SIZE)+"x"+str(WINDOW_SIZE))
   root.resizable(False,False)
   l1 = Label(root, text="Tower Breach", font=(MENUFONT, fs_title1), bg=tohexstr(DARKGREY), fg=tohexstr(WHITE))
   l1.pack(pady=25)


   loginf = LabelFrame(root, padx=10, pady=0, bg=tohexstr(DARKGREY))
   loginf.place(anchor="center", x=340, y=290)

   titleframe = Frame(loginf, bg=tohexstr(DARKGREY))
   titleframe.pack()

   l2frame = Frame(loginf, bg=tohexstr(DARKGREY))
   l2frame.pack(side="top")

   l3frame = Frame(loginf, bg=tohexstr(DARKGREY))
   l3frame.pack(side="top")

   l4frame = Frame(loginf, bg=tohexstr(DARKGREY))
   l4frame.pack(side="top")

   l5frame = Frame(loginf, bg=tohexstr(DARKGREY))
   l5frame.pack(side="top")

   title = Label(titleframe, text="Login", font=(MENUFONT, fs_title2), bg=tohexstr(DARKGREY), fg=tohexstr(WHITE))
   title.pack(pady=15)

   l1 = Label(l2frame, text="Username: ", font=(MENUFONT, fs_entry), bg=tohexstr(DARKGREY), fg=tohexstr(WHITE))
   l1.pack(side="left")
   e1 = Entry(l2frame, border=0, width=20, font=(MENUFONT, fs_entry), bg=tohexstr(LIGHTGREY))
   e1.pack(side="left", padx=2)

   l2 = Label(l3frame, text="Password: ", font=(MENUFONT, fs_entry), bg=tohexstr(DARKGREY), fg=tohexstr(WHITE))
   l2.pack(side="left", pady=4)
   e2 = Entry(l3frame, border=0, width=20, font=(MENUFONT, fs_entry), bg=tohexstr(LIGHTGREY), show="*")
   e2.pack(side="left", padx=1)

   status = Label(l4frame, text="Welcome to Tower Breach", font=(MENUFONT, fs_entry), fg=tohexstr(RED), bg=tohexstr(DARKGREY), wraplength=190)
   status.pack(side="left", pady=0)

   b1 = Button(l5frame, text="Enter",command= lambda: [check_details(root, "Login", status, e1, e2, None)], borderwidth=3)
   b1.pack(side="top", pady=5)

   b1 = Button(root, text="Register",command=lambda : create_register_page(root), height=2, width=8, borderwidth=6, fg=tohexstr(DARKGREY), bg=tohexstr(GREY), font=(MENUFONT, 16))
   b1.place(anchor="center", x=340, y=460)

   root.mainloop()

main()