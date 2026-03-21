# DATA606
Data Science Capstone

##### Triage Functionality

> - Dataset (in RData) was collected by Yale School of Medicine and was publically available from research conducted by Hong, Haimovich, and Taylor (2018).  Can be found at this link:
> - 220/972 attributes were taken out of dataset but still contains (n=560,486) records.


### Directories:

#### src
> - drugbank_ds_utils.py
>     - Queries DrugBank (academic version) database in XBase for medications that treat provided symptoms.
>     - Must load XML file into XBase and run local server to run script.
> - triage_dataset_extract.R
>     - Filters out selected 219/972 attributes from Yale School of Medicine dataset (named "Yale_Dataset.RData").
