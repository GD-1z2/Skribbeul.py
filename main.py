import tkinter, tkinter.messagebox, tkinter.simpledialog
import connection, socket, threading
import json
import logs
import time

# connected = False ; address = "" ; port = 50026
ref_socket = {}

class App(tkinter.Frame):
    """
    da game
    """

    def __init__(self, window):
        tkinter.Frame.__init__(self, window)

        self.color = "black"
        self.size = 5
        self.preX = -666 ; self.preY = -666
        self.lastLine = []
        self.adress = "localhost" ; self.port = 50026 ; self.connected = False
        self.canvasContent = []
        self.canDraw = True
        self.logs = []
        self.dragTime = 0

        self.menuBar = tkinter.Menu(window)

        self.serverMenu = tkinter.Menu(self.menuBar, tearoff=0)
        self.serverMenu.add_command(label="Connexion...", command=self.connection)
        self.trafficButton = self.serverMenu.add_command(label="Traffic", state="disabled", command=self.traffic)
        self.logoutButton = self.serverMenu.add_command(label="Deconnexion", state="disabled", command=self.logout)
        self.menuBar.add_cascade(menu=self.serverMenu, label="Serveur")

        self.helpMenu = tkinter.Menu(self.menuBar, tearoff=0)
        self.helpMenu.add_command(label="    Tutoriels", state="disabled")
        self.helpMenu.add_command(label="Comment jouer", command=self.tutoPlay)
        self.helpMenu.add_command(label="Comment se connecter à un serveur", command=self.tutoServer)
        self.helpMenu.add_separator()
        self.helpMenu.add_command(label="A propos", command=self.about)
        self.menuBar.add_cascade(menu=self.helpMenu, label="Aide")

        window.config(menu=self.menuBar)

        # self.addLabel(self, 2, 2, 290, 450,
        # text="Bienvenue !\nConnectez vous à un serveur pour commencer à jouer :\nServeur -> Connexion\nPour plus d'informations : Aide -> Comment se connecter à un serveur",
        # bg="white", justify="left", wraplength=285)

        self.chatLabel = tkinter.Text(self, width=36, height=28, bg="white", state="disabled")
        self.chatLabel.grid(row=2, column=2, rowspan=2)

        self.wordLabelVar = tkinter.StringVar()
        self.wordLabel = tkinter.Label(self, textvariable=self.wordLabelVar)
        self.wordLabel.grid(row=1, column=1)

        self.infoLabelVar = tkinter.StringVar()
        self.infoLabelVar.set("Déconnecté")
        self.infoLabel = tkinter.Label(self, textvariable=self.infoLabelVar)
        self.infoLabel.grid(row=1, column=2)

        self.canvas = tkinter.Canvas(self, width=900, height=450, bg="white")
        self.canvas.grid(row=2, column=1, rowspan=2)
        self.canvas.bind("<Button-1>", self.onClick)
        self.canvas.bind("<B1-Motion>", self.onDrag)
        self.canvas.bind("<ButtonRelease-1>", self.onRelease)

        # self.messageFrame = tkinter.Frame(self)
        self.messageEntryVar = tkinter.StringVar()
        self.messageEntry = tkinter.Entry(self, width=44, textvariable=self.messageEntryVar)
        self.messageEntry.grid(row=4, column=2, sticky="w")
        self.sendButton = tkinter.Button(self, text="↑", font=("Helvetica", 10), command=self.sendMessage, state="disabled")
        self.sendButton.grid(row=4, column=2, sticky="e")
        # self.messageEntry.grid(row=4, column=2, fill="both")
        self.messageEntry.bind("<Return>", self.sendMessageEv)

        self.blackButton = tkinter.Button(self, text="✓", bg="black", font=("Helvetica", 12), fg="white", command=self.cBlack)
        self.blackButton.grid(row=4, column=1, sticky="w")
        self.greyButton = tkinter.Button(self, text="▪", bg="grey", font=("Helvetica", 12), command=self.cGrey)#●
        self.greyButton.grid(row=4, column=1, sticky="w", padx=40)
        self.whiteButton = tkinter.Button(self, text="▪", bg="white", font=("Helvetica", 12), command=self.cWhite)#●
        self.whiteButton.grid(row=4, column=1, sticky="w", padx=80)
        self.redButton = tkinter.Button(self, text="▪", bg="red", font=("Helvetica", 12), command=self.cRed)#●
        self.redButton.grid(row=4, column=1, sticky="w", padx=120)
        self.orangeButton = tkinter.Button(self, text="▪", bg="orange", font=("Helvetica", 12), command=self.cOrange)#●
        self.orangeButton.grid(row=4, column=1, sticky="w", padx=160)
        self.yellowButton = tkinter.Button(self, text="▪", bg="yellow", font=("Helvetica", 12), command=self.cYellow)#●
        self.yellowButton.grid(row=4, column=1, sticky="w", padx=200)
        self.greenButton = tkinter.Button(self, text="▪", bg="green", font=("Helvetica", 12), command=self.cGreen)#●
        self.greenButton.grid(row=4, column=1, sticky="w", padx=240)
        self.blueButton = tkinter.Button(self, text="▪", bg="blue", font=("Helvetica", 12), command=self.cBlue)#●
        self.blueButton.grid(row=4, column=1, sticky="w", padx=280)
        self.violetButton = tkinter.Button(self, text="▪", bg="violet", font=("Helvetica", 12), command=self.cViolet)#
        self.violetButton.grid(row=4, column=1, sticky="w", padx=320)

        self.size1Button = tkinter.Button(self, text="◦", font=("Helvetica", 12), command=self.size1, width=2)
        self.size1Button.grid(row=4, column=1, sticky="e", padx=0)
        self.size2Button = tkinter.Button(self, text="○", font=("Helvetica", 12), command=self.size2, width=2)
        self.size2Button.grid(row=4, column=1, sticky="e", padx=40)
        self.size3Button = tkinter.Button(self, text="〇", font=("Helvetica", 12), command=self.size3, width=2)
        self.size3Button.grid(row=4, column=1, sticky="e", padx=80)
        self.size4Button = tkinter.Button(self, text="◯", font=("Helvetica", 12), command=self.size4, width=2)
        self.size4Button.grid(row=4, column=1, sticky="e", padx=120)

        self.clearButton = tkinter.Button(self, text="✕", font=("Helvetica", 12), command=self.clear)#✕〤✕
        self.clearButton.grid(row=4, column=1, sticky="e", padx=200)
        self.undoButton = tkinter.Button(self, text=" ⤶ ", font=("Helvetica", 12), command=self.undo)#⤶⬅
        self.undoButton.grid(row=4, column=1, sticky="e", padx=240)

    def connection(self):
        global ref_socket

        self.address = tkinter.simpledialog.askstring(title="Connexion", prompt="Entrez une adresse :", initialvalue=self.adress)
        if self.address == "" : tkinter.messagebox.showerror(title="Erreur", message="Veuillez entrer une adresse") ; return
        if self.address == None : return
        self.port = tkinter.simpledialog.askinteger(title="Connexion", prompt="Entrez un port :", initialvalue=self.port)
        if self.port == "" : tkinter.messagebox.showerror(title="Erreur", message="Veuillez entrer un port") ; return
        if self.port == None : return

        if self.connected == False:
            try :
                self.isocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.isocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
                self.isocket.connect((self.address, self.port))
                # Dialogue avec le serveur : on lance un thread pour gérer la réception des messages
                self.threadRec = connection.ThreadReception(self.isocket, ref_socket, self.chatLabel, self)
                self.threadRec.start()
                self.messageEntry.focus_set()
                
            except socket.error:
                tkinter.messagebox.showerror("Erreur", "La connexion au serveur a échoué.")
                return

        self.connected = True
        self.serverMenu.entryconfig("Connexion...", state="disabled")
        self.serverMenu.entryconfig("Traffic", state="active")
        self.serverMenu.entryconfig("Deconnexion", state="active")
        self.infoLabelVar.set("Connecté")
        self.sendButton.config(state="normal")

    def logout(self):
        self.serverMenu.entryconfig("Connexion...", state="active")
        self.serverMenu.entryconfig("Traffic", state="disabled")
        self.serverMenu.entryconfig("Deconnexion", state="disabled")
        self.infoLabelVar.set("Déconnecté")
        self.wordLabelVar.set("")
        self.sendButton.config(state="disabled")
        self.connected = False
        self.chatLabel.delete("1.0", "end")
        ref_socket.clear()
        tkinter.messagebox.showinfo(title="Deconnexion", message="Vous avez été déconnecté")

    def sendMessage(self):
        global ref_socket

        if self.connected == True:
            try :
                message = self.messageEntryVar.get()
                if message == "": return
                print(message)
                self.messageEntryVar.set("")
                
                self.chatLabel.config(state="normal")
                self.chatLabel.insert("end", message+"\n")
                self.chatLabel.config(state="disabled")
            
                ref_socket[0].send(bytes(message, "UTF8"))
                self.logs.append(["c", message, time.ctime()])
                
            except socket.error:
                pass
    
    def sendMessageEv(self, e): self.sendMessage()

    def sendCanvas(self):
        ref_socket[0].send(bytes("/CANVAS:"+json.dumps(self.canvasContent), "UTF8"))

    def onClick(self, event):
        if not self.canDraw : return
        self.preX = event.x;self.preY = event.y
        self.lastLine.append(0)
        self.canvasContent.append([self.color, self.size, []])

    def onDrag(self, event):
        if not self.canDraw : return
        self.dragTime+=1
        if self.dragTime%25 != 0 : return
        # self.canvas.create_oval(event.x-self.size/2, event.y-self.size/2, event.x+self.size/2, event.y+self.size/2, fill=self.color, outline=self.color)        
        self.canvas.create_line(self.preX, self.preY, event.x, event.y, fill=self.color, width=self.size)
        self.preX = event.x
        self.preY = event.y
        self.lastLine[len(self.lastLine)-1]+=1
        self.canvasContent[len(self.canvasContent)-1][2].append([event.x, event.y])
        print(json.dumps(self.canvasContent))
        print()
    
    def onRelease(self, event):
        if self.canDraw : self.sendCanvas()

    def undo(self):
        if len(self.lastLine)<1 : self.clear() ; tkinter.messagebox.showerror(title="Erreur", message="Aucun élément trouvé") ; return
        for loop in range(self.lastLine[len(self.lastLine)-1]):
            if len(self.canvas.find_all()) > 1:
                item = self.canvas.find_all()[-1]
                self.canvas.delete(item)
        print(len(self.lastLine))
        self.lastLine.pop()
        self.canvasContent.pop()

    def clear(self):
        self.canvas.delete("all")
        self.lastLine.clear()
        self.canvasContent.clear()

    def getColorButton(self, colorG : str = "black"):
        if colorG=="black":return self.blackButton
        elif colorG=="grey":return self.greyButton
        elif colorG=="white":return self.whiteButton
        elif colorG=="red":return self.redButton
        elif colorG=="orange":return self.orangeButton
        elif colorG=="yellow":return self.yellowButton
        elif colorG=="green":return self.greenButton
        elif colorG=="blue":return self.blueButton
        elif colorG=="violet":return self.violetButton
        return self.blackButton

    def setColor(self, colorI = "black"):
        if not self.canDraw : return
        self.getColorButton(self.color).config(text="▪")
        self.color=colorI
        self.getColorButton(self.color).config(text="✓")

    def cBlack(self):self.setColor("black")
    def cGrey(self): self.setColor("grey")
    def cWhite(self):self.setColor("white")
    def cRed(self):self.setColor("red")
    def cOrange(self):self.setColor("orange")
    def cYellow(self):self.setColor("yellow")
    def cGreen(self):self.setColor("green")
    def cBlue(self):self.setColor("blue")
    def cViolet(self):self.setColor("violet")

    def setSize(self, sizeI):
        if not self.canDraw : return
        self.size = sizeI
    def size1(self):self.setSize(3)
    def size2(self):self.setSize(5)
    def size3(self):self.setSize(8)
    def size4(self):self.setSize(12)

    def setHint(self, hint : str):
        hint2 = ""
        for char in hint :
            hint2 += char+" "
        self.wordLabelVar.set(hint2[:-1])
    
    def render(self, content):
        paths = json.loads(content)
        self.canvas.delete("all")
        for path in paths:
            i=0
            for line in path[2][:-1]:
                self.canvas.create_line(line[0], line[1], path[2][i+1][0], path[2][i+1][1], fill=path[0], width=path[1])
                i+=1

    def traffic(self):
        logs.logsWindow(self.logs)

    def about(self):
        tkinter.messagebox.showinfo(title="A propos", message="Skribbeul.py\nJeu multijoueur basé sur skribl.io\nRéalisé en python par 1z2")

    def tutoPlay(self):
        tkinter.messagebox.showinfo(title="Tutoriel : comment jouer",
        message="")

    def tutoServer(self):
        tkinter.messagebox.showinfo(title="Tutoriel : comment se connecter à un serveur",
        message="")

    def addLabel(self, master, x, y, w, h, *args, **kwargs):
        f = tkinter.Frame(master, height=h, width=w)
        f.pack_propagate(0) # don't shrink
        f.grid(row=x, column=y)
        label = tkinter.Label(f, *args, **kwargs)
        label.pack(fill=tkinter.BOTH, expand=1)
        return label



# chatLabel = tkinter.Label(window, width=30, height=30, bg="white", text="Bienvenue !", justify=tkinter.LEFT)
# chatLabel.grid(row=2, column=2, rowspan=2)

if __name__ == "__main__":
    window = tkinter.Tk()
    window.wm_title("Skribbeul.py")
    window.geometry("1200x508+84+206")
    window.wm_resizable(False, False)

    app = App(window)
    app.pack(fill="both", expand=True)

    window.mainloop()