import requests #we will use requests to get the data from SurveyMonkey
import pandas as pd #output will be returned as a pandas dataframe
class Survey_Monkey(object): #define Survey_Monkey class

    def __init__(self, api_key,  host = "https://api.surveymonkey.net"): #define what happens when we define an instance of class Survey_Monkey
        self.api_key = api_key
        self.host = host #set the host argument equal to the host variable for the class instance
    def _api_get(self, endpoint): #Private Method that returns the data from SurveyMonkey API in JSON format
        client = requests.session() 
        headers = {
            "Authorization": "bearer %s" % self.api_key,
            "Content-Type": "application/json"
        }
        
        uri = "%s%s" % (self.host, endpoint) #the endpoint defines what data we are getting from survey monkey, see _endpoint creator for more info

        response = client.get(uri, headers=headers)

        return response.json()
    def _endpoint_creator(self, surveyid, data_pull): #private method to create an endpoint. 
        return "/v3/surveys/" + surveyid + "/" + data_pull #The surveyid is the survey we want and data_pull is the type of data we want to retreive
    def get_survey_list(self, output = "df"): #define a method to return an object that displays all the surveys(with there ids) in the account
        survey_list = self._api_get("/v3/surveys") #tell the _api_get to retrieve general info for all surveys in the account
        
        if output == "df": #if we want the method to return a DataFrame
            ids = []
            titles = []
            for survey in survey_list["data"]: #pull out the data from the survey_list, and iterate over it 
                ids.append(survey["id"]) #for every iteration pull out the id and append it to ids list
                titles.append(survey["title"]) #for every iteration pull out the survey title and append it to titles list
            return(pd.DataFrame({"Survey_ID": ids, "Survey_Title": titles})) #create a pandas dataframe using the ids and titles list and return it 
        elif output == "list": #if we want the method to return a Dataframe
            survey_lst = [] 
            for survey in survey_list["data"]: #pull out the data from the survey_list, and iterate over it
                survey_lst.append([survey["id"], survey["title"]]) #pull out the id and title, put it in a mini-list and append it to survey_lst list
            return(survey_lst) #return the survey_lst
        elif output == "dict": #if we want the output to be a dictionary
            survey_dict = {}
            for survey in survey_list["data"]: #pull out the data from the survey_list, and iterate over it
                survey_dict[survey["title"]] = survey["id"] #for every survey, make the title a key in the list with value equal to the survey id
            return(survey_dict) #return the dictionary
        else: #if the user didn't specify they wanted a DataFrame, List, or Dictionary
            raise ValueError('Unkown Output type, must be "df", "list", or "dict"') #return an error
    def get_survey_codebook(self, surveyid): #define a method to create a Code Book for a survey
        details = self._api_get(self._endpoint_creator(str(surveyid), "details")) #tell the API to get the "Details" for the survey 
        
        code_book = {}
        for page in details["pages"]: #iterate over every page in the survey
            for question in page["questions"]: #iterate over every question on the page
                if question["family"] =='open_ended': #if is an open ended question
                    if "answers" in question: #this is a way of saying "if it is a multi-row open-ended question"
                        for ques in question["answers"]["rows"]: #iterate over every row
                            heading = ques["text"] #we will treat each row as its own question, with its text as the question text
                            ques_id = ques["id"] #retrieve the question id
                            answers = "None" #make the answers None, becuase its open-ended there are no answer keys 
                            code_book[ques_id] = {"heading": heading, "answers": answers} #create a new element in the codebook, with the key being the question id
                                                                                          #the value of the elemtn willl be a dictionary,
                                                                                           #with key heading set to the question text, and key answers equal to the answers
                    else: #if it is a single row open ended question                                                               
                        heading = question["headings"][0]["heading"] #grab the question text, and question id and put it in the code_book dictionary
                        ques_id = question["id"]
                        answers = "None" #again answers are None 
                        code_book[ques_id] = {"heading": heading, "answers": answers}
                elif question["family"] == "datetime": #if it is a question which asks the users to input the date
                    if len(question["answers"]["rows"]) > 1: #if the answers have more than one rows
                        for ques in question["answers"]["rows"]: #treat each row as a question and interate over it
                            heading = ques["text"]
                            ques_id = ques["id"]
                            answers = "None" #again answers are None
                            code_book[ques_id] = {"heading": heading, "answers": answers} #add the question id, and question heading to the codebook
                    else: #if the answers only have one rpw
                        heading = question["headings"][0]["heading"] #treat the overall question heading(not the row heading) as the question text
                        ques_id = question["answers"]["rows"][0]["id"]
                        answers = "None" #again answers are None
                        code_book[ques_id] = {"heading": heading, "answers": answers} #add the question id, and question heading to the codebook
                else: #if its not a date or open-ended question(so its a multiple-choice)
                    #NOTE: This is where functionality needs to be built in for other question types!!!
                    if "rows" in question["answers"]: #if the question has rows(meaning its a matrix and really more than one question)
                        if question["subtype"] == "menu": #if its a matrix of dropdown menus(meaning every row/column cell is its own question
                            for ques in question["answers"]["rows"]: #iterate over every row
                                for subques in question["answers"]["cols"]: #iterate over every column in that row
                                    ques_id = str(ques["id"]) + str(subques["id"])  #combine the row id and column id to make the cell id
                                    heading = ques["text"] + "-" + subques["text"] #combine the row text with the column text to make the question text
                                    answers = {}
                                    for answer in subques["choices"]: #iterate over the answer choices
                                        ans_id = answer["id"]
                                        ans_text = answer["text"]
                                        answers[ans_id] = ans_text #for each answer, save it as an element in dictionary answers with the key being the id
                                    code_book[ques_id] = {"heading": heading, "answers":answers} #add the question to the code_book dictionary, this time including the answers
                        else: #if its not a matrix of drop-down menu's(so every row(but not every coumn) is its own question
                            answers = {}
                            for answer in question["answers"]["choices"]: #first pull out all the answer choices and store it in a dictionary
                                ans_id = answer["id"]
                                ans_text = answer["text"]
                                answers[ans_id] = ans_text
                            for ques in question["answers"]["rows"]: #for every row, pull out the id and text and then make a new elenent in the code book 
                                ques_id = ques["id"]
                                heading = ques["text"]
                                code_book[ques_id] = {"heading": heading, "answers": answers}
                    else: #if the question doesn't have rows(so it is truly one question)
                        heading = question["headings"][0]["heading"] #take out the question text and id
                        ques_id = question["id"]
                        answers = {}
                        for answer in question["answers"]["choices"]: #iterate over all answer choices and pair them by id 
                            ans_id = answer["id"]
                            ans_text = answer["text"]
                            answers[ans_id] = ans_text
                        if "other" in question["answers"].keys(): #if the question has an other(Where you then specify in a textbox)
                            ans_id = question["answers"]["other"]["id"] 
                            ans_text = question["answers"]["other"]["text"]
                            answers[ans_id] = ans_text #also pull the other answer out and put it in the dictionary
                        code_book[ques_id] = {"heading": heading, "answers": answers} #add the question to the code boook
        return code_book #have the method return the code_book
    def get_survey_data(self, survey_id, keep_data = ["id", "ip_address", "collector_id"], code_book = None):
        if code_book is None: #If the user did not input a code book
            code_book = self.get_survey_codebook(survey_id) #call the codebook method to create one
        if type(keep_data) is not list: #checking if the keep_data argument was inputed corecctly 
            raise TypeError("keep_data must be a list") 
        elif len(keep_data) == 0:
            raise ValueError("keep_data must have at least one element")
        survey_resposes = self._api_get(self._endpoint_creator(str(survey_id), "responses/bulk"))#get the survey responses for the survey id as JSON
        
        data_lst = [] #we are going to convert this disgusting JSON to a list, where every element is a respondent. Each element will have a dict of answers
        for respondent in survey_resposes["data"]: #iterate over every respondent in the survey
            res_data = {}
            for variable in keep_data: #for the keep_data variables, the data is in the this first dictionary so take it out now 
                res_data[variable] = respondent[variable]
            for page in respondent["pages"]: #iterate over every page of the survey
                for question in page["questions"]: #iterate over every question on the page 
                    if "row_id" in question["answers"][0]: #if the question has rows
                        if "col_id" in question["answers"][0]: #if the question has columns
                            for ques in question["answers"]: #iterate over ever row/column pair, combine the ids, and add that to res_data 
                                ques_id = str(ques["row_id"]) + str(ques["col_id"])
                                res_data[ques_id] = [ques["choice_id"]]
                        else: #if the data has rows but no columns
                            for ques in question["answers"]: #loop over every row 
                                ques_id = ques["row_id"]
                                if ques_id in res_data.keys(): #the same row may appear twice if you can give 2 answers for the same row
                                    ans_id = res_data[ques_id] #Thus start the list with the first answer so we can append the second 
                                else:
                                    ans_id = []
                                if "text" in ques: #if it is a text box or date question
                                    ans_id.append(ques["text"]) #take the text(there is not id)
                                else: #if it is multiple choice
                                    ans_id.append(ques["choice_id"]) #take the id(ap
                                res_data[ques_id] = ans_id 
                    else: #if the question has no rows
                        ques_id = question['id']
                        ans_ids = []
                        for answer in question["answers"]: #iterate over every answer
                            if "other_id" in answer:
                                #if it is an "other please specify" we need id and text
                                #also add a unique text string to indentify it
                                ans_ids.append(answer["other_id"] + "qwertyuiopoop:" + answer["text"]) 
                            elif "text" in answer:
                                ans_ids.append(answer["text"]) #if its a text, we just need text
                            else:
                                ans_ids.append(answer["choice_id"]) #else grab the id
                        res_data[ques_id] = ans_ids
            data_lst.append(res_data)
            
        clean_lst = [] #Now we are going to convert the ID's we have in the list to actual text questions/answers using the codebook
        for respondent in data_lst: #iterate over every respondent
            res_data = {}
            for question_id in list(respondent.keys()): #iterate over every question
                if question_id in keep_data: #if the question is in keep_data, then nothing has to be done(we didn't use ID's for those)
                    res_data[question_id] = respondent.get(question_id)
                else:
                    heading = code_book.get(question_id)["heading"] #use the question id to search the codebook for the heading
                    ans_ids = respondent.get(question_id) #get the answers that the respondent gave for that question
                    if code_book.get(question_id)["answers"] == "None": #if the code_book has no answers for this question, do nothing, we already have ans
                        res_data[heading] = ' '.join(ans_ids)
                    else: 
                        answers = []
                        for ans in ans_ids: #iterate over every answer
                            if "qwertyuiopoop:" in ans: #if it has a : that means its an other
                                other = ans.replace("qwertyuiopoop", "").split(":", 1) #get rid of the uniue key and split with the first :
                                other_txt = code_book.get(question_id)["answers"].get(other[0])
                                answers.append(other_txt + "(" + other[1] + ")")
                            else:
                                answers.append(code_book.get(question_id)["answers"].get(ans))#if the answer isn't an other, find the text in the codebook
                        the_answer = ', '.join(str(e) for e in answers) #right now every answer for the question is an element of list, convert it to one string
                        res_data[heading] = the_answer 
            clean_lst.append(res_data) #add the data to clean_lst

        columns = keep_data[:] #make the keep data part of the df columns
        for question in code_book:  #iterate over every qeustion in the codebook
            columns.append(code_book[question]["heading"]) #make the heading a column in the df
            
        survey_data_dict = {}
        for variable in columns: #iterate over variable in the column
            survey_data_dict[variable] = []
            for respondent in clean_lst: #iterate over every respondent
                if variable in respondent.keys(): #if you find that question in there data pull out there answer
                    survey_data_dict[variable].append(respondent.get(variable))
                else: #else assign there answer as NA
                    survey_data_dict[variable].append("NA")
        return(pd.DataFrame(data = survey_data_dict)) #make that dictionary into a DataFrame
    def keep_data_options(self): #method to see possible values for keep_data
        print("Your options are: " + str(['id', 'recipient_id', 'collection_mode', 'response_status', 'custom_value', 'first_name', 'last_name',
                                          'email_address', 'ip_address','logic_path', 'metadata', 'collector_id', 'survey_id', 'custom_variables',
                                          'edit_url', 'analyze_url', 'total_time','date_modified', 'date_created', 'href'])) #print options to screen
        
                   
