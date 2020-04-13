# Survey-Monkey-Python-Module

Survey Monkey Class Methods:

Survey_Monkey().get_survey_list(output = "df")
	Description: This method will all you to get a list of all the surveys you have in SurveyMonkey, along with the id for each survey.
		
	Arguments:
		output: "df" for dataframe, "list" for list, and "dict" for dictionary
Survey_Monkey.get_survey_codebook(surveyid)
	Description: When you get data from Survey Monley, the answers are encoded and must be recoded to there normal form using the code_book generated
			from this method. I reccomend getting the code_book the first time you get responses for a survey, and then saving it for future
			use. 

	Arguments: 
		survey_id: the SurveyMonkey id of the survey 		 
Survey_Monkey().get_survey_data(survey_id, keep_data = ["id", "ip_address", "collector_id"], code_book = None)
	Description: Gets survey data for a survey and returns it in a dataframe.
		
	Arguments:
		survey_id: the SurveyMonkey id of the survey
		keep_data: these are variables that are not questions in the Survey, but that SurveyMonkey stores when a respondent fills out a survey. The
			method accepts a list of what variables you want. For what the options are, call Survey_Monkey.keep_data_options()
		code_book: If you have a previously saved code book input it into this argument. If not, the method will automatically generate a codebook
			every time you call it.
Survey_Monkey.keep_data_options():
	Description: prints out the options for the keep_data argument is the get_survey_data() method. 
