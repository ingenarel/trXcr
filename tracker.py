import psutil, time, json, os, argparse
   
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
                if sessions[tracked_tasks][-1]["starttime"] != None and sessions[tracked_tasks][-1]["endtime"] == None:
                    # print("sessions[tracked_tasks][-1]['endtime'] == None")
                    sessions[tracked_tasks][-1]["endtime"] = time.strftime('%M-%S')
            else:
                if sessions[tracked_tasks][-1]["starttime"] == None:
                    sessions[tracked_tasks][-1]["starttime"] = time.strftime('%M-%S')
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
            It can be an int or a float. The default value is 1. using this something
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
            be in the list. Example: "-t firefox,discord,nvim,yazi,lazygit,make"
            """
            )

    parser.parse_args()
    
def main():
    arguments()
    tracked:list = [
            "nvim",
            "firefox",
            "yazi", 
            "discord",
            "make",
            "python",
            "lazygit",
            "paru",
            "pacman",
            ]
    write_delay:int = 10
    update_delay:int = 1
    x = None
    try:
        with open(
                f"log/{time.strftime('%Y')}/{time.strftime('%j')}/{time.strftime('%H')}.log",
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
            print(last_log)
            time.sleep(update_delay)
            os.system("clear")
            x = "done"
        
        hour_log_file_path = f"log/{time.strftime('%Y')}/{time.strftime('%j')}"

        try:
            os.makedirs(hour_log_file_path)
        except FileExistsError:
            pass
        with open(
                f"{hour_log_file_path}/{time.strftime('%H')}.log",
                "w"
                ) as hour_log_file:
            json.dump(last_log, hour_log_file, indent=4)
            print("log written")
        # except

if __name__ == "__main__":
    main()
