
# taken = 0
# drug_freq = get_drug_freq(medication_name)
# last_event = None
# waiting_after_close = True
# for index, event in drug_subset.iterrows():
# 	if event['eventValue'] == "OPEN":
# 		if last_event is None:
# 			if drug_freq == "QD":
# 				return 1.0
# 			taken += 1
# 			last_event = event
# 		else:
# 			if waiting_after_close:
# 				if last_event['eventTime'] + pd.Timedelta('15 minutes') > event['eventTime']:
# 					if drug_freq == "QD":
# 						return 1.0
# 					taken += 1
# 					last_event = event
# 				waiting_after_close = False # either way, 15 min passed or taken event occurred
# 			else:
# 				if last_event['eventTime'] + pd.Timedelta('2 hours, 45 minutes') < event['eventTime']:
# 					return 1.0 # must be second taken event
# 	else:
# 		if last_event is None:
# 			last_event = event
# 			waiting_after_close = True
# 		else:
# 			if waiting_after_close:
# 				if last_event['eventTime'] + pd.Timedelta('15 minutes') > event['eventTime']:
# 					if drug_freq == "QD":
# 						return 1.0
# 					taken += 1
# 					last_event = event
# 			else:
# 				if last_event['eventTime'] + pd.Timedelta('2 hours, 45 minutes') < event['eventTime']:
# 					return 1.0 # must be second taken event
# return 0.5

taken = 0
drug_freq = get_drug_freq(medication_name)
last_event = None
waiting_after_close = True
for index, event in drug_subset.iterrows():
	if last_event is None:
		if event['eventValue'] == "OPEN":
			if drug_freq == 1:
				return 1.0
			taken += 1
			last_event = event
		else:
			last_event = event
			waiting_after_close = True
	else:
		if waiting_after_close:
			if last_event['eventTime'] + pd.Timedelta('15 minutes') > event['eventTime']:
				if drug_freq == "QD":
					return 1.0
				taken += 1
				last_event = event
			waiting_after_close = False # either way, 15 min passed or taken event occurred
		else:
			if last_event['eventTime'] + pd.Timedelta('2 hours, 45 minutes') < event['eventTime']:
				return 1.0 # must be second taken event
return 0.5
