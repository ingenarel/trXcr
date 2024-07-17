import psutil, time, json, os, argparse
   
def log_parser(
    list_of_tracked_tasks:list=[],
    currently_tracked_tasks:list=[],
    last_session=None,
        ):
    if last_session==None:
        # print("last_session==None")
        sessions = {}
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
        sessions = last_session
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

    return sessions 

def arguments():
    parser = argparse.ArgumentParser(
            epilog="""
            This can be used alone for another time tracker's backend.
            Altho this should be used with the other files in this program.
            """
            )
    parser.add_argument(
            "-wd",
            "--write_delay",
            type=int, default=60,
            help="""
            This is the write delay. It should be an int, in seconds. The default value is 60.
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
    except FileNotFoundError:
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
            hour_log_file.writelines(json.dumps(last_log))
            print("log written")
        # except

if __name__ == "__main__":
    main()
