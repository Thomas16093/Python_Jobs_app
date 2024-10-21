import tkinter

if __name__ == "__main__":
    # tkinter creation
    m = tkinter.Tk()
    m.title("Jobs list")
    window_exit = tkinter.Button(m, text="Exit", command=m.destroy)
    window_exit.pack()


    m.mainloop()
