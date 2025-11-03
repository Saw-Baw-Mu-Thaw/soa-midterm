# otp_cache.py
from datetime import datetime, timedelta
import random
import threading
from typing import Dict, Optional


class OTPCache:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, ttl_seconds: int = 300, max_attempts: int = 5):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init(ttl_seconds, max_attempts)
        return cls._instance

    def _init(self, ttl_seconds: int, max_attempts: int):
        self.cache: Dict[int, dict] = {}
        self.lock = threading.Lock()
        self.ttl = ttl_seconds
        self.max_attempts = max_attempts
        self._start_cleanup()

    def _start_cleanup(self):
        def cleanup():
            while True:
                now = datetime.now()
                with self.lock:
                    expired = [
                        tid for tid, d in self.cache.items()
                        if now > d["expires_at"]
                    ]
                    for tid in expired:
                        self.cache.pop(tid, None)
                threading.Event().wait(30)   # every 30 sec

        t = threading.Thread(target=cleanup, daemon=True)
        t.start()

    def generate_code(self) -> str:
        return "".join(random.choices("0123456789", k=6))

    def set(self, transaction_id: int) -> int:
  
     code = self.generate_code()  
     expires_at = datetime.now() + timedelta(seconds=self.ttl)
 
     with self.lock:
         self.cache[transaction_id] = {
             "code": code,           
             "attempts": 0,
             "verified": False,
             "expires_at": expires_at,
         }
     return self.ttl

    def get(self, transaction_id: int) -> Optional[dict]:
        with self.lock:
            data = self.cache.get(transaction_id)
            if not data or datetime.now() > data["expires_at"]:
                self.cache.pop(transaction_id, None)
                return None
            return data.copy()

    def save_attempts(self, transaction_id : int, attempts: int):
        with self.lock:
            data = self.cache.get(transaction_id)
            data['attempts'] = attempts
            self.cache.update({transaction_id : data})

    def verify(self, transaction_id: int, code: str) -> dict:
        data = self.get(transaction_id)
        if not data:
            return {"success": False, "message": "OTP not found or expired"}

        if data["verified"]:
            return {"success": False, "message": "OTP already used"}

        if data["attempts"] >= self.max_attempts:
            self.delete(transaction_id)
            return {"success": False, "message": "Max attempts exceeded"}

        data["attempts"] += 1
        self.save_attempts(transaction_id, data["attempts"])

        if data["code"] == code:
            data["verified"] = True
            return {"success": True, "message": "OTP verified"}
        else:
            remaining = self.max_attempts - data["attempts"]
            return {
                "success": False,
                "message": "Invalid OTP",
                "remaining_attempts": remaining,
            }

    def delete(self, transaction_id: int):
        with self.lock:
            self.cache.pop(transaction_id, None)

    def remaining_seconds(self, transaction_id: int) -> Optional[int]:
        data = self.get(transaction_id)
        if not data:
            return None
        return max(0, int((data["expires_at"] - datetime.now()).total_seconds()))