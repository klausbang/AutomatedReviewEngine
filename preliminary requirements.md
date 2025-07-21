The project is called "Automated Review Engine" (ARE).
The program is written in python.

Frontend: Streamlit UI

The purpose of ARE is to automate document reviews of regulatory documents, like EU Declaration of Conformity for a medical device.

The users are regulatory affairs specialists working for a medical device company.

The automated review engine has the following inputs:

1) Document under review (PDF, MS Word)

2) Form/template for the document where the expected and required structure and content of the document under review can be found (MS Word).

3) Review script with directions for what the engine shall check in the document.

4) Product data from the PLM system. Will be provided manually by pasting tabular data into the GUI or by reference to a CSV file containing the data.
More input files/tables of this type may be needed for the review.

5) Other input files may occur.

The automated review engine has the following outputs:
1) PLM search directions for use to look up and extract the data from the PLM system (human readable structured format). Contains:
a) a search mode, e.g. document search, product search, item search.
b) Search field name, for guiding the user to where the search string shall be pasted in.
c) search string

2) Review report. The main outcome of the Automated Review Engine, documenting the review and the results of the review.

