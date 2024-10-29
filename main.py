import csv
import tkinter
from tkinter import messagebox, filedialog
from tkcalendar import DateEntry
from datetime import date
from pathlib import Path

class WindowApp :
    file = None
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
    job_status = [ "", "On going", "Refused", "Approved"]
    listboxs = []
    listboxs_value = []
    dropdown_menu = tkinter.OptionMenu
    enterprise_is_filtered = False
    enterprise_filter = []
    dropdown_variable = None
    event_listbox = None

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

        # create two frame to allow the exit button to be on the right side
        left_button_frame = tkinter.Frame(button_frame)
        left_button_frame.pack(side="left")

        center_button_frame = tkinter.Frame(button_frame)
        center_button_frame.pack(side="left", after=left_button_frame)
        
        right_button_frame = tkinter.Frame(button_frame)
        right_button_frame.pack(side="right")
        
        # create the button on a grid inside the frames -> allow a side by side
        add_button = tkinter.Button(left_button_frame, text="Add a job", command=self.add_job)
        add_button.grid(row=0, column=0)
        view_button = tkinter.Button(left_button_frame, text="View", command=self.view_job)
        view_button.grid(row=0, column=1)
        edit_button = tkinter.Button(left_button_frame, text="Edit", command=self.edit_job)
        edit_button.grid(row=0, column=2)

        # create the filter dropdown list
        filter_label = tkinter.Label(center_button_frame, text="filter with : ")
        filter_label.pack(side="left")
        self.dropdown_menu = tkinter.OptionMenu(center_button_frame, variable=self.dropdown_variable, value=self.enterprise_filter, command=self.refresh_with_filter)
        self.dropdown_menu.pack(side="left", after=filter_label, expand=True)

        # place Exit button in it's own frame to allow a placement on the right side
        window_exit = tkinter.Button(right_button_frame, text="Exit", command=self.m.destroy)
        window_exit.grid(row=0, column=0, sticky="e")

        # create the second frame that host the list of jobs + scrollbar
        list_frame = tkinter.Frame(self.m, borderwidth=0, relief="flat")
        list_frame.pack(expand=True, fill="both")

        # create scrollbar on the right + listbox with a reference to the newly created scrollbar
        scrollbar = tkinter.Scrollbar(list_frame)
        scrollbar.pack(side="right", fill="y")
        listbox_jobs = tkinter.Listbox(list_frame, yscrollcommand=scrollbar.set, exportselection=0)
        listbox_enterprise = tkinter.Listbox(list_frame, yscrollcommand=scrollbar.set, exportselection=0)
        listbox_status = tkinter.Listbox(list_frame, yscrollcommand=scrollbar.set, exportselection=0)

        # add each listbox to the array -> allow a simpler action on each one for the rest of the program
        self.listboxs.append(listbox_jobs)
        self.listboxs_value.append("job_name")

        self.listboxs.append(listbox_enterprise)
        self.listboxs_value.append("enterprise_name")

        self.listboxs.append(listbox_status)
        self.listboxs_value.append("job_status")

        # populate the listbox with the known jobs 
        self.refresh_all_listbox(self.jobs_list)
        
        for index in range(len(self.listboxs)) :
            # allow the value of the list to be communicated to the rest of the class
            self.listboxs[index].bind(sequence='<<ListboxSelect>>', func=self.on_select)
            self.listboxs[index].bind(sequence='<MouseWheel>', func=self.OnMouseWheel)
            # finish creating the listbox
            if index != 0 :
                self.listboxs[index].pack(side="left", after=self.listboxs[index-1], fill="both", expand=True)
            else :
                self.listboxs[index].pack(side="left", fill="both", expand=True)

        # finish creating scrollbar
        scrollbar.config(command=self.yview)

    def yview(self, *args) :
        for index in range(len(self.listboxs)) :
            self.listboxs[index].yview(*args)

    def OnMouseWheel(self, event):
        for index in range(len(self.listboxs)) :
            self.listboxs[index].yview("scroll", event.delta, "units")
        # this prevents default bindings from firing, which
        # would end up scrolling the widget twice
        return "break"

    # get the name of the new file and set it in a class variable then close the window
    def create_file(self) :
        def return_name(): 
            self.filename = entry.get()
            # set the file was not written with the extension -> add it ourselves
            if (self.filename.endswith('.csv') == False) :
                self.filename = self.filename + str('.csv')
            self.refresh_all_listbox([], creation=True)
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

        # check if a file was select before calling the file loader
        if filename != "" :
            self.filename = filename
            self.load_list_from_file(self.filename)
    
    # write into a csv file the modified data to keep them between use
    def save_file(self) :
        # to change with the dump of the data in the csv
        with open(self.filename, "w", newline='') as save_file : 
            csv_out = csv.writer(save_file, delimiter=";", lineterminator="\n")
            for row_out in self.jobs_list :
                job_out = [row_out["job_name"],row_out["enterprise_name"],row_out["job_status"],row_out["job_date"],row_out["description"]]
                print("writing : " + str(job_out))
                for i, entry in zip(range(len(job_out)),job_out) :
                    if entry == None :
                        job_out[i] = ""
                csv_out.writerow(job_out)
        print(str(self.filename))

    # binded with the listbox to get the line in the list and use it on the rest of the app
    def on_select(self, event) :
        selection = event.widget.curselection()
        if selection:
            if selection[0] != self.job_index :
                index = selection[0]
                data = self.jobs_list[index]["job_name"]
                #data = event.widget.get(index)
                self.event_listbox = event.widget
                self.selected_job = data
                self.job_index = index
                # allow multi selection
                # will select the same job in each row help visualize each value of a job
                for i in range(len(self.listboxs)) :
                    if self.listboxs[i] != self.event_listbox :
                        self.listboxs[i].selection_clear(0, len(self.jobs_list))
                        self.listboxs[i].selection_set(index, index)
                    else : pass
            else :
                pass
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
        a = tkinter.Tk()
        a.title("Add a job")
        current_job_status = tkinter.StringVar(a)
        # add a boolean variable for testing if we want to add a job today
        check_button_value = tkinter.BooleanVar(a)

        def submit_job():
            job = {"job_name" : "", "enterprise_name" : "", "job_status" : "", "job_date" : "", "description" : "" }
            job["job_name"] = job_name_entry.get()
            job["enterprise_name"] = enterprise_name_entry.get()
            job["job_status"] = current_job_status.get()
            if job_date_entry.get_date() != date(2000, 1, 1) :
                job["job_date"] = job_date_entry.get_date()
            else : job["job_date"] = ""
            job["description"] = job_description.get()
            self.jobs_list.insert(len(self.jobs_list), job)
            self.refresh_all_listbox(self.jobs_list)
            a.destroy()

        def update_date():
            # if the checkbutton is checked -> set the date to today and gey out the DateEntry to prevent changing the date
            if check_button_value.get() :
                today = date.today()
                job_date_entry.set_date(today)
                job_date_entry.config(state='disabled')
            # else re-activate the DateEntry to modify the date as we want
            else : 
                job_date_entry.config(state='enabled')
        
        tkinter.Label(a, text="Job Name").grid(row=0, column=0)
        tkinter.Label(a, text="Enterprise").grid(row=0, column=1)
        tkinter.Label(a, text="Job Status").grid(row=0, column=2)
        tkinter.Label(a, text="Application date").grid(row=0, column=3)
        tkinter.Label(a, text="Job description").grid(row=0, column=4)
        job_name_entry = tkinter.Entry(a)
        job_name_entry.grid(row=1, column=0, padx=5)
        enterprise_name_entry = tkinter.Entry(a)
        enterprise_name_entry.grid(row=1, column=1)
        tkinter.OptionMenu(a, current_job_status, *self.job_status).grid(row=1, column=2, padx=5)
        # create a frame to center the date Label betwwen the checkbutton and the date entry
        date_frame = tkinter.Frame(a)
        # add a check button to specify if the application has been done today
        tkinter.Checkbutton(date_frame, text="Today", variable=check_button_value, command=update_date).grid(row=0, column=0)
        job_date_entry = DateEntry(date_frame)
        job_date_entry.grid(row=0, column=1, padx=5)
        date_frame.grid(row=1, column=3)
        job_description = tkinter.Entry(a)
        job_description.grid(row=1, column=4)
        tkinter.Button(a, text="Add", command=submit_job).grid(row=1, column=5, padx=5)

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
        if self.job_index != None :
            edit_window = tkinter.Tk()
            edit_window.title("Edit job : " + str(self.selected_job))
            current_job_status = tkinter.StringVar(edit_window)
            # add a boolean variable for testing if we want to add a job today
            check_button_value = tkinter.BooleanVar(edit_window)

            def submit_job():
                job = {"job_name" : "", "enterprise_name" : "", "job_status" : "", "job_date" : "", "description" : "" }
                job["job_name"] = job_name_entry.get()
                job["enterprise_name"] = enterprise_name_entry.get()
                job["job_status"] = current_job_status.get()
                # if the date is today ( default with DateEntry ) but not wanted -> add nothing
                if job_date_entry.get_date() == date.today() and check_button_value == False :
                    job["job_date"] = ""
                else : job["job_date"] = job_date_entry.get_date() # else add the date to the job
                job["description"] = job_description.get()
                self.jobs_list.pop(self.job_index)
                self.jobs_list.insert(self.job_index, job)
                self.refresh_all_listbox(self.jobs_list)
                edit_window.destroy()

            def update_date():
                # if the checkbutton is checked -> set the date to today and gey out the DateEntry to prevent changing the date
                if check_button_value.get() :
                    today = date.today()
                    job_date_entry.set_date(today)
                    job_date_entry.config(state='disabled')
                # else re-activate the DateEntry to modify the date as we want
                else : 
                    job_date_entry.config(state='enabled')

            tkinter.Label(edit_window, text="Job Name").grid(row=0, column=0)
            tkinter.Label(edit_window, text="Enterprise").grid(row=0, column=1)
            tkinter.Label(edit_window, text="Job Status").grid(row=0, column=2)
            tkinter.Label(edit_window, text="Application date").grid(row=0, column=3)
            tkinter.Label(edit_window, text="Job description").grid(row=0, column=4)
            # create a local variable for accessing the current_job easily
            current_job = self.jobs_list[self.job_index]
            job_name_entry = tkinter.Entry(edit_window)
            job_name_entry.insert(0, str(current_job["job_name"]))
            job_name_entry.grid(row=1, column=0, padx=5)
            enterprise_name_entry = tkinter.Entry(edit_window)
            enterprise_name_entry.insert(0, str(current_job["enterprise_name"]))
            enterprise_name_entry.grid(row=1, column=1)
            tkinter.OptionMenu(edit_window, current_job_status, *self.job_status).grid(row=1, column=2, padx=5)
            if current_job["job_status"] != "" : current_job_status.set(current_job["job_status"])
            
            # creating a frame to grid check button and DateEntry to the same place
            date_frame = tkinter.Frame(edit_window)

            # add a check button to specify if the application has been done today
            tkinter.Checkbutton(date_frame, text="Today", variable=check_button_value, command=update_date).grid(row=0, column=0)
            
            job_date_entry = DateEntry(date_frame)
            if current_job["job_date"] != "" : job_date_entry.set_date(current_job["job_date"])
            job_date_entry.grid(row=0, column=1, padx=5)

            # grid the frame after the job status -> will center the Label above
            date_frame.grid(row=1, column=3)

            job_description = tkinter.Entry(edit_window)
            job_description.insert(0, str(current_job["description"]))
            job_description.grid(row=1, column=4)
            tkinter.Button(edit_window, text="Edit", command=submit_job).grid(row=1, column=5, padx=5)
        else :
            messagebox.showwarning("Edit job","Select a job first !")


    def refresh_list(self, list_box : tkinter.Listbox, list : dict, list_value : str, creation : bool) :
        if creation :
            list_box.delete(0, len(self.jobs_list))
            self.jobs_list = list
            self.enterprise_filter = []
            self.enterprise_is_filtered = False
        else :
            list_box.delete(0, tkinter.END)
            for line in range(len(list)) :
                job = list[line][list_value]
                list_box.insert(line, str(job))
    
    def refresh_all_listbox(self, list_jobs : dict, value_creation = False) :
        if len(self.listboxs) != len(self.listboxs_value) : 
            print("error : inconsistency between number of listbox and the value displayed in it !")
        for i in range(len(self.listboxs)) :
            self.refresh_list(self.listboxs[i], list_jobs, self.listboxs_value[i], value_creation)
        if self.enterprise_is_filtered == False:
            for index in range(len(self.jobs_list)) :
                current_enterprise = self.jobs_list[index]["enterprise_name"]
                if current_enterprise not in self.enterprise_filter : self.enterprise_filter.append(current_enterprise)
            self.refresh_dropdown_menu()

    def refresh_with_filter(self) :
        enterprise_selected = self.dropdown_variable
        print("selected enterprise : " + str(enterprise_selected))
        if enterprise_selected == "All" :
            self.enterprise_is_filtered = False
            self.refresh_all_listbox(self.jobs_list)
        else :
            self.enterprise_is_filtered = True
            filtered_jobs = []
            for job in self.jobs_list :
                if job["enterprise_name"] == enterprise_selected :
                    filtered_jobs.append(job)
                else : pass
            self.refresh_all_listbox(filtered_jobs)

    def refresh_dropdown_menu(self) :
        menu = tkinter.OptionMenu
        menu = self.dropdown_menu["menu"]
        menu.delete(0, "end")

        # bypass the automatic affectation of OptionMenu that doesn't work for my need 
        menu.add_command(label="All", command = lambda value="All" : (setattr(self, 'dropdown_variable', value), self.refresh_with_filter()))
        for string in self.enterprise_filter:
            if string != "" :
                menu.add_command(label=string,
                            command = lambda value=string: (setattr(self, 'dropdown_variable', value), self.refresh_with_filter())) 
            else : pass

    # load the file selected from the file picker
    def load_list_from_file(self, path_to_file):
        if Path(path_to_file).is_file() :
            # open the file and load jobs into a list to send it in refresh_list
            jobs_from_file = []
            with open(path_to_file) as file:
                reader = csv.reader(file, delimiter=";")
                for values in reader:
                    # test if the job has all the values in the file -> if not add a blank one
                    if len(values) < 5 : 
                        for i in range(len(values), 5) :
                            values.append("")
                    # reference the value of the job in the correct properties
                    job = {"job_name" : values[0], "enterprise_name" : values[1], "job_status" : values[2], "job_date" : values[3], "description" : values[4]}

                    # convert string date to proper date
                    if job["job_date"] != "" :
                        job_date = job["job_date"].split("-")
                        job["job_date"] = date(int(job_date[0]), int(job_date[1]), int(job_date[2]))

                    jobs_from_file.append(job)
                    # refresh the listbox to dipslay the jobs read from the file
                    self.refresh_all_listbox(self.jobs_list, True)
                    self.refresh_all_listbox(jobs_from_file)
                for jobs in jobs_from_file :
                    print(str(jobs))
        else :
            # create the file and refresh the listbox
            # needed if the file picker send a non-existant file
            self.file = open(self.filename, "w")
            self.refresh_all_listbox([], True)


if __name__ == "__main__":
    # tkinter creation
    main = tkinter.Tk()

    # call the class to run the windows app
    app = WindowApp(main)

    # display the window app
    main.mainloop()