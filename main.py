import pandas as pd
import requests
import string
import json
import time
import base64
from io import BytesIO
import streamlit as st
startTime = time.time()

# If you use more than 50 seed keywords you should slow down your requests - otherwise google is blocking the script
# If you have thousands of seed keywords use e.g. WAIT_TIME = 1 and MAX_WORKERS = 10

WAIT_TIME = 0.1
MAX_WORKERS = 20

# set the autocomplete language
lang = "en"

charList = string.ascii_lowercase + string.digits

def makeGoogleRequest(query):
    # If you make requests too quickly, you may be blocked by google 
    time.sleep(WAIT_TIME)
    URL="http://suggestqueries.google.com/complete/search"
    PARAMS = {"client":"firefox",
            "hl":lang,
            "q":query}
    headers = {'User-agent':'Mozilla/5.0'}
    response = requests.get(URL, params=PARAMS, headers=headers)
    if response.status_code == 200:
        suggestedSearches = json.loads(response.content.decode('utf-8'))[1]
        return suggestedSearches
    else:
        return "ERR"
def qrlist(k) :
    queryList1 = ['are ' + k + " " + char for char in charList]
    queryList2 = ['what is ' + k + " " + char for char in charList]
    queryList3 = ['is ' + k + " " + char for char in charList]
    queryList4 = ['best ' + k + " " + char for char in charList]
    queryList5 = [k + " vs " + char for char in charList]
    queryList6 = [k + " or " + char for char in charList]
    queryList7 = ['can ' + k + " " + char for char in charList]
    queryList8 = ['which ' + k + " " + char for char in charList]
    queryList9 = ['will ' + k + " " + char for char in charList]
    queryList10 = ['how ' + k + " " + char for char in charList]
    queryList11 = ['what are ' + k + " " + char for char in charList]
    queryList12 = ['do ' + k + " " + char for char in charList]
    queryList13 = [k + " for " + char for char in charList]
    queryList14 = ['best ' + k + " for " + char for char in charList]
    queryList15 = ['difference between ' + k + " and " + char for char in charList]
    queryList16 = ['what are ' + k +' '+ char for char in charList]


    joinedlist = queryList1 + queryList2 + queryList3  + queryList4 + queryList5 + queryList6 + queryList7 +  queryList8 + queryList9 + queryList15 + queryList10+ queryList11+ queryList12+ queryList13+ queryList14+queryList16
    return joinedlist
resultList = []
def getGoogleSuggests(keyword):
    # err_count1 = 0
    queryList = qrlist(keyword)
    my_bar = st.progress(0)
    percent_complete=0
    for query in queryList:
        if 'are '  in query :
            qquery = 'are ' 
        elif 'what '  in query :
            qquery = 'what ' 
        elif 'is '  in query :
            qquery = 'is ' 
        elif 'best'  in query :
            qquery = 'best' 
        elif ' vs '  in query :
            qquery = ' vs ' 
        elif ' or '  in query :
            qquery = ' or ' 
        elif 'can '  in query :
            qquery = 'can ' 
        elif 'which '  in query :
            qquery = 'which ' 
        elif 'will '  in query :
            qquery = 'will ' 
        elif 'how '  in query :
            qquery = 'how ' 
        elif 'do '  in query :
            qquery = 'do ' 
        elif 'for '  in query :
            qquery = 'for ' 
        elif 'best ' in query :
            qquery = 'best '
        elif 'difference ' in query :
            qquery = 'difference '
        

        percent_complete =percent_complete + 1
        my_bar.progress(percent_complete/len(queryList))
        suggestion = makeGoogleRequest(query)
        if suggestion != 'ERR':
            for s in suggestion: 
                if qquery in s:
                    if  (" for ") in s:
                        type = "use case"
                    elif s.startswith ("are "):
                        type = "attribute"
                    elif s.startswith ("is "):
                        type = "attribute"
                    elif s.startswith ("can "):
                        type = "attribute"
                    elif s.startswith ("best "):
                        type = "subtopic"
                    elif  " vs " in s:
                        type = "ontology"
                    elif " or " in s:
                        type = "ontology"
                    elif s.startswith ("how to"):
                        type = "how to guide"
                    elif s.startswith ("do "):
                        type = "attribute"
                    elif s.startswith ("difference between "):
                        type = "ontology"
                    else :
                        type = 'other'
                    resultList.append({
                        'keyword' : keyword ,
                        'type' : type ,
                        'query': query,
                        'suggestion' : s
                        })
                else :
                    pass


keywords = st.text_input('Add the comma separated Keywords and press the button (maximum of 3)')

if st.button('Start Process The Keyword'):
    tt = keywords.split(',')
    for t in tt[:3] :
        getGoogleSuggests(t)


def to_excel(df):
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1')
    writer.save()
    processed_data = output.getvalue()
    return processed_data

def get_table_download_link(df,name):
    """Generates a link allowing the data in a given panda dataframe to be downloaded
    in:  dataframe
    out: href string
    """
    val = to_excel(df)
    b64 = base64.b64encode(val)  # val looks like b'...'
    return f'<a href="data:application/octet-stream;base64,{b64.decode()}" download="{name}.xlsx">Download Excel file</a>' # decode b'abc' => abc



outputDf = pd.DataFrame(resultList)


st.dataframe(outputDf)
st.markdown(get_table_download_link(outputDf,'Google_ac'), unsafe_allow_html=True)


st.text(f"Execution time: { ( time.time() - startTime ) :.2f} sec")
