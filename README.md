# Snackbot
Snackbot is a Slackbot used on the Stanford Student Space Initiative's Slack workspace to incentivize workspace cleaning. Members of the club can earn snack credits which are used to unlock a shelf of snacks. Free credits are given quarterly to nourish busy engineers, and additional credits are earned by spending a few minutes cleaning part of the lab, and then sending the Snackbot a photo of what was cleaned. 

# Use
This bot is hosted locally on a Raspberry Pi attached to the snack cabinet. It uses Slack's API to respond to events, including the `/snack` command, where users use credits, and messages to the Slack bot. Data is stored on a local SQLite database. 

# Hardware Implementation
The Raspberry Pi controls MOSFETs through the GPIO pins, which switches a 12v power supply and retracts a solenoid.

# Further Reading
[SSI Internal Documentation](https://ssi-wiki.stanford.edu/Snack_Bot)

[Learn more about SSI](https://www.stanfordssi.org)
