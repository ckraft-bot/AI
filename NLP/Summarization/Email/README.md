## Use case: 
Email summarization is a streamlined process designed to manage your inbox more effectively by leveraging the capabilities of AI, particularly OpenAI's GPT model. This innovative approach aims to condense the content of unread emails, providing you with a concise summary of each, thus saving time and enhancing productivity.
Audience: C level suite managers

## Steps:
- Config an app password with Google: How to create app passwords
- Use IMAP to reach my email inbox
- Verify that the api got through by counting the unread emails
- Parse unread emails from byes into raw utf8
- Pass in the raw unread emails into LLM propmpt of your choice
    - Flag the call to action emails by bolding those details in the summary
    - Sort summaries into categories
    - Ask the LLM of your choice to summarize the emails into short paragrphs or sentences
- Use SMTP to send the summary from myself to myself

Count unread emails
![image](https://github.com/user-attachments/assets/24aef777-d77a-4567-b1e6-4b7d027a1b00)

Unread emails
![unread email 9_12](https://github.com/user-attachments/assets/22e93c23-2299-4561-9971-ceab637265d2)


Summarized email sent to my inbox
![image](https://github.com/user-attachments/assets/1ffcbb32-f945-46cd-8fc1-68523f8fe586)

