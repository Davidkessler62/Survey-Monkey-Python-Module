import Survey_Monkey

#Create an instance of class Survey Monkey and define api key
monkey = Survey_Monkey(api_key = "Your API Key")

#Get a dataframe of all survey's you have in Survey Monkey
ari_surveys_df = monkey.get_survey_list(output = "df")

#print the dataframe into the console
print(ari_surveys_df)

#Get responses from one of your surveys
results_df = monkey.get_survey_data(survey_id = "example id")
#Print the responses into the console
print(results_df)

#Get the code_book for a survey, store it in a variable, and pass it as an argument to the get_survey_data() method
codebook = monkey.get_survey_codebook(surveyid = 274291824)
df2 = monkey.get_survey_data(survey_id = "example id", code_book = codebook)
print(df2)

#Change the keep_data to only gather the ip address
df3 = monkey.get_survey_data(survey_id = "example id", keep_data = ["ip_address"])
print(df3)

