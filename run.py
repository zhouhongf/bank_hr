import subprocess


if __name__ == '__main__':
    list_server = [
        ["pipenv", "run", "python", "scheduled_task.py"],
    ]

    list_process = []
    for server in list_server:
        process = subprocess.Popen(server)
        list_process.append(process)

    for process in list_process:
        process.wait()
        if process.poll():
            exit(0)
