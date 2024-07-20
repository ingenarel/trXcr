import psutil, time, json, os, argparse, re
   
def smart_multi(multistring:str):
    return re.sub(r" +", " ", multistring)

def check_last_log():
    try:
        y = sorted(os.listdir("log"))[-1]
    except FileNotFoundError:
        exit(smart_multi("""
             The program can't start because the log directory isn't created.
             
             If this is your first time using this program, you need to provide the tasknames that you want to track.
             Like firefox, nvim, yazi for example.

             And if you ran this program before and this is still happening, check if your log directory is in the same
             directory as the program or not. also check permissions and double check the directory.
             The log directory and it's subdirectories shouldn't be empty or shouldn't be tampered with.
             
             for more info, run this program with --help.
             """))
    except IndexError:
        exit(smart_multi("""
             The program can't start because log directory is created but the program thinks it's empty.
             
             If this is your first time using this program, you need to provide the tasknames that you want to track.
             Like firefox, nvim, yazi for example.

             And if you ran this program before and this is still happening, check if your log directory is in the same
             directory as the program or not. also check permissions and double check the directory. The log directory
             shouldn't be empty or shouldn't be tampered with.
             
             for more info, run this program with --help.
             """))

    # print(y)
    try:
        yd = sorted(os.listdir(f"log/{y}"))[-1]
    except IndexError:
        exit(smart_multi("""
             The program can't start because log directory is created but the latest year directory is empty.
             
             If this is your first time using this program, you need to provide the tasknames that you want to track.
             Like firefox, nvim, yazi for example.

             And if you ran this program before and this is still happening, check if your log directory is in the same
             directory as the program or not. also check permissions and double check the directory. The log directory
             and it's subdirectories shouldn't be empty or shouldn't be tampered with.
             
             for more info, run this program with --help.
             """))
    # print(yd)
    try:
        h = sorted(os.listdir(f"log/{y}/{yd}"))[-1]
    except IndexError:
        exit(smart_multi("""
             The program can't start because log directory and the year directory exists, but there isn't a valid
             year's day directory, or it's empty.
             
             If this is your first time using this program, you need to provide the tasknames that you want to track.
             Like firefox, nvim, yazi for example.

             And if you ran this program before and this is still happening, check if your log directory is in the same
             directory as the program or not. also check permissions and double check the directory. The log directory
             and it's subdirectories shouldn't be empty or shouldn't be tampered with.
             
             for more info, run this program with --help.
             """))
    # print(h)
    try:
        with open(
                f"log/{y}/{yd}/{h}",
                "r"
                ) as load_log_file:
            try_load = json.load(load_log_file)
            try_load = None
    except json.decoder.JSONDecodeError:
        exit(smart_multi(f"""
        There is something wrong with log/{y}/{yd}/{h} file. Check it's validity. It shouldn't be empty.
        If it's empty, delete it. And after deleting it, if the parent directory is empty, delete it too.
             """))
    return y, yd, h

def read_tracked_programs_from_log():
    y, yd, h = check_last_log()
    with open(
            f"log/{y}/{yd}/{h}",
            "r"
            ) as load_log_file:
            file_load = json.load(load_log_file)
    return [task for task in file_load if task != "tracking_start_and_end_time"]

def log_parser(
    list_of_tracked_tasks:list=[],
    currently_tracked_tasks:list=[],
    last_session=None,
        ):
    if last_session==None:
        # print("last_session==None")
        sessions:dict = {
                "tracking_start_and_end_time": 
                    {
                        "starttime": time.strftime('%M-%S'),
                        "endtime": time.strftime('%M-%S'),
                    }
                }
        for tracked_tasks in list_of_tracked_tasks:
            sessions[tracked_tasks]=[] # this is sessions list
            if tracked_tasks in currently_tracked_tasks:
                # print("tracked_tasks in currently_tracked_tasks")
                sessions[tracked_tasks].append(
                        {
                            "starttime": time.strftime('%M-%S'), 
                            "endtime": None,
                        }
                    )
            else:
                sessions[tracked_tasks].append(
                        {
                            "starttime": None,
                            "endtime": None,
                        }
                    )

    else:
        # print("last_session!=None")
        sessions:dict=last_session
        for tracked_tasks in list_of_tracked_tasks:
            if tracked_tasks not in currently_tracked_tasks:
                # print("tracked_tasks not in currently_tracked_tasks")
                try:
                    if sessions[tracked_tasks][-1]["starttime"] != None and sessions[tracked_tasks][-1]["endtime"] == None:
                        # print("sessions[tracked_tasks][-1]['endtime'] == None")
                        sessions[tracked_tasks][-1]["endtime"] = time.strftime('%M-%S')
                except KeyError:
                    sessions[tracked_tasks]=[] # this is sessions list
                    sessions[tracked_tasks].append(
                        {
                            "starttime": None,
                            "endtime": None,
                        }
                    )
            else:
                try:
                    if sessions[tracked_tasks][-1]["starttime"] == None:
                        sessions[tracked_tasks][-1]["starttime"] = time.strftime('%M-%S')
                except KeyError:
                    sessions[tracked_tasks]=[] # this is sessions list
                    sessions[tracked_tasks].append(
                        {
                            "starttime": time.strftime('%M-%S'),
                            "endtime": None,
                        }
                    )
                else:
                    if sessions[tracked_tasks][-1]["endtime"] != None:
                        # print("sessions[tracked_tasks][-1]['endtime'] != None:")
                        sessions[tracked_tasks].append(
                                {
                                    "starttime": time.strftime('%M-%S'), 
                                    "endtime": None
                                }
                            )
        sessions["tracking_start_and_end_time"]["endtime"]=time.strftime('%M-%S')

    return sessions 

def arguments():
    parser = argparse.ArgumentParser(
            epilog="""
            This can be used alone for another time tracker's backend.
            Altho this should be used with the other files in this program.
            """,
            )

    parser.add_argument(
            "-wd",
            "--write_delay",
            type=int, 
            default=60,
            help="""
            This is the delay that your data gets written down in the log.
            It should be an int. The default value is 60.
            Lower values means more writes, that means that in the case of a power outage,
            or a system shutdown, your data loss would be less, it would be more
            accurate. However it can also wear out your storage device with
            the constant writing on the storage device.
            Higher values means less writes, that means that in the case of a power outage,
            or a system shutdown, your data loss would be more, it would be less
            accurate. However it doesn't wear out your storage device that much
            because of the delay between writes. To actually calculate how long
            each write will take, you should multiply it with the update delay.
            That means if update delay is 1, and the write delay is 60, that 
            means you should get a write delay of 1*60 = 60 seconds. if update 
            delay is 1.5, and the write delay is 50, that means you should get 
            a write delay of 1.5*50 = 75 seconds.
            """,
            )

    parser.add_argument(
            "-ud",
            "--update-delay",
            type=float,
            default=1,
            help="""
            This is the update delay that your data gets updated.
            It can be an int or a float. The default value is 1. Setting this something
            that's less that 1 isn't gonna make a difference cz the the program
            doesn't write down the milliseconds in the database. it writes the seconds.
            so making this less than 1 should make no difference in accuracy while it
            will make this program use more resource too. However you can set it
            to less than one because of freedom of choice. if you set the value 
            that's higher than 1, the update delay is gonna be much more slow, so
            the data is gonna be much less accurate. But if your system has a hard
            time running this program in the background all the time, you can se
            this to something that's more than 1. that's not guarantied to fix it,
            however it might help.
            """,
            )

    parser.add_argument(
            "-t",
            "--track",
            type=str,
            default=None,
            help="""
            This is the list of files that the program would track. The default 
            value is None. If the value isn't provided, the program would try to
            read the latest file from the log, and try to track the programs that
            the latest log has. to provide the list of processes that you want to
            track, you would need to seperate them by commas, and no spaces should
            be in the list. Example: "-t firefox,discord,nvim,yazi,lazygit,make".
            if you put something and see that it's not being tracked, you should
            open your os's task manager and see what's the task's name. because
            the script check's the processes name then tracks from it.
            """
            )

    parser.add_argument(
            "-ut",
            "--update-tracked",
            type=str,
            default=None,
            help="""
            This is the list of program's that you want to add to the currently
            tracked list.
            """
            )

    parser.add_argument(
            "-d",
            "--debug",
            type=str,
            default="False",
            help="""
            This is the output's value. The default value is False. If the value
            is set to true/t/y/yes, then it will run in debug mode. it's case
            insensitive, otherwise, the value would be false.
            """
            )

    args = parser.parse_args()


    # update delay
    if args.update_delay < 1:
        print("Update delay is less than 1. This isn't recommended.")
    # update delay

    # write delay
    if args.update_delay * args.write_delay < 1:
        print("update delay*write delay is less than one. this will wear out your system")
    # write delay

    # track and update tracked
    if args.track != None and args.update_tracked == None:
        tracked = set(args.track.split(","))
    # except AttributeError:
    elif args.track == None and args.update_tracked == None:
        tracked = set(read_tracked_programs_from_log())
    elif args.track == None and args.update_tracked != None:
        tracked = set(read_tracked_programs_from_log() + args.update_tracked.split(","))
    elif args.track != None and args.update_tracked != None:
        print("why bro?")
        tracked = set(args.track.split(",") + args.update_tracked.split(","))
    # track and update tracked

    # debug
    if args.debug.lower() in ["true", "t", "y", "yes"]:
        debug = True
    else:
        debug = False
    # debug

    return {
            "wd": args.write_delay,
            "ud": args.update_delay,
            "t": tracked,
            "d": debug,
            }
    
def main():
    args = arguments()
    if args["d"] == True:
        print(f"args:\n{args}")
    tracked:set = args["t"]
    write_delay:int = args["wd"]
    update_delay:int = args["ud"]
    x = None

    try:
        with open(
                f"log/{time.strftime('%Y')}/{time.strftime('%j')}/{time.strftime('%H')}.json",
                "r"
                ) as load_log_file:
            file_load = json.load(load_log_file)
        x = "file"
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        pass
    
    while True:
        for _ in range(write_delay):
            currently_tracked = set(
                    process.info["name"] for process in psutil.process_iter(["name"]) if process.info["name"] in tracked
                    )
            log_infos = {
                    "list_of_tracked_tasks": tracked,
                    "currently_tracked_tasks": currently_tracked,
                    }
            if x == "done":
                last_log = log_parser(
                        **log_infos,
                        last_session=last_log
                        )
            elif x == "file":
                last_log = log_parser(
                        **log_infos,
                        last_session=file_load
                        )
            elif x == None:
                 last_log = log_parser(
                        **log_infos,
                        last_session=None
                        )
            if args["d"] == True:
                print(last_log)
            time.sleep(update_delay)
            x = "done"
        
        hour_log_file_path = f"log/{time.strftime('%Y')}/{time.strftime('%j')}"

        try:
            os.makedirs(f"{hour_log_file_path}")
        except FileExistsError:
            pass
        with open(
                f"{hour_log_file_path}/{time.strftime('%H')}.json",
                "w"
                ) as hour_log_file:
            json.dump(last_log, hour_log_file, indent=4)
            if args["d"] == True:
                print("log written\n")
        if time.strftime('%H') != check_last_log()[2][:2]:
            x = None

if __name__ == "__main__":
    main()
