import customtkinter
import socket
import threading
import confidential

window = customtkinter.CTk()
window.title("Client")
username = " "

top_frame = customtkinter.CTkFrame(master=window)
Namelbl = customtkinter.CTkLabel(master=top_frame, text="Name:")
Nameent = customtkinter.CTkEntry(master=top_frame)
Connectbtn = customtkinter.CTkButton(master=top_frame, text="Connect", command=lambda : connect())
Namelbl.grid(row=0, column=1, padx=(10, 10))
Nameent.grid(row=0, column=2, padx=(10, 10), pady=10)
Connectbtn.grid(row=2, column=1, columnspan=2, padx=20, pady=10)
top_frame.grid(row=0, column=0, padx=20, pady=20)

displayFrame = customtkinter.CTkFrame(master=window, width=400)
Display = customtkinter.CTkTextbox(master=displayFrame, width=400, height=400)
Display.configure(state=customtkinter.DISABLED)
displayFrame.grid(row=1, column=0, padx=20, pady=(0,20))
Display.grid(row=0, column=0, padx=20, pady=20)

bottomFrame = customtkinter.CTkFrame(master=window)
Message = customtkinter.CTkTextbox(bottomFrame, height=2, width=440)
Message.configure(state=customtkinter.DISABLED)
Message.bind("<Return>", (lambda event: getChatMessage(Message.get("1.0", customtkinter.END))))
Message.grid(row=0, column=0)
bottomFrame.grid(row=2, column=0, padx=20, pady=(0,20))

# network client
client = None
HOST_ADDR = confidential.HOST_ADDR
HOST_PORT = confidential.HOST_PORT

def showerror(text):
    errorbox = customtkinter.CTkToplevel()
    errorbox.title("ERROR!!!")
    errorbox.resizable(False, False)
    errorframe = customtkinter.CTkFrame(master=errorbox)
    errorframe.grid(row=0, column=0)
    errorlbl = customtkinter.CTkLabel(master=errorframe, text=text)
    errorlbl.grid(row=0, column=0, padx=20, pady=20)
    errorbtn = customtkinter.CTkButton(master=errorframe, text="OK", command=errorbox.destroy)
    errorbtn.grid(row=1, column=0, padx=20, pady=20)
    errorbox.grab_set()

def connect():
    global username, client
    if len(Nameent.get()) < 1:
        showerror("You MUST enter your first name <e.g. John>")
    else:
        username = Nameent.get()
        connect_to_server(username)

def connect_to_server(name):
    global client, HOST_PORT, HOST_ADDR
    try:
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((HOST_ADDR, HOST_PORT))
        client.send(name.encode()) # Send name to server after connecting

        Nameent.configure(state=customtkinter.DISABLED)
        Connectbtn.configure(state=customtkinter.DISABLED)
        Message.configure(state=customtkinter.NORMAL)

        # start a thread to keep receiving message from server
        # do not block the main thread :)
        threading._start_new_thread(receive_message_from_server, (client, "m"))
    except Exception as e:
        showerror("Cannot connect to host: " + HOST_ADDR + " on port: " + str(HOST_PORT) + " Server may be Unavailable. Try again later")


def receive_message_from_server(sck, m):
    while True:
        from_server = sck.recv(4096).decode()

        if not from_server: break

        # display message from server on the chat window

        # enable the display area and insert the text and then disable.
        # why? Apparently, tkinter does not allow us insert into a disabled Text widget :(
        texts = Display.get("1.0", customtkinter.END).strip()
        Display.configure(state=customtkinter.NORMAL)
        if len(texts) < 1:
            Display.insert(customtkinter.END, from_server)
        else:
            Display.insert(customtkinter.END, "\n\n"+ from_server)

        Display.configure(state=customtkinter.DISABLED)
        Display.see(customtkinter.END)

        # print("Server says: " +from_server)

    sck.close()
    window.destroy()


def getChatMessage(msg):
    msg = msg.replace('\n', '')
    
    if msg == '':
        return

    texts = Display.get("1.0", customtkinter.END).strip()

    # enable the display area and insert the text and then disable.
    # why? Apparently, tkinter does not allow use insert into a disabled Text widget :(
    Display.configure(state=customtkinter.NORMAL)
    if len(texts) < 1:
        Display.insert(customtkinter.END, "You->" + msg, "tag_your_message") # no line
    else:
        Display.insert(customtkinter.END, "\n\n" + "You->" + msg, "tag_your_message")
    Display.configure(state=customtkinter.DISABLED)
    send_mssage_to_server(msg)

    Display.see(customtkinter.END)
    Message.delete('1.0', customtkinter.END)


def send_mssage_to_server(msg):
    client_msg = str(msg)
    client.send(client_msg.encode())
    if msg == "exit":
        client.close()
        window.destroy()
    print("Sending message")

window.mainloop()