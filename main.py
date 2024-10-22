import tkinter
import datetime
from tkinter import messagebox, filedialog
from tkcalendar import DateEntry

class WindowApp :
    filename = ""
    selected_job = ""
    job_index = None
    jobs_list = [{"job_name" : "Jobs 1", "enterprise_name" : "", "job_status" : "", "job_date" : "", "description" : "" },
                {"job_name" : "Jobs 2", "enterprise_name" : "", "job_status" : "", "job_date" : "", "description" : "" },
                {"job_name" : "Jobs 3", "enterprise_name" : "", "job_status" : "", "job_date" : "", "description" : "" },
                {"job_name" : "Jobs 4", "enterprise_name" : "", "job_status" : "", "job_date" : "", "description" : "" },
                {"job_name" : "Jobs 5", "enterprise_name" : "", "job_status" : "", "job_date" : "", "description" : "" },
                {"job_name" : "Jobs 6", "enterprise_name" : "", "job_status" : "", "job_date" : "", "description" : "" },
                {"job_name" : "Jobs 7", "enterprise_name" : "", "job_status" : "", "job_date" : "", "description" : "" },
                {"job_name" : "Jobs 8", "enterprise_name" : "", "job_status" : "", "job_date" : "", "description" : "" },
                {"job_name" : "Jobs 9", "enterprise_name" : "", "job_status" : "", "job_date" : "", "description" : "" },
                {"job_name" : "Jobs 10", "enterprise_name" : "", "job_status" : "", "job_date" : "", "description" : "" },
                {"job_name" : "Jobs 11", "enterprise_name" : "", "job_status" : "", "job_date" : "", "description" : "" }]
    listbox_jobs = None

    def __init__(self, main):
        self.m = main
        width, height = self.get_curr_screen_geometry()
        self.m.focus_force() # make window on top -> fix the state left from the screen_geometry func
        self.m.geometry(""+str(int(width / 2))+"x"+str(int(height / 2))+"")
        self.m.title("Jobs list")

        window_menu = tkinter.Menu(self.m)
        self.m.config(menu=window_menu)
        fileSelector = tkinter.Menu(window_menu, tearoff=0)
        window_menu.add_cascade(label="File", menu=fileSelector)
        fileSelector.add_command(label="New", command=self.create_file)
        fileSelector.add_command(label="Open", command=self.select_file)
        fileSelector.add_command(label="Save", command=self.save_file)
        fileSelector.add_separator()
        fileSelector.add_command(label="Exit", command=self.m.destroy)

        # create a frame to host the button of my main window
        button_frame = tkinter.Frame(self.m, borderwidth=0, relief="flat")
        button_frame.pack(fill="x")
        
        # create the button on a grid inside the frame -> allow a side by side
        add_button = tkinter.Button(button_frame, text="Add a job", command=self.add_job)
        add_button.grid(row=0, column=0)
        view_button = tkinter.Button(button_frame, text="View", command=self.view_job)
        view_button.grid(row=0, column=1)
        edit_button = tkinter.Button(button_frame, text="Edit", command=self.edit_job)
        edit_button.grid(row=0, column=2)
        window_exit = tkinter.Button(button_frame, text="Exit", command=self.m.destroy)
        window_exit.grid(row=0, column=3)

        # create the second frame that host the list of jobs + scrollbar
        list_frame = tkinter.Frame(self.m, borderwidth=0, relief="flat")
        list_frame.pack(expand=True, fill="both")

        # create scrollbar on the right + listbox with a reference to the newly created scrollbar
        scrollbar = tkinter.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        self.listbox_jobs = tkinter.Listbox(list_frame, yscrollcommand=scrollbar.set)

        # populate the listbox with the known jobs 
        for line in range(len(self.jobs_list)) :
            job = self.jobs_list[line]["job_name"]
            self.listbox_jobs.insert(line, str(job))

        # allow the value of the list to be communicated to the rest of the class
        self.listbox_jobs.bind(sequence='<<ListboxSelect>>', func=self.on_select)
        # finish creating the listbox and scrollbar together
        self.listbox_jobs.pack(side="left", fill="both", expand=True)
        scrollbar.config(command=self.listbox_jobs.yview)

    # get the name of the new file and set it in a class variable then close the window
    def create_file(self) :
        def return_name(): 
            self.filename = entry.get()
            # set the file was not written with the extension -> add it ourselves
            if (self.filename.endswith('.csv') == False) :
                self.filename = self.filename + str('.csv')
            self.refresh_list([], creation=True)
            n.destroy()
        n = tkinter.Tk()
        n.title("New file")
        tkinter.Label(n, text="File name : ").grid(row=0)
        entry = tkinter.Entry(n)
        entry.grid(row=0, column=1)
        submit_button = tkinter.Button(n, text="Submit", command=return_name)
        submit_button.grid(row=1)

    # get the path to the file, set it in a class variable to be used in the main app
    def select_file(self) :
        filetype = (
            ('excel files', '*.csv'),
            ('All files', '*.*')
        )

        filename = filedialog.askopenfilename(
            title="Open a file",
            initialdir='/', # modify to execution directory
            filetypes=filetype
        )

        self.filename = filename
    
    # write into a csv file the modified data to keep them between use
    def save_file(self) :
        # to change with the dump of the data in the csv
        print(str(self.filename))

    # binded with the listbox to get the line in the list and use it on the rest of the app
    def on_select(self, event) :
        selection = event.widget.curselection()
        if selection:
            index = selection[0]
            data = event.widget.get(index)
            self.selected_job = data
            self.job_index = index
        else:
            pass
    
    # pulled from a forum -> should be able to determine the screen value even on a multi monitor setup
    def get_curr_screen_geometry(self):
        root = tkinter.Tk()
        root.update_idletasks()
        root.attributes('-fullscreen', True)
        root.state('iconic')
        width = root.winfo_screenwidth()
        height = root.winfo_screenheight()
        root.destroy()
        return width, height
    
    # add a job on the list with all the different data
    def add_job(self) :
        pass

    # view the selected job in the listbox with detailled information
    def view_job(self) :
        if self.job_index != None :
            view_window = tkinter.Tk()
            view_window.title("Job : " + str(self.selected_job))
            tkinter.Label(view_window, text=self.selected_job).grid(row=0, column=0)
            tkinter.Label(view_window, text=self.jobs_list[self.job_index]["enterprise_name"]).grid(row=0, column=1)
            tkinter.Label(view_window, text=self.jobs_list[self.job_index]["job_status"]).grid(row=0, column=2)
            tkinter.Label(view_window, text=str(self.jobs_list[self.job_index]["job_date"])).grid(row=0, column=3)
            tkinter.Label(view_window, text=self.jobs_list[self.job_index]["description"]).grid(row=0, column=4)
            tkinter.Button(view_window, text="Exit", command=view_window.destroy).grid(row=1)
        else :
            messagebox.showwarning("View job","Select a job first !")

    # allow the modification of the selected job ( ex : job application refused )
    def edit_job(self) :
        pass

    def refresh_list(self, list, creation) :
        if creation :
            self.listbox_jobs.delete(0, len(self.jobs_list))
            self.jobs_list = list
        else :
            if len(list) > len(self.jobs_list) :
                for line in range(len(list)) :
                    job = list[line]["job_name"]
                    if (self.jobs_list.__contains__(job) == False) :
                        self.jobs_list.append(job)
                        self.listbox_jobs.insert(line, str(job))
            else : 
                self.listbox_jobs.delete(0, len(self.jobs_list))
                self.jobs_list = list
                for line in range(len(list)) :
                    job = list[line]["job_name"]
                    self.listbox_jobs.insert(line, str(job))


if __name__ == "__main__":
    # tkinter creation
    main = tkinter.Tk()

    # call the class to run the windows app
    app = WindowApp(main)
    # display the window app
    main.mainloop()

