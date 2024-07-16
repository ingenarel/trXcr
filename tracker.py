import psutil, time, json
import os
   
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
                sessions[tracked_tasks].append({"starttime": time.asctime(), "endtime": None})
            else:
                sessions[tracked_tasks].append({"starttime": None, "endtime": None})

    else:
        # print("last_session!=None")
        sessions = last_session
        for tracked_tasks in list_of_tracked_tasks:
            if tracked_tasks not in currently_tracked_tasks:
                # print("tracked_tasks not in currently_tracked_tasks")
                if sessions[tracked_tasks][-1]["starttime"] != None and sessions[tracked_tasks][-1]["endtime"] == None:
                    # print("sessions[tracked_tasks][-1]['endtime'] == None")
                    sessions[tracked_tasks][-1]["endtime"] = time.asctime()
            else:
                if sessions[tracked_tasks][-1]["starttime"] == None:
                    sessions[tracked_tasks][-1]["starttime"] = time.asctime()
                else:
                    if sessions[tracked_tasks][-1]["endtime"] != None:
                        # print("sessions[tracked_tasks][-1]['endtime'] != None:")
                        sessions[tracked_tasks].append({"starttime": time.asctime(), "endtime": None})

    return sessions 

def main():
    tracked:list = ["nvim", "firefox", "yazi", "discord"]
    write_delay:int = 60
    update_delay:int = 1
    x = True
    while True:
        for _ in range(write_delay):
            currently_tracked = set(process.info["name"] for process in psutil.process_iter(["name"]) if process.info["name"] in tracked)
            log = log_parser(
                    list_of_tracked_tasks=tracked, 
                    currently_tracked_tasks=currently_tracked,
                    last_session=log if x == False else None)
            # print(currently_tracked)
            print(log)
            time.sleep(update_delay)
            os.system("clear")
            x = False
        with open(f"{time.strftime('%h-%j')}.log", "w") as day_log_file:
            day_log_file.writelines(json.dumps(log))
        print("log written")

if __name__ == "__main__":
    main()
