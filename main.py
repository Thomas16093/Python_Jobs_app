import csv
import tkinter
from tkinter import messagebox, filedialog
from tkcalendar import DateEntry
from datetime import date
from pathlib import Path
import webbrowser as web
import validators
import i18n
import locale

return_value = -1

class WindowApp :
    file = None
    filename = ""
    selected_job = ""
    job_index = None
    job_template = {"job_name" : "", "enterprise_name" : "", "job_status" : "", "job_date" : "", "url" : "", "description" : "" }
    jobs_list = [ job_template.copy() ]
    job_status_template = [ "", "On going", "Refused", "Approved"]
    job_status = []
    jobs_timeout = []
    timeout_details_label = None
    listboxs = []
    listboxs_value = []
    dropdown_menu = tkinter.OptionMenu
    enterprise_is_filtered = False
    enterprise_filter = []
    current_job_list = jobs_list
    dropdown_variable = None
    event_listbox = None
    job_count = None
    job_details = []
    current_language = None
    available_languages = []

    def __init__(self, main, all_languages):
        # refresh a bunch of class variable
        self.listboxs = []
        self.listboxs_value = []
        self.enterprise_filter = []
        self.job_details = []
        self.current_language = i18n.get('locale')
        self.job_status = [ "", i18n.t('jobs_app.ongoing'), i18n.t('jobs_app.refused'), i18n.t('jobs_app.approved')]

        self.available_languages = all_languages
        self.m = main
        width, height = self.get_curr_screen_geometry()
        self.m.focus_force() # make window on top -> fix the state left from the screen_geometry func
        self.m.geometry(""+str(int(width / 2))+"x"+str(int(height / 2))+"")
        self.m.title(i18n.t('jobs_app.title'))

        # create the menu for the app
        window_menu = tkinter.Menu(self.m)
        self.m.config(menu=window_menu)
        fileSelector = tkinter.Menu(window_menu, tearoff=0)
        window_menu.add_cascade(label=i18n.t('jobs_app.file'), menu=fileSelector)
        fileSelector.add_command(label=i18n.t('jobs_app.new'), command=self.create_file)
        fileSelector.add_command(label=i18n.t('jobs_app.open'), command=self.select_file)
        fileSelector.add_command(label=i18n.t('jobs_app.save'), command=self.save_file)
        fileSelector.add_separator()
        fileSelector.add_command(label=i18n.t('jobs_app.exit'), command=self.exit_completly)
        
        # add a second menu for selecting the languages
        sub_menu = tkinter.Menu(window_menu, tearoff=0)
        for lang in self.available_languages :
            sub_menu.add_command(label=str(lang), command=lambda language=lang: self.refresh_languages(language))
        window_menu.add_cascade(label=i18n.t('jobs_app.languages'), menu=sub_menu)

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
        add_button = tkinter.Button(left_button_frame, text=i18n.t('jobs_app.add_job'), command=self.add_job)
        add_button.grid(row=0, column=0)
        view_button = tkinter.Button(left_button_frame, text=i18n.t('jobs_app.view'), command=self.view_job)
        view_button.grid(row=0, column=1)
        edit_button = tkinter.Button(left_button_frame, text=i18n.t('jobs_app.edit'), command=self.edit_job)
        edit_button.grid(row=0, column=2)

        # create the filter dropdown list
        filter_label = tkinter.Label(center_button_frame, text=i18n.t('jobs_app.filter') + " : ")
        filter_label.pack(side="left")
        self.dropdown_variable = tkinter.StringVar(center_button_frame)
        self.dropdown_variable.set("All")
        self.dropdown_menu = tkinter.OptionMenu(center_button_frame, variable=self.dropdown_variable, value=self.dropdown_variable.get())
        self.dropdown_menu.pack(side="left", after=filter_label, expand=True)

        # place Exit button in it's own frame to allow a placement on the right side
        window_exit = tkinter.Button(right_button_frame, text=i18n.t('jobs_app.exit'), command=self.exit_completly)
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
        
        # All Frame creation for the bottom of the main window

        # create a frame to place a job count on the bottom right
        job_count_frame = tkinter.Frame(self.m)

        self.job_count = tkinter.StringVar(job_count_frame, value=len(self.jobs_list))
        # create them in inverse order because the pack manager place the first RIGHT to the rightmost of the window
        # the others follow and stick to the precedent
        tkinter.Entry(job_count_frame, textvariable=self.job_count, width=5, state="readonly").pack(side=tkinter.RIGHT, padx=5)
        tkinter.Label(job_count_frame, text=i18n.t('jobs_app.count') + " : ").pack(side=tkinter.RIGHT)

        job_count_frame.pack(side=tkinter.RIGHT)

        # create a job detail frame
        detail_frame = tkinter.Frame(self.m)

        # create two frame : first contain basic info, second contain the description value wich can be a lot larger
        detail_job_frame = tkinter.Frame(detail_frame)
        detail_job_frame.grid(row=0, column=0)

        detail_description_frame = tkinter.Frame(detail_frame)
        detail_description_frame.grid(row=0, column=1)

        # create a url frame to display the url of the job and open to the page on click
        url_job_frame = tkinter.Frame(self.m)

        # add the differents value in the frames
        tkinter.Label(detail_job_frame, text=i18n.t('jobs_app.name')).grid(row=0, column=0)
        detail_job_name = tkinter.Entry(detail_job_frame, state="readonly")
        detail_job_name.grid(row=1, column=0)
        self.job_details.append(detail_job_name)
        tkinter.Label(detail_job_frame, text=i18n.t('jobs_app.enterprise')).grid(row=2, column=0)
        detail_job_enterprise = tkinter.Entry(detail_job_frame, state="readonly")
        detail_job_enterprise.grid(row=3, column=0)
        self.job_details.append(detail_job_enterprise)
        tkinter.Label(detail_job_frame, text=i18n.t('jobs_app.status')).grid(row=4, column=0)
        detail_job_status = tkinter.Entry(detail_job_frame, state="readonly")
        detail_job_status.grid(row=5, column=0)
        self.job_details.append(detail_job_status)
        tkinter.Label(detail_job_frame, text=i18n.t('jobs_app.application')).grid(row=6, column=0)
        detail_job_date = tkinter.Entry(detail_job_frame, state="readonly")
        detail_job_date.grid(row=7, column=0)
        self.job_details.append(detail_job_date)
        
        tkinter.Label(url_job_frame, text=i18n.t('jobs_app.url') + " : ").grid(row=0, column=0)
        detail_job_url = tkinter.Text(url_job_frame, height=1, state="disabled")
        detail_job_url.bind(sequence="<ButtonRelease-1>", func=self.OpenUrl)
        detail_job_url.grid(row=0, column=1)
        self.job_details.append(detail_job_url)

        tkinter.Label(detail_description_frame, text=i18n.t('jobs_app.desc')).grid(row=0, column=0)
        detail_job_desc = tkinter.Text(detail_description_frame, height=7, state="disabled")
        detail_job_desc.grid(row=1, column=0)
        self.job_details.append(detail_job_desc)

        self.timeout_details_label = tkinter.Label(detail_description_frame, text=i18n.t('jobs_app.timeout_exceed'))

        detail_frame.pack(side=tkinter.BOTTOM, before=job_count_frame)
        url_job_frame.pack(side=tkinter.BOTTOM, before=detail_frame, pady=5)

        # finish creating scrollbar
        scrollbar.config(command=self.yview)

    def exit_completly(self) :
        global return_value
        return_value = 0
        self.m.destroy()

    def yview(self, *args) :
        for index in range(len(self.listboxs)) :
            self.listboxs[index].yview(*args)

    def OnMouseWheel(self, event) :
        for index in range(len(self.listboxs)) :
            self.listboxs[index].yview("scroll", -event.delta, "units")
        # this prevents default bindings from firing, which
        # would end up scrolling the widget twice
        return "break"
    
    def OpenUrl(self, event) :
        value = event.widget.get('1.0', 'end-1c')
        # test if the url is correct before trying to open it
        if validators.url(value) : web.open_new(value)

    # check if the timeout given by the enterprise is expired 
    # -> the enterprise consider this application refused
    def CheckTimeOut(self, job_date : date, job_timeout) :
        if job_timeout != None :
            if type(job_date) == date :
                diff = date.today() - job_date
                if diff.days > job_timeout : 
                    return True
                return False
            return False
        return False

    # binded with the listbox to get the line in the list and use it on the rest of the app
    def on_select(self, event) :
        # get the correct index of the value when we edit a filtered version --> modify the correct job in the global list
        def find_index(data) :
            for index, job in enumerate(self.jobs_list) : 
                if job == data : return index
        selection = event.widget.curselection()
        if selection:
            if selection[0] != self.job_index :
                index = selection[0]
                data = self.current_job_list[index]["job_name"]
                #data = event.widget.get(index)
                self.event_listbox = event.widget
                self.selected_job = data
                self.job_index = find_index(self.current_job_list[index])
                # allow multi selection
                # will select the same job in each row help visualize each value of a job
                for i in range(len(self.listboxs)) :
                    if self.listboxs[i] != self.event_listbox :
                        self.listboxs[i].selection_clear(0, len(self.jobs_list))
                        self.listboxs[i].selection_set(index, index)
                    else : pass
                self.update_job_detail()
            else :
                pass
        else:
            pass
    
    # gather information from the selection to display each information on the bottom entry
    def update_job_detail(self) :
        def update_timeout(status : bool):
            if status :
                self.job_details[text_entry].config(height=6)
                self.timeout_details_label.grid(row=2, column=0)
            else :
                self.timeout_details_label.grid_forget()
                self.job_details[text_entry].config(height=7)

        if self.job_index != None :
            text_entry = None
            # get each field that will display an info and each key for the job to get the value needed
            for entry,i in zip(range(len(self.job_details)),self.jobs_list[self.job_index].keys()) :
                # check if a value is given, if not a blank value is set
                if self.jobs_list[self.job_index] != None :
                    temp_str = str(self.jobs_list[self.job_index][i])
                    if temp_str == "On going" : temp_str = i18n.t('jobs_app.ongoing')
                    elif temp_str == "Refused" : temp_str = i18n.t('jobs_app.refused')
                    elif temp_str == "Approved" : temp_str = i18n.t('jobs_app.approved')
                else :
                    temp_str = ""
                # get the type of the field to check if it's a Text or an Entry
                entry_type = type(self.job_details[entry])
                # if the field is a Text and not an Entry -> change the way to delete and insert the value
                if entry_type == tkinter.Text :
                    text_entry = entry
                    self.job_details[entry].config(state="normal") # set text to normal to modify the value
                    self.job_details[entry].delete('1.0', tkinter.END)
                    self.job_details[entry].insert('1.0', temp_str)
                    self.job_details[entry].config(state="disabled") # re-set the text to readonly as it should be
                else :
                    self.job_details[entry].config(state="normal") # set entry to normal to modify the value
                    self.job_details[entry].delete(0, tkinter.END)
                    self.job_details[entry].insert(0, temp_str)
                    self.job_details[entry].config(state="readonly") # re-set the entry to readonly as it should be
            if self.jobs_list[self.job_index]["job_date"] != "" :
                if self.CheckTimeOut(self.jobs_list[self.job_index]["job_date"], self.jobs_timeout[self.job_index]) :
                    if self.jobs_list[self.job_index]["job_status"] != "Refused" :
                        update_timeout(True)
                else : update_timeout(False)
            else : update_timeout(False)
                
     
    # pulled from a forum -> should be able to determine the screen value even on a multi monitor setup
    def get_curr_screen_geometry(self) :
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
        add_window = tkinter.Tk()
        add_window.title(i18n.t('jobs_app.add_job'))
        current_job_status = tkinter.StringVar(add_window)
        # add a boolean variable for testing if we want to add a job today
        check_button_value = tkinter.BooleanVar(add_window)
        timeout_button_value = tkinter.BooleanVar(add_window)
        timeout_label = tkinter.Label(add_window, text=i18n.t('jobs_app.days'), width=4)
        timeout_entry = tkinter.Entry(add_window, justify=tkinter.RIGHT)

        def submit_job() :
            job = self.job_template.copy()
            job["job_name"] = job_name_entry.get()
            job["enterprise_name"] = enterprise_name_entry.get()
            job["job_status"] = get_job_status(current_job_status.get())
            if job_date_entry.get_date() != date(2000, 1, 1) :
                job["job_date"] = job_date_entry.get_date()
            else : job["job_date"] = ""
            job["url"] = job_url_entry.get() 
            job["description"] = job_description.get()
            if timeout_button_value.get() : 
                if validate_timeout_value() :
                    self.jobs_timeout.append(int(timeout_entry.get()))
                else :
                    self.jobs_timeout.append(None)
            else : 
                self.jobs_timeout.append(None)
            self.jobs_list.insert(len(self.jobs_list), job)
            # refresh with the current list and not the global one
            # --> avoid getting back to all job with the filter value set to True
            self.refresh_all_listbox(self.current_job_list)
            add_window.destroy()

        def update_date() :
            # if the checkbutton is checked -> set the date to today and gey out the DateEntry to prevent changing the date
            if check_button_value.get() :
                today = date.today()
                job_date_entry.set_date(today)
                job_date_entry.config(state='disabled')
            # else re-activate the DateEntry to modify the date as we want
            else : 
                job_date_entry.config(state='enabled')

        def update_timeout() :
            if timeout_button_value.get() :
                timeout_label.grid(row=2, column=2, sticky="w")
                timeout_entry.grid(row=2, column=1)
            else :
                timeout_label.grid_forget()
                timeout_entry.grid_forget()

        def validate_timeout_value() :
            input_data = timeout_entry.get()
            if input_data:
                try:
                    int(input_data)
                    return True
                except ValueError:
                    return False
            return False

        def get_job_status(current_status : str) :
            if current_status == "" : return ""
            elif current_status == i18n.t('jobs_app.ongoing') : return "On going"
            elif current_status == i18n.t('jobs_app.refused') : return "Refused"
            elif current_status == i18n.t('jobs_app.approved') : return "Approved"
        
        tkinter.Label(add_window, text=i18n.t('jobs_app.name')).grid(row=0, column=0)
        tkinter.Label(add_window, text=i18n.t('jobs_app.enterprise')).grid(row=0, column=1)
        tkinter.Label(add_window, text=i18n.t('jobs_app.status')).grid(row=0, column=2)
        tkinter.Label(add_window, text=i18n.t('jobs_app.application')).grid(row=0, column=3)
        tkinter.Label(add_window, text=i18n.t('jobs_app.url')).grid(row=0, column=4)
        tkinter.Label(add_window, text=i18n.t('jobs_app.description')).grid(row=0, column=5)
        job_name_entry = tkinter.Entry(add_window)
        job_name_entry.grid(row=1, column=0, padx=5)
        enterprise_name_entry = tkinter.Entry(add_window)
        enterprise_name_entry.grid(row=1, column=1)
        tkinter.OptionMenu(add_window, current_job_status, *self.job_status).grid(row=1, column=2, padx=5)
        # create a frame to center the date Label betwwen the checkbutton and the date entry
        date_frame = tkinter.Frame(add_window)
        # add a check button to specify if the application has been done today
        tkinter.Checkbutton(date_frame, text=i18n.t('jobs_app.today'), variable=check_button_value, command=update_date).grid(row=0, column=0)
        job_date_entry = DateEntry(date_frame)
        job_date_entry.grid(row=0, column=1, padx=5)
        date_frame.grid(row=1, column=3)
        job_url_entry = tkinter.Entry(add_window)
        job_url_entry.grid(row=1, column=4)
        job_description = tkinter.Entry(add_window)
        job_description.grid(row=1, column=5, padx=4)
        tkinter.Checkbutton(add_window, text=i18n.t('jobs_app.add_timeout'), variable=timeout_button_value, command=update_timeout).grid(row=2, column=0)
        tkinter.Button(add_window, text=i18n.t('jobs_app.submit'), command=submit_job).grid(row=1, column=6, padx=2)

    # view the selected job in the listbox with detailled information
    def view_job(self) :
        if self.job_index != None :
            view_window = tkinter.Tk()
            view_window.title("Job : " + str(self.selected_job))
            tkinter.Label(view_window, text=i18n.t('jobs_app.name')).grid(row=0, column=0)
            tkinter.Label(view_window, text=self.selected_job, borderwidth=2, relief=tkinter.GROOVE).grid(row=0, column=1)

            tkinter.Label(view_window, text=i18n.t('jobs_app.enterprise')).grid(row=1, column=0)
            tkinter.Label(view_window, text=self.jobs_list[self.job_index]["enterprise_name"], borderwidth=2, relief=tkinter.GROOVE).grid(row=1, column=1)

            tkinter.Label(view_window, text=i18n.t('jobs_app.status')).grid(row=2, column=0)
            tkinter.Label(view_window, text=self.jobs_list[self.job_index]["job_status"], borderwidth=2, relief=tkinter.GROOVE).grid(row=2, column=1)

            tkinter.Label(view_window, text=i18n.t('jobs_app.application')).grid(row=3, column=0)
            tkinter.Label(view_window, text=str(self.jobs_list[self.job_index]["job_date"]), borderwidth=2, relief=tkinter.GROOVE).grid(row=3, column=1)

            tkinter.Label(view_window, text=i18n.t('jobs_app.description')).grid(row=4, column=0)
            tkinter.Label(view_window, text=self.jobs_list[self.job_index]["description"], borderwidth=2, relief=tkinter.GROOVE).grid(row=4, column=1)

            if self.jobs_timeout[self.job_index] != None : 
                job_timeout = self.jobs_timeout[self.job_index]
                if self.CheckTimeOut(self.jobs_list[self.job_index]["job_date"], job_timeout) and self.jobs_list[self.job_index]["job_status"] != "Refused":
                    tkinter.Label(view_window, text=i18n.t('jobs_app.timeout_exceed')).grid(row=5, columnspan=2)
                else :
                    if type(self.jobs_list[self.job_index]["job_date"]) == date :
                        if self.jobs_list[self.job_index]["job_status"] != "Refused" :
                            remaining = date.today() - self.jobs_list[self.job_index]["job_date"]
                            tkinter.Label(view_window, text=i18n.t('jobs_app.days_remaining') + " : " + str(remaining.days), borderwidth=2, relief=tkinter.GROOVE).grid(row=5, columnspan=2)
                        else :
                            tkinter.Label(view_window, text=i18n.t('jobs_app.job_refused'), borderwidth=2, relief=tkinter.GROOVE).grid(row=5, columnspan=2)
            else :
                tkinter.Label(view_window, text=i18n.t('jobs_app.no_timeout'), borderwidth=2, relief=tkinter.GROOVE).grid(row=5, columnspan=2)
            tkinter.Button(view_window, text=i18n.t('jobs_app.exit'), command=view_window.destroy).grid(row=6, column=0)
        else :
            messagebox.showwarning("View job","Select a job first !")

    # allow the modification of the selected job ( ex : job application refused )
    def edit_job(self) :
        if self.job_index != None :
            edit_window = tkinter.Tk()
            edit_window.title(i18n.t('jobs_app.edit_job') + " : " + str(self.selected_job))
            current_job_status = tkinter.StringVar(edit_window)
            # add a boolean variable for testing if we want to add a job today
            check_button_value = tkinter.BooleanVar(edit_window)
            check_change_value = tkinter.BooleanVar(edit_window)

            def submit_job() :
                job = self.job_template.copy() # get current job template to populate with the new values
                job["job_name"] = job_name_entry.get()
                job["enterprise_name"] = enterprise_name_entry.get()
                job["job_status"] = get_job_status(current_job_status.get())
                # if the date is today ( default with DateEntry ) but not wanted -> add nothing
                if job_date_entry.get_date() == date.today() and check_button_value == False :
                    job["job_date"] = ""
                else : job["job_date"] = job_date_entry.get_date() # else add the date to the job
                job["url"] = job_url_entry.get()
                job["description"] = job_description.get()
                self.jobs_list.pop(self.job_index)
                self.jobs_list.insert(self.job_index, job)
                # refresh with the current list and not the global one
                # --> avoid getting back to all job with the filter value set to True
                self.refresh_with_filter() 
                edit_window.destroy()

            def update_date() :
                # if the checkbutton is checked -> set the date to today and grey out the DateEntry to prevent changing the date
                if check_button_value.get() :
                    today = date.today()
                    job_date_entry.set_date(today)
                    job_date_entry.config(state='disabled')
                # else re-activate the DateEntry to modify the date as we want
                else : 
                    job_date_entry.config(state='enabled')
            
            def change_status() :
                if check_change_value.get() :
                    current_job_status.set(self.job_status[2])

            def get_job_status(current_status : str) :
                if current_status == "" : return ""
                elif current_status == i18n.t('jobs_app.ongoing') : return "On going"
                elif current_status == i18n.t('jobs_app.refused') : return "Refused"
                elif current_status == i18n.t('jobs_app.approved') : return "Approved"

            tkinter.Label(edit_window, text=i18n.t('jobs_app.name')).grid(row=0, column=0)
            tkinter.Label(edit_window, text=i18n.t('jobs_app.enterprise')).grid(row=0, column=1)
            tkinter.Label(edit_window, text=i18n.t('jobs_app.status')).grid(row=0, column=2)
            tkinter.Label(edit_window, text=i18n.t('jobs_app.application')).grid(row=0, column=3)
            tkinter.Label(edit_window, text=i18n.t('jobs_app.url')).grid(row=0, column=4)
            tkinter.Label(edit_window, text=i18n.t('jobs_app.description')).grid(row=0, column=5)
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
            tkinter.Checkbutton(date_frame, text=i18n.t('jobs_app.today'), variable=check_button_value, command=update_date).grid(row=0, column=0)
            
            job_date_entry = DateEntry(date_frame)
            if current_job["job_date"] != "" : job_date_entry.set_date(current_job["job_date"])
            job_date_entry.grid(row=0, column=1, padx=5)

            # grid the frame after the job status -> will center the Label above
            date_frame.grid(row=1, column=3)

            job_url_entry = tkinter.Entry(edit_window)
            job_url_entry.insert(0, str(current_job["url"]))
            job_url_entry.grid(row=1, column=4)

            job_description = tkinter.Entry(edit_window)
            job_description.insert(0, str(current_job["description"]))
            job_description.grid(row=1, column=5, padx=4)
            tkinter.Button(edit_window, text=i18n.t('jobs_app.submit'), command=submit_job).grid(row=1, column=6, padx=2)

            if self.jobs_timeout[self.job_index] != None :
                if current_job["job_date"] != "" :
                    timed_out = self.CheckTimeOut(current_job["job_date"], self.jobs_timeout[self.job_index])
                    if timed_out :
                        tkinter.Checkbutton(edit_window, 
                            text=i18n.t('jobs_app.timeout_refused'), 
                            variable=check_change_value, 
                            command=change_status).grid(row=2, column=0, columnspan=2)
                else :
                    tkinter.Label(edit_window, text=i18n.t('jobs_app.timeout_no_date')).grid(row=2, column=0, columnspan=3)
        else :
            messagebox.showwarning(i18n.t('jobs_app.edit_job'),i18n.t('jobs_app.warning_select'))


    def refresh_list(self, list_box : tkinter.Listbox, list : dict, list_value : str, creation : bool) :
        if creation :
            list_box.delete(0, tkinter.END)
            self.jobs_list = list
            self.jobs_timeout = []
            self.current_job_list = list
            self.enterprise_filter = []
            self.enterprise_is_filtered = False
        else :
            list_box.delete(0, tkinter.END)
            for line in range(len(list)) :
                job = list[line][list_value]
                if list_value == "job_status" and job != "" : 
                    if job == "On going" : job = i18n.t('jobs_app.ongoing')
                    if job == "Refused" : job = i18n.t('jobs_app.refused')
                    if job == "Approved" : job = i18n.t('jobs_app.approved')
                list_box.insert(line, str(job))
    
    def refresh_all_listbox(self, list_jobs : dict, value_creation = False) :
        if len(self.listboxs) != len(self.listboxs_value) : 
            print("error : inconsistency between number of listbox and the value displayed in it !")
        for i in range(len(self.listboxs)) :
            self.refresh_list(self.listboxs[i], list_jobs, self.listboxs_value[i], value_creation)
        # get the new number of job for the current list 
        number_of_jobs = len(self.current_job_list)
        if self.job_count != None : self.job_count.set(str(number_of_jobs)) # test if not None to avoid a crash at program init
        if self.enterprise_is_filtered == False and number_of_jobs > 0:
            for index in range(number_of_jobs) :
                current_enterprise = self.jobs_list[index]["enterprise_name"]
                if current_enterprise not in self.enterprise_filter : self.enterprise_filter.append(current_enterprise)
            self.refresh_dropdown_menu()

    def refresh_with_filter(self) :
        enterprise_selected = self.dropdown_variable.get()
        # check if we have selected an enterprise or we want to display all of them
        if enterprise_selected == "All" :
            self.enterprise_is_filtered = False
            self.current_job_list = self.jobs_list # get the global list when not in a filtered mode
            self.refresh_all_listbox(self.jobs_list)
        else :
            self.enterprise_is_filtered = True
            self.current_job_list = [] # before adding jobs, set the list to nothing
            for job in self.jobs_list :
                if job["enterprise_name"] == enterprise_selected :
                    # append only the job matching the enterprise selected
                    self.current_job_list.append(job)
                else : pass
            self.refresh_all_listbox(self.current_job_list)

    def refresh_languages(self, lang):
        if self.current_language != lang :
            self.current_language = lang
            i18n.set('locale', lang)
            global return_value
            return_value = 1
            self.m.destroy()
        else: 
            pass

    def refresh_dropdown_menu(self) :
        menu = tkinter.OptionMenu
        menu = self.dropdown_menu["menu"]
        menu.delete(0, tkinter.END)

        # bypass the automatic affectation of OptionMenu that doesn't work for my need 
        menu.add_command(label="All", command = lambda value="All" : (self.dropdown_variable.set(value), self.refresh_with_filter()))
        for string in self.enterprise_filter:
            if string != "" :
                menu.add_command(label=string,
                            command = lambda value=string: (self.dropdown_variable.set(value), self.refresh_with_filter())) 
            else : pass

    # get the name of the new file and set it in a class variable then close the window
    def create_file(self) :
        def return_name() : 
            self.filename = entry.get()
            # set the file was not written with the extension -> add it ourselves
            if (self.filename.endswith('.csv') == False) :
                self.filename = self.filename + str('.csv')
            self.refresh_all_listbox([], value_creation=True)
            n.destroy()
        n = tkinter.Tk()
        n.title(i18n.t('jobs_app.new_file'))
        tkinter.Label(n, text=i18n.t('jobs_app.filename') + " : ").grid(row=0)
        entry = tkinter.Entry(n)
        entry.grid(row=0, column=1)
        submit_button = tkinter.Button(n, text=i18n.t('jobs_app.submit'), command=return_name)
        submit_button.grid(row=1)

    # get the path to the file, set it in a class variable to be used in the main app
    def select_file(self) :
        filetype = (
            ('excel files', '*.csv'),
            ('All files', '*.*')
        )

        filename = filedialog.askopenfilename(
            title=i18n.t('jobs_app.open_file'),
            initialdir=Path.cwd(), # Use Path to get current working directory
            filetypes=filetype
        )

        # check if a file was select before calling the file loader
        if filename != "" :
            self.filename = filename
            self.load_list_from_file(self.filename)
    
    # write into a csv file the modified data to keep them between use
    def save_file(self) :
        # needed because lambda command doesn't properly get the value in the Entry
        def get_value():
            self.filename = file.get()
        # add the extension if necessary
        def check_extensions():
            if (self.filename.endswith('.csv') == False) :
                self.filename = self.filename + str('.csv')
        # ask for a filename if none is set
        if self.filename == "" :
            filename_window = tkinter.Tk()
            filename_window.title(i18n.t('jobs_app.filename'))
            file = tkinter.StringVar(filename_window)

            tkinter.Label(filename_window, text=i18n.t('jobs_app.ask_filename')).pack()
            tkinter.Entry(filename_window, textvariable=file).pack()
            tkinter.Button(filename_window, text=i18n.t('jobs_app.submit'), command = lambda value=file.get(): (setattr(self, 'filename', value), get_value(), check_extensions(), self.save_file(), filename_window.destroy())).pack()
        else :
            # to change with the dump of the data in the csv
            with open(self.filename, "w", newline='') as save_file : 
                csv_out = csv.writer(save_file, delimiter=";", lineterminator="\n")
                for i, row_out in zip(range(len(self.jobs_list)),self.jobs_list) :
                    job_out = [row_out["job_name"],row_out["enterprise_name"],row_out["job_status"],row_out["job_date"],row_out["url"],row_out["description"]]
                    job_out.append(self.jobs_timeout[i])
                    for j, entry in zip(range(len(job_out)),job_out) :
                        if entry == None :
                            job_out[j] = ""
                    csv_out.writerow(job_out)

    # load the file selected from the file picker
    def load_list_from_file(self, path_to_file) :
        if Path(path_to_file).is_file() :
            # open the file and load jobs into a list to send it in refresh_list
            jobs_from_file = []
            # reset the filter when loading a new file
            self.dropdown_variable.set("All")
            # reset all listbox before displaying the new one
            self.refresh_all_listbox(jobs_from_file, True) 
            with open(path_to_file) as file:
                reader = csv.reader(file, delimiter=";")
                for values in reader:
                    # test if the job has all the values in the file -> if not add a blank one
                    value_quantity = len(self.job_template) + 1
                    if len(values) < value_quantity : 
                        for i in range(len(values), value_quantity) :
                            values.append("")
                    # reference the value of the job in the correct properties
                    #job = {"job_name" : values[0], "enterprise_name" : values[1], "job_status" : values[2], "job_date" : values[3], "url" : values[4] ,"description" : values[5]}
                    job = self.job_template.copy()
                    i = 0
                    for key in job.keys() :
                        job[key] = values[i]
                        i+=1

                    if values[i] == '' : timeout = None
                    else : timeout = int(values[i])
                    self.jobs_timeout.append(timeout)

                    # convert string date to proper date
                    if job["job_date"] != "" :
                        job_date = job["job_date"].split("-")
                        job["job_date"] = date(int(job_date[0]), int(job_date[1]), int(job_date[2]))

                    jobs_from_file.append(job)
            # refresh the listbox to dipslay the jobs read from the file
            self.refresh_all_listbox(self.jobs_list)
        else :
            # create the file and refresh the listbox
            # needed if the file picker send a non-existant file
            self.file = open(self.filename, "w")
            self.refresh_all_listbox([], True)


if __name__ == "__main__":

    # handle the X button of the app like normal 
    # but change also the value of return_value to exit the while loop
    def closing_button() :
        global return_value
        return_value = 0
        main.destroy()

    def show_start_error() :
        messagebox.showerror("No language found !", "No language found in the translations folder make sure it exist and have at least one language file")

    # use a subfolder aside of the app for the translation
    translation_folder = Path.cwd().as_posix() + "/translations"

    # test if the folder exist before trying to load languages file
    if Path.exists(Path(translation_folder)) :

        # set the variable to nothing
        available_translation = []
        # use this folder to try to load the translation files
        i18n.load_path.append(translation_folder)
        # iterate in every file of the folder to find a language file 
        # and propose it to the user in the app
        for file in Path(translation_folder).iterdir() :
            # try to slice the file name in three part : jobs_app - language - yml
            # ex : jobs_app.en.yml
            slices = str(file.name).split('.')
            if slices != 3 : pass # if it doesn't match exlude this file
            available_translation.append(slices[1])

        # verify that at least one language file is present before launching the application
        if len(available_translation) != 0 :

            # use locale to get system locale and use it as default if it exist
            system_locale = locale.getlocale()[0]
            # search in known translations if the system locale exist
            for lang in available_translation :
                if system_locale.__contains__(lang) : 
                    i18n.set('locale', lang)
            
            while(return_value != 0):
                # tkinter creation
                main = tkinter.Tk()

                # call the class to run the windows app
                app = WindowApp(main, available_translation)

                # change how the X button is handled to add the modification of the return value
                main.protocol("WM_DELETE_WINDOW", closing_button)

                # display the window app
                main.mainloop()

        else :
            show_start_error()

    else : 
        Path.mkdir(translation_folder)
        show_start_error()
