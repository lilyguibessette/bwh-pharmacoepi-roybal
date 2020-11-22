# Increasing Patient Medication Adherence By Custom Text AI Generated Text Message
### Author(s): Lily Bessette, lgbessette@bwh.harvard.edu
### Contributor(s): Joe Buckley, jjbuckley@bwh.harvard.edu
### Updated 2020-11-21

## Project Requirements

Python version 3.7.x. Development using `venv`, see [documentation](https://docs.python.org/3/library/venv.html).
See `requirements.txt` for external dependencies.


## Directory Structure:

The parent directory of this code repository should contain 3 folders containing data:

`Pillsy` 
- contains open/close event data from patient pill bottle
- exists as csv of data for each day
- named "YYYY-MM-DD_Pillsy" with date prepended in format as indicated

`REDCap`
- contains demographic patient data
- exists as csv of data exported daily from REDCap
- named "YYYY-MM-DD_REDCap" with date prepended in format as indicated

`SMSChoices`
- contains one file sms_choices.csv
- this is the link between the numeric codes associated with text messages to be sent and the texts themselves
