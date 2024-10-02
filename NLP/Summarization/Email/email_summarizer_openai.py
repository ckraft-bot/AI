import config
import datetime  
import email  
import imaplib  
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
    call_to_action_keywords = ["sign", "submit", "fill out", "complete", "send over", "attend", "join", "meeting", "schedule", "appointment", "meeting request"]
    for keyword in call_to_action_keywords:
        if keyword in summary.lower():
            return f"<b>{summary}</b>"
    return summary


# Function to summarize emails
def summarize_emails(email_contents):  
    summaries = []  
    for content, sender in email_contents:  # Adjust here to unpack the tuple  
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
            summaries.append((summary, sender))  # Keep the summary associated with its sender  
        except Exception as e:  
            print(f"Error summarizing email: {e}")  
            summaries.append(("Error summarizing this email.", sender))  # Include sender even in case of error  
    return summaries  

def sort_category(summaries):  
    category_descriptions = {  
        "vendors": "Emails from vendor providers about contract renewals, selling products/services, or relationship management.",  
        "team": "Emails from team members requesting access to certain systems or submitting their paid time off (PTO) requests.",  
        "senior leadership": "Emails from senior leaders about organizational changes, upcoming townhall meetings, or strategic updates.",  
        "admin": "Emails from HR about new hires, reminder to give feedback on quarterly/annual performance reviews, security policy updates, budgeting plans, or financial reports.",  
        "system notification": "Emails about system failures, scheduled maintenance, or software upgrades.",  
        "spam/phishing": "Unsolicited emails trying to sell products or services, or phishing attempts to steal sensitive information.",  
    }  
  
    categories = list(category_descriptions.keys())  
    sorted_summaries = {category: [] for category in categories}  
    sorted_summaries["uncategorized"] = []  # Ensure there's a place for uncategorized summaries  
  
    for summary in summaries:  
        try:  
            response = openai.ChatCompletion.create(  
                engine=config.DEPLOYMENT_NAME,  
                messages=[  
                    {"role": "system", "content": "You are an AI assistant that helps people with text summarization"},  
                    {"role": "user", "content": f"This email falls into this category. The categoris are defined here{category_descriptions}\n{summary}"}  
                ],  
                temperature=0.3,  
                max_tokens=2500,  
                top_p=0.95,  
                frequency_penalty=0,  
                presence_penalty=0,  
                stop=None  
            )  
            # Assuming the model's response is the first line without the dash  
            best_category = response.choices[0].text.strip().split("\n")[0].replace("-", "").strip()  
            if best_category in categories:  
                sorted_summaries[best_category].append(summary)  
            else:  
                sorted_summaries["uncategorized"].append(summary)  
        except Exception as e:  
            print(f"Error classifying summary with OpenAI: {e}")  
            sorted_summaries["uncategorized"].append(summary)  
  
    return sorted_summaries  


# Main code to fetch, summarize, sort, and send the summary via email  
def main():    
    today = datetime.date.today().strftime("%Y-%m-%d")    
    username = email_user  
    password = email_pass   
  
    # Fetch and decode unread emails    
    emails = fetch_and_decode_unread_emails(username, password)    
  
    # Summarize the emails including sender information    
    email_summaries_with_senders = summarize_emails(emails)  # This now includes sender information  
  
    # Extract just the summaries for sorting  
    summaries_only = [summary for summary, _ in email_summaries_with_senders]  
  
    # Sort summaries by category  
    sorted_summaries = sort_category(summaries_only)  
  
    # Compile summaries into a single string to include in the email body, reassociating sender information  
    summary_body = ""  
    for category, summaries in sorted_summaries.items():  
        summary_body += f"<br><br>{category.upper()}:<br>"  
        for summary in summaries:  
            # Find the sender associated with this summary  
            sender = next((sender for summ, sender in email_summaries_with_senders if summ == summary), "Unknown sender")  
            # Apply emphasize_summary to bold summaries with call to action keywords  
            emphasized_summary = emphasize_summary(summary)  
            summary_body += f"From: {sender}<br>{emphasized_summary}<br><br>"  
  
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
