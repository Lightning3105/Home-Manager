from requests import post

def broadcast(*args):
	message = " ".join(args)
	post("http://192.168.1.4:3001/assistant", json={"command": message, "user": "james", "broadcast": "true"})

if __name__ == '__main__':
    broadcast("This is a test")
