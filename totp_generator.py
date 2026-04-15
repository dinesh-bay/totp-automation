import pyotp
import os

# Replace with your secret key (see Security section in README)
secret_key = "YOUR_SECRET_KEY_HERE"

totp = pyotp.TOTP(secret_key)
current_otp = totp.now()

# Write OTP to file
output_path = os.path.join(os.path.dirname(__file__), "totp_output.txt")
with open(output_path, "w") as f:
    f.write(current_otp)

print(f"OTP generated: {current_otp}")
