# <reward>
reward_val = "0.0"
if (answer.lower() == 'y'):
    reward_val = "1.0"
elif (answer.lower() == 'n'):
    reward_val = "0.0"
else:
    print("Entered choice is invalid. Service assumes that you didn't like the recommended food choice.")

client.events.reward(event_id=eventid, value=reward_val)
# </reward>