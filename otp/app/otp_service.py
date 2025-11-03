import requests
from .otp_cache import OTPCache
from .repository.config import EMAIL_SERVICE_URL, OTP_TTL_SECONDS, MAX_OTP_ATTEMPTS

cache = OTPCache(OTP_TTL_SECONDS, MAX_OTP_ATTEMPTS)

class OTPService:
    async def generate(self, transaction_id: int) -> dict:
        if cache.get(transaction_id):
            remaining = cache.remaining_seconds(transaction_id) or 0
            return {"success": False, "message": f"Wait {remaining}s"}

        # Generate & store OTP
        cache.set(transaction_id)
        data = cache.get(transaction_id)
        code = data["code"]

        print(f"\nOTP FOR TXN {transaction_id}: {code}\n")

        return {
            "success": True,
            "message": "OTP generated & sent",
            "data": {
                "transaction_id": transaction_id,
                "otp_code": code,
                "expires_in_seconds": OTP_TTL_SECONDS
            }
        }

    def verify(self, transaction_id: int, code: str) -> dict:
        result = cache.verify(transaction_id, code)
        return {
            "success": result["success"],
            "verified": result["success"],
            "message": result["message"],
            "remaining_attempts": result.get("remaining_attempts")
        }

    async def resend(self, transaction_id: int) -> dict:
        cache.delete(transaction_id)
        return await self.generate(transaction_id)