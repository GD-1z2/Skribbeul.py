import tkinter

class logsWindow(tkinter.Tk):
    """
    Logs "traffic" window
    """
    def __init__(self, logs):
        tkinter.Tk.__init__(self)
        self.title("Traffic")

        label1 = tkinter.Label(self, text="Origine")
        label1.grid(row=0, column=0)
        label2 = tkinter.Label(self, text="Contenu")
        label2.grid(row=0, column=1)
        label3 = tkinter.Label(self, text="Heure")
        label3.grid(row=0, column=2)
        for row in range(10):
            try:
                log = logs[-10:][row]
            except :
                continue
            label1 = tkinter.Label(self, text=("Serveur>Client" if log[0]=="s" else "Client>Serveur"))
            label1.grid(row=row+1, column=0, sticky="w")
            label2 = tkinter.Label(self, text=log[1])
            label2.grid(row=row+1, column=1, sticky="w")
            label3 = tkinter.Label(self, text=log[2])
            label3.grid(row=row+1, column=2, sticky="w")
        
        refreshButton = tkinter.Button(self, text="Refraichir", command=self.refresh)
        refreshButton.grid(row=12, column=0, sticky="w")

        self.mainloop()

    def refresh(self):
        pass