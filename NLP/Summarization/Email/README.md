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
![image](https://github.com/user-attachments/assets/e8085ab7-6cd5-4735-9a88-cb04339ea267)

Summarized email sent to my inbox
![image](https://github.com/user-attachments/assets/88d8ce0b-132e-4655-8865-da723f52d3ba)
