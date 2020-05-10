# email-light-thing
Checks my email's annoyance-level based on a set of keywords and adjusts a Hue lamp accordingly.

This Python script uses the Google API to check my gmail inbox and evaluate the number of messages within it likely to annoy me.

Annoyance level is based on:

- Is the email sent just to me?

- Is the email from a student email address?

- Does the email contain more than three keywords from a list that includes things like "grade", "late", "unfair",...

It's possible I had a little too much time on my hands during the pandemic apocalypse...
