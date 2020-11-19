import tkinter as tk
from tkinter import messagebox
import threading
import socket
import time
import datetime

#network variables
HOST = "0.0.0.0"
PORT = 65432
FORMAT = "utf-8"
ADDR = (HOST, PORT)
client = None

your_details = {"name": None, "symbol":None, "color":None, "score":0}
opponent_details = {"name": None, "symbol":None, "color":None, "score":0}

your_turn = False
you_started = False
buttons_list = []

draw = False

two_players = False

def startgame():
    global list_labels, your_turn, your_details, opponent_details, you_started, draw
    draw = False
    for i in range (9):
        buttons_list[i]["symbol"] = str(i)
        buttons_list[i]["button"]["text"] = " "
        buttons_list[i]["state"] = "normal"
        buttons_list[i]["button"].config(state = "normal", bg = "grey")

    turn_label.config(foreground="black")
    time.sleep(0.7)
    turn_label["text"] = "STATUS: Starting game."
    time.sleep(0.7)
    turn_label["text"] = "STATUS: Starting game.."
    time.sleep(0.7)
    turn_label["text"] = "STATUS: Starting game..."

    if you_started:
        you_started = False
        your_turn = False
        your_details["symbol"] = "O"
        opponent_details["symbol"] = "X"
        turn_label["text"] = "STATUS: " + opponent_details["name"] + "'s turn!"

    else:
        you_started = True
        your_turn = True
        your_details["symbol"] = "X"
        opponent_details["symbol"] = "O"
        turn_label["text"] = "STATUS: Your turn!"
        turn_label.config(foreground = "black")

def pressbutton(xy):    
    global client, your_turn, score_label1, score_label2
    btn_index = xy[0] * 3 + xy[1]
    buton = buttons_list[btn_index]
    if your_turn: 
        if buton["state"] == "normal":
            buton["button"].config(disabledforeground = your_details["color"], text = your_details["symbol"], state = "disabled")
            buton["state"] = "disabled"
            buton["symbol"] = your_details["symbol"]
            client.send(f"xy: {xy[0]}{xy[1]}".encode(FORMAT))
            your_turn = False

        result = checkwin()        
        if result is True:
            your_details["score"] = your_details["score"] + 1
            turn_label["text"] = "Game over, You Won!"
            turn_label.config(foreground = "green")
            score_label1.configure(text = f"{your_details['name']}: {your_details['score']}", foreground = your_details['color'])
            score_label2.configure(text = f"{opponent_details['name']}: {opponent_details['score']}", foreground = opponent_details['color'])
            answr = messagebox.askquestion("Game over!", "You won!\nPlay again?")
            if answr == "yes":
                client.send("newgame".encode(FORMAT))
                turn_label["text"] = f"Waiting for {opponent_details['name']}"
                turn_label.config(foreground = "red")

        elif draw == True:
            turn_label["text"] = "Game over, Draw!"
            turn_label.config(foreground = "blue")
            answr = messagebox.askquestion("Game over!", "Draw!\nPlay again?")
            if answr == "yes":
                client.send("newgame".encode(FORMAT))
                turn_label["text"] = f"Waiting for {opponent_details['name']}"
                turn_label.config(foreground = "red")
        else:
            turn_label["text"] = "STATUS: " + opponent_details["name"] + "'s turn"
            
    elif your_details["symbol"] == None:
        turn_label["text"] = "Wait for player2 to join"
        turn_label.config(foreground = "red")
    else:
        turn_label["text"] = "Wait for your turn!" 
        turn_label.config(foreground = "red")

def checkwin():
    global buttons_list, draw
    win = False
    wincolor = "#32CD32"
    losecolor = "red"
    #check rows
    for i in range (0, 9, 3):
        if buttons_list[i]["symbol"] == buttons_list[i+1]["symbol"] == buttons_list[i+2]["symbol"]:
            if buttons_list[i]["symbol"] == your_details["symbol"]:
                buttons_list[i]["button"].config(bg = wincolor)
                buttons_list[i+1]["button"].config(bg = wincolor)
                buttons_list[i+2]["button"].config(bg = wincolor)
            else:
                buttons_list[i]["button"].config(bg = losecolor)
                buttons_list[i+1]["button"].config(bg = losecolor)
                buttons_list[i+2]["button"].config(bg = losecolor)
            win = True
            break

    #check columns
    if win == False:
        for i in range(3):
            if buttons_list[i]["symbol"] == buttons_list[i+3]["symbol"] == buttons_list[i+6]["symbol"]:
                if buttons_list[i]["symbol"] == your_details["symbol"]:
                    buttons_list[i]["button"].config(bg = wincolor)
                    buttons_list[i+3]["button"].config(bg = wincolor)
                    buttons_list[i+6]["button"].config(bg = wincolor)
                else:
                    buttons_list[i]["button"].config(bg = losecolor)
                    buttons_list[i+3]["button"].config(bg = losecolor)
                    buttons_list[i+6]["button"].config(bg = losecolor)
                win = True
                break

    #check diagonals
    if win == False:
        if buttons_list[0]["symbol"] == buttons_list[4]["symbol"] == buttons_list[8]["symbol"]:
            if buttons_list[0]["symbol"] == your_details["symbol"]:
                buttons_list[0]["button"].config(bg = wincolor)
                buttons_list[4]["button"].config(bg = wincolor)
                buttons_list[8]["button"].config(bg = wincolor)
            else:
                buttons_list[0]["button"].config(bg = losecolor)
                buttons_list[4]["button"].config(bg = losecolor)
                buttons_list[8]["button"].config(bg = losecolor)
            win = True
        elif buttons_list[2]["symbol"] == buttons_list[4]["symbol"] == buttons_list[6]["symbol"]:
            if buttons_list[2]["symbol"] == your_details["symbol"]:
                buttons_list[2]["button"].config(bg = wincolor)
                buttons_list[4]["button"].config(bg = wincolor)
                buttons_list[6]["button"].config(bg = wincolor)
            else:
                buttons_list[2]["button"].config(bg = losecolor)
                buttons_list[4]["button"].config(bg = losecolor)
                buttons_list[6]["button"].config(bg = losecolor)
            win = True

    #check draw
    btn_state = []
    if win == False:
        for i in range(9):
            if buttons_list[i]["state"] == "disabled":
                btn_state.append(True)
            else:
                btn_state.append(False)
        if all(btn_state):
            draw = True

    if win == True:
        for i in range(9):
            buttons_list[i]["button"].config(state = "disabled")

    return win


def send():
    global chatmsg, row
    import time
    if two_players:
        if 1 < len(sendmsg.get('1.0', '10.100')) < 502:
            time = datetime.datetime.now().strftime("%H:%M:%S")
            chatmsg.config(state = "normal")
            chatmsg.insert("end", f"<{time}> {your_details['name']}: {sendmsg.get('1.0', '10.100')}")
            
            #CHANGE TIMESTAMP COLOR
            
            #GO FROM END(THE EXTRA NEWLINE THAT TKINTER ADDS - BACK UP ONE CHARACTER TO GET LAST LINE INDEX)
            line_index = (int(chatmsg.index('end-1c').split('.')[0])) - 1
            
            chatmsg.tag_add(f"{line_index}", f"{line_index}.0", f"{line_index}.10") #(name, start, end)
            chatmsg.tag_config(f"{line_index}", foreground = "grey")
            #CHANGE NAME COLOR
            nameindex = 11 + len(your_details["name"])
            chatmsg.tag_add(f"{line_index} + X", f"{line_index}.11", f"{line_index}.{nameindex}")
            chatmsg.tag_config(f"{line_index} + X", foreground = your_details['color'])
            
            mesaj = "chat" + sendmsg.get("1.0", "500.500")
            client.send(mesaj.encode(FORMAT))
            sendmsg.delete("1.0", "end")
            chatmsg.see("end")
            chatmsg.config(state = "disabled")
        else:
            tk.messagebox.showwarning(title = "Message too long", message = "Please limit your message to 500 characters")
    else:
        tk.messagebox.showwarning(title = "You're all alone", message = "Wait for opponent...")
        
def connect():
    global client
    if 2 < len(enter_name.get()) < 11:
        your_details["name"] = enter_name.get() 
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(ADDR)
        client.send(enter_name.get().encode(FORMAT)) #send name
        #start client thread to keep receiving messages from server
        thread = threading.Thread(target = manage_messages, args = (client,))
        thread.start()
        frame.pack_forget() #close name window
        game.pack(side = "left")
        root.bind("<Return>", sendbyenter)
        entirechat.pack(side = "right")
        chat.pack(side = "top")
        newmsg.pack(side = "bottom")
        root.config(menu = menubar)
        root.title(f"X si O Client - {your_details['name']}")
    else:
        tk.messagebox.showerror(title = "Name not eligible", message = "Your name must be between 3 and 10 letters")

def sendbyenter(a):
    sendmsg.delete("end-1c", "end")
    send()

def manage_messages(client):
    global your_details, opponent_details, your_turn, you_started, score_label1, score_label2, chatmsg, two_players
    while True:
        msg = client.recv(2048).decode(FORMAT)
        print(msg)
        if not msg:
            break
        
        #check if msg is welcome message
        if "Player" in msg:
            if "Player1" in msg:
                your_details["color"] = "purple"
                opponent_details["color"] = "#ff2e02"
                turn_label["text"] = f"Server: Welcome {your_details['name']}! Waiting for player 2"
            elif "Player2" in msg:
                turn_label["text"] = f"Server: Welcome {your_details['name']}! Game will start soon"
                your_details["color"] = "#ff2e02"
                opponent_details["color"] = "purple"
        #check if its 2nd message (my symbol) (opponent name)
        elif "Playing" in msg:
            two_players = True
            index = msg.find("Your symbol is:")
            opponent_details["name"] = msg[17:index-1]
            your_details["symbol"] = msg[-1]
            score_label1.configure(text = f"{your_details['name']}: {your_details['score']}", foreground = your_details['color'])
            score_label2.configure(text = f"{opponent_details['name']}: {opponent_details['score']}", foreground = opponent_details['color'])            
            if your_details["symbol"] == "X":
                opponent_details["symbol"] = "O"
            else:
                opponent_details["symbol"] = "X"                
            turn_label["text"] = f"Server: {opponent_details['name']} is connected!"
            
            if your_details["symbol"] == "X":
                turn_label["text"] = "STATUS: Your turn!"
                turn_label.config(foreground = "black")
                your_turn = True
                you_started = True
            else:
                turn_label["text"] = f"STATUS: {opponent_details['name']}'s turn!"
                your_turn = False
                you_started = False
        elif msg.startswith("xy"):
            x = msg[-2]
            y = msg[-1]
            btn_index = int(x) * 3 + int(y)
            buton = buttons_list[btn_index]
            buton["symbol"] = opponent_details["symbol"]
            buton["state"] = "disabled"
            buton["button"].config(text = opponent_details["symbol"], state = "disabled", disabledforeground = opponent_details["color"])
            result = checkwin()
            if result is True:
                opponent_details["score"] = opponent_details["score"] + 1
                turn_label["text"] = "Game over, You Lost!"
                turn_label.config(foreground="red")
                score_label1.configure(text = f"{your_details['name']}: {your_details['score']}", foreground = your_details['color'])
                score_label2.configure(text = f"{opponent_details['name']}: {opponent_details['score']}", foreground = opponent_details['color'])
                answr = messagebox.askquestion("Game over!", "You lost!\nPlay again?")
                if answr == "yes":
                    client.send("newgame".encode(FORMAT))
                    turn_label["text"] = f"Waiting for {opponent_details['name']}"
                    turn_label.config(foreground = "red")
                #thread = threading.Thread(target = startgame)
                #thread.start()
            elif draw == True:
                turn_label["text"] = "Game over, Draw!"
                turn_label.config(foreground="blue")
                answr = messagebox.askquestion("Game over!", "Draw!\nPlay again?")
                if answr == "yes":
                    client.send("newgame".encode(FORMAT))
                    turn_label["text"] = f"Waiting for {opponent_details['name']}"
                    turn_label.config(foreground = "red")
                #thread = threading.Thread(target = startgame)
                #thread.start()
            else:
                your_turn = True
                turn_label["text"] = "STATUS: Your turn!"
                turn_label.config(foreground="black")
                
        elif msg.startswith("chat"):
            if your_details["symbol"] != None:
                chatmsg.config(state = "normal")
                time = datetime.datetime.now().strftime("%H:%M:%S")
                chatmsg.insert("end", f"<{time}> {opponent_details['name']}: {msg[4:]}")
                
                #CHANGE TIMESTAMP COLOR
                line_index = (int(chatmsg.index('end-1c').split('.')[0])) - 1
                print(line_index)
                chatmsg.tag_add(f"{line_index}", f"{line_index}.0", f"{line_index}.10")
                chatmsg.tag_config(f"{line_index}", foreground = "grey")
                #CHANGE NAME COLOR
                nameindex = 11 + len(opponent_details["name"])
                chatmsg.tag_add(f"{line_index} + X", f"{line_index}.11", f"{line_index}.{nameindex}")
                chatmsg.tag_config(f"{line_index} + X", foreground = opponent_details['color'])
                
                chatmsg.see("end")
                chatmsg.config(state = "disabled")

        elif msg == "startnew":
            startgame()
           
    client.close()

def about():
    msg = messagebox.showinfo("About", "Created by Alex.")

def leavegame():
    msg = messagebox.askquestion("Quit?", "Are you sure about this?")
    if msg == "yes":
        client.close()
        root.destroy()
        quit()

#main window
root = tk.Tk()
root.resizable(0,0)
root.title("X si O Client")

#enter name frame
frame = tk.Frame(root)
name_label = tk.Label(frame, text = "Name: ")
name_label.pack(side = "left")
enter_name = tk.Entry(frame)
enter_name.pack(side = "left")
connect_button = tk.Button(frame, text = "Connect", command = connect)
connect_button.pack(side = "left")
frame.pack(side = "top")

#game frame
game = tk.Frame(root)

#menus
menubar = tk.Menu(root)
filemenu = tk.Menu(menubar, tearoff = 0)
menubar.add_cascade(label = "File", menu = filemenu)
filemenu.add_separator()
filemenu.add_command(label="Exit", command = leavegame)
menubar.add_command(label="About", command = about)

#create buttons
image = tk.PhotoImage(width=1, height=1)

i = 0
for x in range(3):
    for y in range(3):
        btn = tk.Button(game, relief= "flat", bg = "grey", image = image, text = " ", font = "Arial 65 bold", 
                        width = 100, height = 100, compound= "c", state = "normal", 
                        command = lambda xy = [x,y] : pressbutton(xy))
        btn.grid(row = x, column = y)

        dict_btn = {"xy": [x, y], "symbol": str(i), "button": btn, "state": "normal"}
        buttons_list.append(dict_btn)
        i = i + 1

#turn label
turn_label = tk.Label(game, text = "Status: Waiting for opponent")
turn_label.grid(row = 3, columnspan = 3)

#score label
score_label = tk.Label(game, text = f"Score:  ")
score_label.grid(row = 4, column = 0)

score_label1 = tk.Label(game)
score_label1.grid(row = 4, column = 1)

score_label2 = tk.Label(game)
score_label2.grid(row = 4, column = 2)

entirechat = tk.Frame(root)
#chat frame
chat = tk.Frame(entirechat)
chatmsg = tk.Text(chat, height = 20, width = 40, state = "disabled")
scrollchat = tk.Scrollbar(chat)
scrollchat.pack(side = "right", fill = "y")
chatmsg.pack()
scrollchat.config(command = chatmsg.yview)
chatmsg.config(yscrollcommand = scrollchat.set)

#new messages frame
newmsg = tk.Frame(entirechat)
sendmsg = tk.Text(newmsg, height = 2, width = 34)
sendmsg.pack(side = "left")
sendbtn = tk.Button(newmsg, height = 1, width = 4, text = "SEND", command = send)
sendbtn.pack(side = "right")

root.mainloop()
