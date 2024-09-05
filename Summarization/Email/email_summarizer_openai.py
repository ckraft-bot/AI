import config
import datetime  
import email  
import imaplib  
import openai  
import smtplib  
import ssl  
from email.mime.multipart import MIMEMultipart  
from email.mime.text import MIMEText  
from email.utils import formatdate  


email_user = config.GMAIL_USER 
email_pass = config.GMAIL_PASS 

# Function to count unread emails 
def count_unread_emails(email_user, email_pass):  
    # Connect to the email server  
    mail = imaplib.IMAP4_SSL('imap.gmail.com')  
    mail.login(email_user, email_pass)  
    mail.select('inbox')  
      
    # Search for unread emails  
    status, response = mail.search(None, '(UNSEEN)')  
    if status != 'OK':  
        return "There are 0 unread emails."  # If the status is not OK, return a message indicating 0 unread emails  
      
    # The response will contain a list of unread email IDs, if any  
    unread_email_ids = response[0].split()  
      
    mail.logout()  # Logout from the email server  
      
    # Return a formatted string indicating the count of unread emails  
    return "There are {} unread emails.".format(len(unread_email_ids))  

print(count_unread_emails(email_user, email_pass))  


# Function to fetch and decode unread emails  
def fetch_and_decode_unread_emails(email_user, email_pass):  
    # Connect to the email server  
    mail = imaplib.IMAP4_SSL('imap.gmail.com')  
    mail.login(email_user, email_pass)  
    mail.select('inbox')  
      
    # Search for unread emails  
    status, response = mail.search(None, '(UNSEEN)')  
    if status != 'OK':  
        return []  
  
    email_contents = []  
    for num in response[0].split():  
        status, data = mail.fetch(num, '(RFC822)')  
        if status != 'OK':  
            continue  
  
        raw_email = data[0][1]  
        msg = email.message_from_bytes(raw_email)  
          
        if msg.is_multipart():  
            for part in msg.walk():  
                content_type = part.get_content_type()  
                content_disposition = str(part.get("Content-Disposition"))  
                if content_type == "text/plain" and "attachment" not in content_disposition:  
                    charset = part.get_content_charset()  
                    email_text = part.get_payload(decode=True).decode(encoding=charset, errors="ignore")  
                    email_contents.append(email_text)  
        else:  
            content_type = msg.get_content_type()  
            if content_type == "text/plain":  
                charset = msg.get_content_charset()  
                email_text = msg.get_payload(decode=True).decode(encoding=charset, errors="ignore")  
                email_contents.append(email_text)  
  
    mail.logout()  
    return email_contents  
  
# Function to summarize emails  
def summarize_emails(email_contents):  
    summaries = []  
    for content in email_contents:  
        try:  
            response = openai.ChatCompletion.create(  
                engine=config.DEPLOYMENT_NAME,  
                messages=[  
                    {"role": "system", "content": "You are an AI assistant that helps people with text summarization"},  
                    {"role": "user", "content": f"summarize this text\n{content}"}  
                ],  
                temperature=0.7,  
                max_tokens=1500,  
                top_p=0.95,  
                frequency_penalty=0,  
                presence_penalty=0,  
                stop=None  
            )  
            summary = response.choices[0].message.content  
            summaries.append(summary)  
        except Exception as e:  
            print(f"Error summarizing email: {e}")  
            summaries.append("Error summarizing this email.")  
    return summaries  
  
# Main code to fetch, summarize, and send the summary via email  
def main():  
    today = datetime.date.today().strftime("%Y-%m-%d")  
    username = email_user
    password = email_pass 
  
    # Fetch and decode unread emails  
    email_contents = fetch_and_decode_unread_emails(username, password)  
      
    # Summarize the emails  
    summaries = summarize_emails(email_contents)  
      
    # Compile summaries into a single string to include in the email body  
    summary_body = "\n\n".join(summaries)  
      
    # Construct and send the email with the summary  
    message = MIMEMultipart()  
    message["From"] = username  
    message["To"] = username  
    message["Date"] = formatdate(localtime=True)  
    message["Subject"] = f"Daily Summarizer for {today}"  
    message.attach(MIMEText(summary_body, 'plain'))  
    text = message.as_string()  
  
    # Log in to server using secure context and send email  
    context = ssl.create_default_context()  
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:  
        server.login(username, password)  
        server.sendmail(username, username, text)  
  
if __name__ == "__main__":  
    main()  
