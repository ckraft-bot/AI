## Use case: 
Email summarization is a streamlined process designed to manage your inbox more effectively by leveraging the capabilities of AI, particularly OpenAI's GPT model. This innovative approach aims to condense the content of unread emails, providing you with a concise summary of each, thus saving time and enhancing productivity.
Audience: C level suite managers

## Steps:
- Config an app password with Google: How to create app passwords
- Use IMAP to reach my email inbox
- Verify that the api got through by counting the unread emails
- Parse unread emails from byes into raw utf8
- Pass in the raw unread emails into OpenAI prompt
- Ask chat gpt to summarize the emails 
- Use SMTP to send the summary from myself to myself

Count unread emails
![image](https://github.com/user-attachments/assets/24aef777-d77a-4567-b1e6-4b7d027a1b00)

Unread emails
![unread email 9_12](https://github.com/user-attachments/assets/a6de89a4-fa95-4529-8dcf-94842967931a)



Summarized email sent to my inbox
![sumarized email 9_12](https://github.com/user-attachments/assets/b0fbc2ab-0ece-49f0-bea1-399d22cf0af2)
