# Chat_system
# 📡 Python Socket Chat System

### 👨‍💻 Developed by: Orel Cohen & Oshri Halevi  
### 🧠 Technologies: Python, TCP, Multi-threading, Socket Programming

---

## 📌 Project Description

This project is a **real-time text-based chat system** built using **Python sockets and the TCP protocol**.  
It includes a central **server** and multiple **clients** that can connect, start private conversations, and exchange messages.

The system was developed as part of a university networking course, focusing on socket programming and client-server communication.

---

## 🧩 Features

- 🔗 Full-duplex communication using TCP
- 👥 Supports multiple clients (5+)
- 🧵 Server handles multiple clients using threads
- 📤 Private messaging between users
- 🧑‍💻 Unique usernames
- 💬 Command-based interface: `/chat`, `/message`, `/help`, `/quit`
- ⚠️ Error handling for disconnections and invalid commands

---

## 🛠️ How to Run

> Make sure you have Python 3.x installed

### 1. Run the Server

```bash
python chat_server.py
