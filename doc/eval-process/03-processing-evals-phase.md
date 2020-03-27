# Processing evals phase


## Subphases

* Generate reviewee eval docs
  * Each reviewee will have its results appended to its eval doc
* Generate team eval docs
  * Each team will have its results appended to its team doc
  * Results here are obtaining from satisfaction questions within self-evaluation forms from team members.
* Send email with results
  * for each manager an email will be sent with a listOf(minion eval docs) and the team eval doc.