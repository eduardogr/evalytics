# Evaluation phase

*Input*: <reviewee, listOf(reviewers)>

## Subphases

* Getting assigns for each reviewer
  * This obtain the relation <reviewer, listOf(formOfReviewees)>
* Evals delivery
  * For each reviewer we will send an email information email with its evaluations to complete
* Verify evaluations
  * *Input*: org chart and spreedsheet result files
  * Does everyone has completed its evals? 
  * What happens here: return OK or listOf(reviewers with uncompleted evals)
* Reminder delivery
    * If not OK in *verify evaluation* subphase, reminder emails will be sent to reviewers with uncomplete evaluations