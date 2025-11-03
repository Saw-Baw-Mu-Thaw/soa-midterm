#repository/otp_repository.py
from datetime import datetime
from typing import Dict


class OTPRepository:
    def __init__(self):
        pass
    
    def validate_otp_request(self, transaction_data: Dict) -> dict:
        try:
            # Validate required fields
            if not transaction_data.get('transaction_id'):
                return {
                    'valid': False,
                    'message': 'Transaction ID is required'
                }
            
            if not transaction_data.get('customer_email'):
                return {
                    'valid': False,
                    'message': 'Customer email is required'
                }
            
            if not transaction_data.get('customer_name'):
                return {
                    'valid': False,
                    'message': 'Customer name is required'
                }
            
            # Validate transaction status
            status = transaction_data.get('status', '').upper()
            if status not in ['PENDING', 'INITIATED']:
                return {
                    'valid': False,
                    'message': f'Transaction status "{status}" is not eligible for OTP'
                }
            
            return {
                'valid': True,
                'message': 'Transaction data is valid for OTP generation'
            }
            
        except Exception as e:
            print(f"[OTP Repository] Error validating request: {e}")
            return {
                'valid': False,
                'message': f'Validation error: {str(e)}'
            }
    
    