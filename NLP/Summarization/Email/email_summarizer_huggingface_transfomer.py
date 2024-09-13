import config
import datetime  
import email  
import imaplib  
import smtplib  
import ssl  
from transformers import pipeline
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
        return "Unable to reach inbox"  
      
    # The response will contain a list of unread email IDs, if any  
    unread_email_ids = response[0].split()  
      
    mail.logout() 
      
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
  
    emails = []  
    for num in response[0].split():  
        status, data = mail.fetch(num, '(RFC822)')  
        if status != 'OK':  
            continue  
  
        raw_email = data[0][1]  
        msg = email.message_from_bytes(raw_email)  
        sender = msg['From']  
          
        if msg.is_multipart():  
            for part in msg.walk():  
                content_type = part.get_content_type()  
                content_disposition = str(part.get("Content-Disposition"))  
                if content_type == "text/plain" and "attachment" not in content_disposition:  
                    charset = part.get_content_charset()  
                    email_text = part.get_payload(decode=True).decode(encoding=charset, errors="ignore")  
                    emails.append((email_text, sender))  
        else:  
            content_type = msg.get_content_type()  
            if content_type == "text/plain":  
                charset = msg.get_content_charset()  
                email_text = msg.get_payload(decode=True).decode(encoding=charset, errors="ignore")  
                emails.append((email_text, sender))  
  
    mail.logout()  
    return emails  


# Function to detect emails that require action
def emphasize_summary(summary):
    call_to_action_keywords = ["sign", "submit", "fill out", "complete", "send over", "attend", "join", "meeting", "schedule", "appointment"]
    for keyword in call_to_action_keywords:
        if keyword in summary.lower():
            return f"<b>{summary}</b>"
    return summary

# Function to summarize emails
def summarize_emails(emails):
    summarizer = pipeline("summarization", model="t5-base") 
    summaries = []
    for content, sender in emails:
        try:
            summary = summarizer(content, max_length=400, min_length=100, do_sample=False)[0]['summary_text']
            emphasized_summary = emphasize_summary(summary)
            summaries.append(f"From: {sender}<br>Summary: {emphasized_summary}")
        except Exception as e:
            print(f"Error summarizing email from {sender}: {e}")
            summaries.append(f"From: {sender}<br>Summary: Error summarizing this email.")
    return summaries

# Function to sort summaries by category
def sort_category(summaries):
    classifier = pipeline("zero-shot-classification")
    """
    Vendors: Emails from vendor providers about contract renewals, selling products/services, or relationship management.
    Team: Emails from team members requesting access to certain systems or submitting their paid time off (PTO) requests.
    Senior Leadership: Emails from senior leaders about organizational changes, upcoming townhall meetings, or strategic updates.
    Admin: Emails from HR about new hires, reminder to give feedback on quarterly/annual performance reviews, security policy updates, budgeting plans, or financial reports.
    System Notifications: Emails about system failures, scheduled maintenance, or software upgrades.
    Spam/Phishing: Unsolicited emails trying to sell products or services, or phishing attempts to steal sensitive information.
    """
    categories = ["vendors", "team", "senior leadership", "admin", "system notification", "spam/phishing"] 
    sorted_summaries = {category: [] for category in categories}
    
    for summary in summaries:
        try:
            result = classifier(summary, candidate_labels=categories)
            best_category = result['labels'][0]
            sorted_summaries[best_category].append(summary)
        except Exception as e:
            print(f"Error classifying summary: {e}")
            sorted_summaries["uncategorized"].append(summary)
    
    return sorted_summaries

# Main code to fetch, summarize, sort, and send the summary via email  
def main():  
    today = datetime.date.today().strftime("%Y-%m-%d")  
    username = email_user
    password = email_pass 
  
    # Fetch and decode unread emails  
    emails = fetch_and_decode_unread_emails(username, password)  
      
    # Summarize the emails  
    summaries = summarize_emails(emails)  
    
    # Sort summaries by category
    sorted_summaries = sort_category(summaries)
    
    # Compile summaries into a single string to include in the email body  
    summary_body = ""
    for category, summaries in sorted_summaries.items():
        summary_body += f"<br><br>{category.upper()}:<br>" + "<br><br>".join(summaries)
      
    # Construct and send the email with the summary  
    message = MIMEMultipart()  
    message["From"] = username  
    message["To"] = username  
    message["Date"] = formatdate(localtime=True)  
    message["Subject"] = f"Daily Summarizer for {today}"  
    message.attach(MIMEText(summary_body, 'html'))  
    text = message.as_string()  
  
    # Log in to server using secure context and send email  
    context = ssl.create_default_context()  
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:  
        server.login(username, password)  
        server.sendmail(username, username, text)  
  
if __name__ == "__main__":  
    main()