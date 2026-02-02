"""
    @project: Windify
    @Author: niu
    @file: playground.py.py
    @date: 2026/2/1 14:35
    @desc:
"""
import bcrypt

password = "020121"
hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
print(f"Hashed: {hashed}")