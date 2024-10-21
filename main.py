import tkinter
import tkinter.filedialog

class WindowApp :
    filename = ""

    def __init__(self, main):
        self.m = main
        width, height = self.get_curr_screen_geometry()
        self.m.geometry(""+str(int(width / 2))+"x"+str(int(height / 2))+"")
        self.m.title("Jobs list")

        window_menu = tkinter.Menu(self.m)
        self.m.config(menu=window_menu)
        fileSelector = tkinter.Menu(window_menu, tearoff=0)
        window_menu.add_cascade(label="File", menu=fileSelector)
        fileSelector.add_command(label="New", command=self.createFile)
        fileSelector.add_command(label="Open", command=self.select_file)
        fileSelector.add_command(label="Save", command=self.save_file)
        fileSelector.add_separator()
        fileSelector.add_command(label="Exit", command=self.m.destroy)

        window_exit = tkinter.Button(self.m, text="Exit", command=self.m.destroy)
        window_exit.pack(expand=True)

    def createFile(self) :
        name = tkinter.StringVar()

        def return_name():
            self.filename = entry.get()
            print("new value : " + str(self.filename))
            n.destroy

        n = tkinter.Tk()
        n.title("New file")
        tkinter.Label(n, text="File name : ").grid(row=0)
        entry = tkinter.Entry(n, textvariable=name)
        entry.grid(row=0, column=1)
        tkinter.Button(n, text="Submit", command=return_name).grid(row=1)

    def select_file(self) :
        filetype = (
            ('excel files', '*.csv'),
            ('All files', '*.*')
        )

        filename = tkinter.filedialog.askopenfilename(
            title="Open a file",
            initialdir='/', # modify to execution directory
            filetypes=filetype
        )

        self.filename = filename
    
    def save_file(self) :
        # to change with the dump of the data in the csv
        print(str(self.filename))

    def get_curr_screen_geometry(self):
        root = tkinter.Tk()
        root.update_idletasks()
        root.attributes('-fullscreen', True)
        root.state('iconic')
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        return width, height


if __name__ == "__main__":
    # tkinter creation
    main = tkinter.Tk()

    app = WindowApp(main)

    main.mainloop()

