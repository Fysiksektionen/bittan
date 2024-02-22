"""Run this manually to create a token to Google's API, given that credentials.json exists."""
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def main():
	flow = InstalledAppFlow.from_client_secrets_file(
		"credentials.json", SCOPES
	)
	creds = flow.run_local_server(port=0)
	# Save the credentials for the next run
	with open("gmail_token.json", "w") as token:
		token.write(creds.to_json())

if __name__ == "__main__":
	main()
