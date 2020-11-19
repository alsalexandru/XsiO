#! /usr/bin/env python3
import tkinter as tk
import socket
import threading

#Socket global variables
HOST = "0.0.0.0"
PORT = 65432
ADDR = (HOST, PORT)
FORMAT = "utf-8"
server = None

#Clients global variables
client_name = ""
clients = []
clients_names = []

startnew = [False, False]
resetscore = [False, False]

def start_server():
    global server
    start_btn.config(state = "disabled")
    stop_btn.config(state = "normal")
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)
    server.listen(2)
    print(f"[LISTENING] Server is listening on IP: {HOST}   PORT: {PORT}")
    thread = threading.Thread(target = accept_clients, args = (server,))
    thread.start()
    
def stop_server():
    start_btn.config(state = "normal")
    stop_btn.config(state = "disabled")
    server.close()

def accept_clients(server):
    while True:
        if len(clients) < 2:
            conn, addr = server.accept()
            clients.append(conn)
            thread = threading.Thread(target = manage_messages, args = (conn, addr))
            thread.start()
    
def manage_messages(conn, addr):
    global client_name, clients, startnew
    #receive client name
    client_name = conn.recv(2048).decode(FORMAT)
    clients_names.append(client_name) #append newplayer name to player list
    client_name_list(clients_names) #refresh player list in GUI

    #send welcome message
    if len(clients) < 2:
        conn.send(f"{clients_names[0]} you are Player1".encode(FORMAT))
    else:
        conn.send(f"{clients_names[1]} you are Player2".encode(FORMAT))

    if len(clients) > 1:
        symbols = ["X", "O"]
        clients[0].send(f"Playing against: {clients_names[1]}\nYour symbol is: {symbols[0]}".encode(FORMAT))
        clients[1].send(f"Playing against: {clients_names[0]}\nYour symbol is: {symbols[1]}".encode(FORMAT))

    while True:
        #get players move
        data = conn.recv(2048).decode(FORMAT)
        print(data)
        if not data:
            break
        #MOVES
        if data.startswith("xy"):
            if conn == clients[0]:
                clients[1].send(data.encode(FORMAT))
            else:
                clients[0].send(data.encode(FORMAT))
        #CHAT
        elif data.startswith("chat"):
            if conn == clients[0]:
                clients[1].send(data.encode(FORMAT))
            if conn == clients[1]:
                clients[0].send(data.encode(FORMAT))
        #NEWGAME        
        elif data == "newgame":
            if conn == clients[0]:
                startnew[0] = True
            else:
                startnew[1] = True           
        if all(startnew):
            clients[0].send("startnew".encode(FORMAT))
            clients[1].send("startnew".encode(FORMAT))
            startnew = [False, False]
            
    #remove player, close connection, update player list
    index = clients.index(conn)
    del clients[index]
    del clients_names[index]
    conn.close()
    client_name_list(clients_names)

#Update client list
def client_name_list(name_list):
    client_list.config(state="normal")
    client_list.delete("1.0", "end")

    for nume in name_list:
        client_list.insert("end", nume + "\n")
    client_list.config(state = "disabled")

main = tk.Tk()
main.resizable(0,0)
main.title("Server X si O")

#Top frame - buttons for starting and stopping server
top_frame = tk.Frame(main)
start_btn = tk.Button(top_frame, text="Start", command = start_server)
start_btn.pack(side = "left")
stop_btn = tk.Button(top_frame, text="Stop", state = "disabled", command = stop_server)
stop_btn.pack(side="left")
top_frame.pack(side="top", pady=(5, 0))

#Mid frame - Display HOST addr and PORT number
mid_frame = tk.Frame(main)
label_host = tk.Label(mid_frame, text = f"Address: {HOST}")
label_host.pack(side = "left")
label_port = tk.Label(mid_frame, text = f"PORT: {PORT}")
label_port.pack(side = "left")
mid_frame.pack(side = "top", pady = (5, 0))

#Client frame - showing client list
client_frame = tk.Frame(main)
title_lable = tk.Label(client_frame, text = "Client List").pack()
scroll = tk.Scrollbar(client_frame)
scroll.pack(side = "right", fill = "y")
client_list = tk.Text(client_frame, height = 10, width = 30)
client_list.pack(side = "left", fill = "y", padx = (5, 0))
scroll.config(command = client_list.yview)
client_list.config(yscrollcommand = scroll.set, background = "#F4F6F7", highlightbackground = "grey", state = "disabled")
client_frame.pack(side = "bottom", pady = (5, 10))

main.mainloop()
