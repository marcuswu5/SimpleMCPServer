import emailcache
from email import message
import os.path
import base64
import time

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

def decode_body(payload):
   if 'parts' in payload:
      for part in payload['parts']:
        if part['mimeType'] in ['text/plain', 'text/html']:
            data = part['body'].get('data')
            if data:
                return base64.urlsafe_b64decode(data).decode('utf-8')
        else:
            # Recurse if nested parts exist
            content = decode_body(part)
            if content:
                return content
   else:
      data = payload['body'].get('data')
      if data:
          return base64.urlsafe_b64decode(data).decode('utf-8')
   return None

def main():
  try:
    last_refreshed = emailcache.get_last_refreshed()
  except:
    last_refreshed = -1
  if last_refreshed != -1 and last_refreshed > int(time.time()) - 86400:
      emails = emailcache.get_all_emails()
      for email in emails:
        print(f"Sender: {email[1]}\nSubject: {email[2]}\nBody: {email[3]}\n")
      return
  else:
    get_new_emails()

def get_new_emails():
  """Shows basic usage of the Gmail API.
  Lists the user's Gmail labels.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          "C:\\Users\\wumar\\Desktop\\Personal Codes\\SimpleMCPServer\\credentials.json", SCOPES
      )
      creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    # Call the Gmail API
    service = build("gmail", "v1", credentials=creds)
    results = service.users().messages().list(userId="me", includeSpamTrash=False, labelIds=["INBOX"], q="is:unread AND newer_than:1d").execute()
    messages = results.get("messages", [])

    if not messages:
        print("No messages found.")
        return

    print("Messages:")
    emails = []
    for message in messages:
        msg = service.users().messages().get(userId="me", id=message["id"]).execute()
        for header in msg["payload"]["headers"]:
            if header["name"] == "From":
                sender = header["value"]
            if header["name"] == "Subject":
                subject = header["value"]        
    
        email = (msg["id"], sender, subject, decode_body(msg["payload"]), msg["internalDate"])
        emails.append(email)    

    emailcache.add_to_cache(emails)    
    emailcache.prune_cache()
  except HttpError as error:
    # TODO(developer) - Handle errors from gmail API.
    print(f"An error occurred: {error}")


if __name__ == "__main__":
  main()