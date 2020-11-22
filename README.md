# Increasing Patient Medication Adherence By Custom AI Generated Text Message
### Author(s): Lily Bessette, lgbessette@bwh.harvard.edu
### Conceptualized by: Julie Lauffenburger and Niteesh Choudhry
### Contributor(s): Joe Buckley, jjbuckley@bwh.harvard.edu
### Updated 2020-11-21

## Project Requirements

Python version 3.7.x. Development using `venv`, see [documentation](https://docs.python.org/3/library/venv.html).
See `requirements.txt` for external dependencies.


## Directory Structure:

The parent directory of this code repository should contain 3 folders containing data to be read in:

`PatientData` 
- contains all patient data used in prediction modeling and patient history (baseline demographics, observed feedback, other attributes for the program to continually update)
- exists as pickle of data for each day following full completion of reward calls to Personalizer (to update resulting adherence from yesterday) and rank calls to Personalizer (to find SMS message to send today) 
- named "YYYY-MM-DD_pillsy" with date prepended in format as indicated
- date used is of when data is generated by program (i.e. today is exported at program completion, yesterday is loaded in for program)

`Pillsy` 
- contains open/close event data from patient electronic pill bottle
- exists as csv of data for each day
- named "YYYY-MM-DD_pillsy" with date prepended in format as indicated
- date used is of when data is generated by pill bottle users (i.e. yesterday)

`REDCap`
- contains demographic patient data
- exists as csv of data exported daily from REDCap
- named "YYYY-MM-DD_redcap" with date prepended in format as indicated
- date used is of when data is to be updated in patient dictionary (i.e. today)

`SMSChoices`
- contains one file sms_choices.csv
- this is the link between the numeric codes associated with text messages to be sent and the texts themselves


The parent directory should also have these folder for the program to export to:

`SMSHistory` 
- contains all SMS messaging history generated from the decisions of the rank calls to Personalizer
`For a particular SMSHistory file:`
    - exists as csv of data for each day
    - named "YYYY-MM-DD_sms_history" with date prepended in format as indicated
    - date used is of when data is to generated from patient dictionary (i.e. today)

`RewardData` 
- contains all reward_updates generated from the computation of adherence between rank calls from the Pillsy data 
- these reward_updates are the reward calls that we make to Personalizer to indicate how well it predicted an appropriate SMS message based on a patient's medication adherence from the last run to midnight 
`For a particular RewardData file:`
    - exists as csv of data for each day
    - named "YYYY-MM-DD_reward_updates" with date prepended in format as indicated
    - date used is of when reward data is generated from computation from Pillsy data and patient dictionary and sent to Personalizer (i.e. today)
