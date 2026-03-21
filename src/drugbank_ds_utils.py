'''
############################ NOTES ############################

SETTING UP BASEX ON LOCAL COMPUTER:

*** Ensure you have Java 17 or higher.***

CLI commands used on Apple Silicon Mac:
- Install BaseX through homebrew -> brew install basex
- Open BaseXGUI -> java -cp /opt/homebrew/Cellar/basex/12.2/libexec/BaseX.jar org.basex.BaseXGUI
- Start BaseX local server -> basexserver

To ensure there is a user in BaseX with 'admin' permissions, run the following QueryX commands in BaseXGUI:

user:create('<name>', '<password>', 'admin') ## pass these credentials when intitating BaseXClient session
user:list-details('<name>') # check that the new user has admin rights
user:check('<name>', '<password>') # verifies that user and password are correct

*** See here for reference: https://old.docs.basex.org/wiki/User_Module#user:current ***

*** Ensure your server is on before running the below. *** 
'''

# Imports

#pip install basexclient # install 

from BaseXClient import BaseXClient



# Queries the DrugBank XML dataset for drugs used for symptoms in a list
def get_drugs(symptom_list:list):
    
    # Connect to BaseX server 
    session = BaseXClient.Session('localhost', 1984, 'admin2', 'admin2')
    
    # Open database (named DrugBank in BaseX)
    session.execute("OPEN DrugBank")

    # Assign "where" line for XQuery
    if not symptom_list:
        print("List is empty!")
        return 
    
    elif len(symptom_list) > 1:
        
        where_line = f'where contains(lower-case($d/indication), "{symptom_list.pop()}") or '
        
        while symptom_list:
            where_line += f'contains(lower-case($d/indication), "{symptom_list.pop()}")' 
    else: 
        where_line = f'where contains(lower-case($d/indication), "{symptom_list.pop()}"'
        
    # XQuery text
    query_text = f"""
    declare default element namespace "http://www.drugbank.ca";
    for $d in //drug
    {where_line} 
    return $d/name/string()
    """
    
    # Execute query
    query = session.query(query_text)
    result = query.execute()
    
    print("Drug List:")
    print(result)
    
    # Cleanup
    query.close()
    session.close()

# Test functionality
test_list = ['headache', 'fever']

get_drugs(test_list)