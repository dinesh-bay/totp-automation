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

### Example: Tosca Integration

Here's how you can set this up in Tosca:

1. **Store the secret key as an encrypted Configuration Parameter (CP) in Tosca**
   - Create a CP like `{CP[TOTP_SecretKey]}` and encrypt the value
   - This ensures the key is never stored in plain text

2. **Run the Python script using TBox Start Program**
   - Module: `TBox Start Program` (found under TBox Automation Tools → Process Operations)
   - Path: `python` (or full path like `C:\Python3x\python.exe`)
   - Arguments: `C:\path\to\totp_generator.py`

3. **Read the OTP from the output file using TBox Read/Create File**
   - Module: `TBox Read/Create File` (found under TBox Automation Tools → File Operations)
   - Directory: path where `totp_output.txt` is saved
   - FileName: `totp_output.txt`
   - Text: set ActionMode to **Buffer** → `{B[OTP_Value]}`

4. **Enter the OTP in the authentication window**
   - Use the buffered value `{B[OTP_Value]}` in your Input action on the OTP field

5. **Delete the output file using TBox Delete File**
   - Module: `TBox Delete File` (found under TBox Automation Tools → File Operations)
   - Directory: path where `totp_output.txt` is saved
   - FileName: `totp_output.txt`

6. **Wrap steps 2-5 in a Reusable Test Step Block** so your team can use it anywhere without duplicating the setup

The flow in Tosca looks like:

```
[TBox Start Program → python] → [TBox Read/Create File → Buffer OTP] → [Enter OTP] → [TBox Delete File]
```

All of this happens in seconds — well within the 30-second TOTP window.

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

After your automation reads the OTP, **delete the output file immediately.** Don't just delete it normally — that sends it to the recycle bin where it can still be recovered.

**Option 1: Delete via Python (recommended — bypasses recycle bin)**

```python
import os
os.remove("totp_output.txt")  # Permanently deleted, does NOT go to recycle bin
```

**Option 2: Delete via command line (bypasses recycle bin)**

```bash
# Windows
del /f totp_output.txt

# Linux/Mac
rm -f totp_output.txt
```

**Option 3: Delete via Tosca (TBox Execute Program)**

- Program: `cmd`
- Arguments: `/c del /f "C:\path\to\totp_output.txt"`

**Option 4: Manual deletion**

If you ever delete the file manually (right-click → delete), it goes to the **recycle bin**. Make sure to:
1. Open Recycle Bin
2. Find and delete `totp_output.txt` from there, OR
3. Right-click Recycle Bin → Empty Recycle Bin

Better yet — use **Shift+Delete** to permanently delete without going to recycle bin.

**Why this matters:** The OTP file contains a valid token. While it expires in 30 seconds, leaving multiple OTP files around is a security risk. Make cleanup part of your automation flow, not an afterthought.

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
