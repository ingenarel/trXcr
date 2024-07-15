import psutil, time

tracked:list = ["nvim", "yazi", "firefox"]

write_delay:int = 10
update_delay:int = 1

data = []

for _ in range(write_delay):
    currently_tracked = set(process.info["name"] for process in psutil.process_iter(["name"]) if process.info["name"] in tracked)
    for task in tracked:
        if task in tracked and task in currently_tracked:
            data.append(f"{task}: {time.asctime()}")
    time.sleep(update_delay)

with open("day_log.log", "a") as day_log:
    for line in data:
        day_log.write(f"{line}\n")
