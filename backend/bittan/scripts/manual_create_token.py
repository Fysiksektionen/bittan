"""Run this manually to create a token to Google's API, given that gmail_secret.json exists.
May not work in a Docker container; run on your local machine and then upload the generated gmail_token.json"""
from google_auth_oauthlib.flow import InstalledAppFlow

def main():

	SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

	flow = InstalledAppFlow.from_client_secrets_file(
		"../gmail_secret.json", SCOPES
	)
	creds = flow.run_local_server(port=0)
	with open("../gmail_token.json", "w") as f:
		f.write(creds.to_json())

if __name__ == "__main__":
	main()
