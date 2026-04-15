# TOTP Automation — Dynamic Token Retrieval from Authenticator App

Automate the retrieval of Time-based One-Time Passwords (TOTP) from authenticator apps like Microsoft Authenticator, Google Authenticator, etc.

This was built to solve a real problem: **MFA tokens change every 30 seconds, and there was no way to include them in automated test flows.** External user accounts require MFA and it can't be disabled for security reasons. So we built a way to programmatically generate the same TOTP that the authenticator app generates — and plug it into the automation.

This solution has been **integrated with Tosca seamlessly** and is live for multiple applications. It can be integrated with any test automation framework or workflow automation tool.

## How It Works

Authenticator apps use a shared secret key to generate time-based 6-digit codes. The same algorithm (`TOTP` — RFC 6238) can run in Python using the `pyotp` library. The script generates the exact same code that your authenticator app shows at that moment.

```
Secret Key (one-time capture) → pyotp → 6-digit TOTP → Pass to automation framework
```

The entire token retrieval process takes less than a second.

## Important

- This solution retrieves the 6-digit token using the **authenticator app's secret key only**
- It does **NOT** work for SMS-based or call-based OTPs
- The TOTP is time-based and valid for **30 seconds only**

## Pre-requisites

1. **Python 3.x** installed on the machine where your automation runs
2. **pyotp library** installed:
   ```bash
   pip install pyotp
   ```
3. **Secret key** from your authenticator app setup:
   - When you set up MFA for an account, the service shows a QR code or a secret key
   - Capture this secret key during the initial MFA setup (one-time activity)
   - This is the same key the authenticator app uses internally

## Usage

```python
import pyotp

secret_key = "YOUR_SECRET_KEY_HERE"

totp = pyotp.TOTP(secret_key)
current_otp = totp.now()

print(current_otp)  # 6-digit code, same as your authenticator app
```

Or run the script directly:

```bash
python totp_generator.py
```

The script writes the OTP to `totp_output.txt` which your automation framework can read.

## Integration with Test Automation

This has been integrated with **Tosca** seamlessly. The general approach:

1. The Python script generates the TOTP and writes it to a file
2. Your automation framework reads the file and enters the OTP in the authentication window
3. The entire flow — generate, read, enter — should complete within 30 seconds (the TOTP validity window)
4. If your framework is slow, implement a **retry/loop mechanism** to regenerate the OTP if it expires

**Works with any framework** — Tosca, Playwright, Selenium, UiPath, or any workflow automation. The script is standalone. Just plug and play.

For better reuse, create a reusable test step/function in your framework so your team can use it without changing the structure.

## Security — Read This Carefully

The secret key is the most sensitive piece of this solution. **Treat it like a password.**

### Do

- Encrypt the secret key in your automation framework before using it
- Pass the secret key as an environment variable or encrypted parameter, never hardcoded
- Restrict access to the machine where the script runs
- Delete the output file (`totp_output.txt`) after your automation reads the OTP

### Do NOT

- Store the secret key in plain text in the script
- Commit the secret key to any repository
- Share the script with the secret key embedded
- Leave the OTP output file on the machine after use

### Cleaning Up the OTP File

After your automation reads the OTP, **delete the output file immediately.** And don't just delete it — **empty your recycle bin** as well. The file contains a valid (though time-limited) OTP, and the secret key could potentially be reverse-engineered from patterns if multiple OTPs are collected.

```python
import os

# After reading the OTP, delete the file
os.remove("totp_output.txt")
```

On Windows, if you want to bypass the recycle bin entirely:

```python
import os
os.remove("totp_output.txt")  # This permanently deletes, does not go to recycle bin
```

> `os.remove()` in Python already bypasses the recycle bin. But if you're manually deleting the file (not through code), make sure to **Shift+Delete** or empty the recycle bin afterwards.

### .gitignore

The repo includes a `.gitignore` that excludes the OTP output file and any files that might contain secrets.

## Recommendations

- Automation test leads should ensure the secret key is encrypted during processing
- Your framework should handle the OTP retrieval and entry seamlessly within the 30-second window
- If the window is missed, implement a loop to regenerate
- Before deploying, ensure Python and pyotp are installed on the target machine
- Test the integration in a non-production environment first

## License

MIT
