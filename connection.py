import socket, threading, sys, time

class ThreadReception(threading.Thread):
    """objet thread gérant la réception des messages"""
    def __init__(self, conn, ref_socket, textarea, app):

        threading.Thread.__init__(self)
        ref_socket[0] = conn
        self.connexion = conn  # réf. du socket de connexion
        self.textarea = textarea
        self.app = app
              
    def run(self):
        while True:
            try:
                # en attente de réception
                receivedMsg = self.connexion.recv(4096)
                receivedMsg = receivedMsg.decode(encoding="UTF-8")
                
                self.app.logs.append(["s", receivedMsg, time.ctime()])

                self.textarea.config(state="normal")
                self.textarea.insert("end", receivedMsg) # add message
                self.textarea.yview_scroll(1, "pages") # scroll
                self.textarea.config(state="disabled")
                
                if "/HINT" in  receivedMsg:
                    self.app.setHint(receivedMsg.split(":")[1])
                elif "/DRAW" in receivedMsg:
                    self.app.canDraw = True
                elif "/NODRAW" in receivedMsg:
                    self.app.canDraw = False
                elif "/END" in receivedMsg:
                    self.app.logout()
                    break
                    
            except socket.error as err:
                print("Socket error : " + err.strerror)
                self.textarea.config(state="normal")
                self.textarea.insert("end", "Erreur réseau : " + err.strerror) # add message
                self.textarea.yview_scroll(1, "pages") # scroll
                self.textarea.config(state="disabled")
                input()

# # Frame 2 : zone de réception (zone de texte + scrollbar)
# Frame2 = Frame(Mafenetre,borderwidth=2,relief=GROOVE)

# # height = 10 <=> 10 lignes
# ZoneReception = Text(Frame2,width =80, height =30,state=DISABLED)
# ZoneReception.grid(row=0,column=0,padx=5,pady=5)

# scroll = Scrollbar(Frame2, command = ZoneReception.yview)

# ZoneReception.configure(yscrollcommand = scroll.set)

# scroll.grid(row=0,column=1,padx=5,pady=5,sticky=E+S+N)

# Frame2.grid(row=1,column=0,padx=5,pady=5)

# # Frame 3 : envoi de message au serveur
# Frame3 = Frame(Mafenetre,borderwidth=2,relief=GROOVE)

# MESSAGE = StringVar()
# Entry(Frame3, textvariable= MESSAGE).grid(row=0,column=0,padx=5,pady=5)