import socket
from intentlang import MagicIntent
MagicIntent.hack_str(cache=True, record=True)

print("What is 2+2".o(int))

data = [1, 2, 3, 4, 5]

if "sum of all numbers".i(data).o(float) > 10:
    print("Sum of all numbers is greater than 10")
else:
    print("Sum of all numbers is less than or equal to 10")

res = "filter out all lucky numbers".i(data).c("even numbers are lucky numbers").o(list[int])
print(res)


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
"Connect to example.com using the initialized socket object and send HTTP GET request".i(sock).r("Don't receive data, only send, and don't close the socket")()
print(sock.recv(15).decode())


sock_1: socket.socket = "创建socket对象并向example.com发起HTTP GET请求".o(socket.socket).r("Don't receive data, only send, and don't close the socket")
print(sock_1.recv(15).decode())
