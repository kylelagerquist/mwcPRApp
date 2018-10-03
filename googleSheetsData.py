import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('./MWCapp-6ea127e5c10a.json', scope)
gc = gspread.authorize(credentials)


mainDatabaseKey = '1SHD8PpHVwbqErSb98IUfSCvPmtuBuoharKSvHHW3Snw'
orderingToolKey = '1ZbMTvlplLRQZYawlHr2ptkaubn_iukXVQZD0uDRsFTo'
productionRecord = '1H2F_SLN_8LXagXuzxVDrbBjngjCpWwrUxH3SmLhtoS4'
mainDatabaseSpreadsheet = gc.open_by_key(mainDatabaseKey)
orderingToolSpreadsheet = gc.open_by_key(orderingToolKey)
productionRecordSpreadsheet = gc.open_by_key(productionRecord)

def getMenuCalData():
    menuCalSheet = mainDatabaseSpreadsheet.worksheet("[Table] MenuCal")
    menuCalData = menuCalSheet.get_all_values()
    menuCalDict = {}

    for x in range(2,len(menuCalData)-1,2):
        menuCalDict[menuCalData[x][0]] = {"breakfast": menuCalData[x][2], "lunch":menuCalData[x+1][2]}

    return menuCalDict
        
def getSchoolData():
    schoolsSheet = mainDatabaseSpreadsheet.worksheet("[Table] EaterInfo")
    schoolsData = schoolsSheet.get_all_values()
    schoolDict = {}

    for x in range(2,len(schoolsData)):
        schoolDict[schoolsData[x][2]] = {
        "name" : schoolsData[x][2],
        "live" : schoolsData[x][3],
        "age" : schoolsData[x][4],
        "population" : schoolsData[x][5],
        "attendance" : int(schoolsData[x][6]),
        "Breakfast" : int(schoolsData[x][7].strip('%'))/100,
        "Lunch" : int(schoolsData[x][8].strip('%'))/100,
        "expandedSalad" : schoolsData[x][9],
        "grabAndGo" : schoolsData[x][10]
        }

    return schoolDict


def getMenuData():
    menuSheet = mainDatabaseSpreadsheet.worksheet("[Table] Menu")
    menuData = menuSheet.get_all_values()
    menuSheetDict = {}

    for x in range(2,len(menuData)):
        menuSheetDict[menuData[x][0]] = {}
        menuSheetDict[menuData[x][0]]["components"] =  menuData[x][1].split(',')

    return menuSheetDict

def getBaselineOptInData():
    baselineOptInSheet = orderingToolSpreadsheet.worksheet("Baseline Opt In rates")
    baselineOptInData = baselineOptInSheet.get_all_values()
    baselineOptInDict = {}

    liveSchoolArray = getLiveSchools()
    for x in range(1,len(baselineOptInData)):
        baselineOptInDict[baselineOptInData[x][0]] = {}
        for y in range(1,len(baselineOptInData[x])):
        	if len(baselineOptInData[x][y]) > 1:
        		percentage = int(baselineOptInData[x][y].strip('%'))/100
        		baselineOptInDict[baselineOptInData[x][0]][baselineOptInData[0][y]] = percentage

    return baselineOptInDict

def getLiveSchools():
	schoolDict = getSchoolData()
	returnArray = []
	for key in schoolDict:
		if schoolDict[key]["live"] == "TRUE":
			returnArray.append(key)
	return returnArray

def getMenuDay(meal,dateStr):
    menuCalDict = getMenuCalData()

    if dateStr in menuCalDict.keys():
        if meal == 'Breakfast':
            return menuCalDict[dateStr]["breakfast"]
        else:
            return menuCalDict[dateStr]["lunch"]


def sendToDatabase(formDict):
	schoolDict = getSchoolData()
	PRComponentsSpreadsheet = productionRecordSpreadsheet.worksheet("[Table] PRComponents")
	PRMealsSpreadsheet = productionRecordSpreadsheet.worksheet("[Table] PRMeals")
	allComponentValues = PRComponentsSpreadsheet.get_all_values()
	allMealsValues = PRMealsSpreadsheet.get_all_values()
	allComponentValuesLength = len(allComponentValues)
	allMealsValuesLength = len(allMealsValues)
	tableAcc = []

	today = datetime.datetime.today().strftime('%D')
	mealDateSplit = formDict['date'].split("-")
	mealDate = mealDateSplit[1]+"/"+mealDateSplit[2]+"/"+mealDateSplit[0]
	meal = formDict['meal'].lower()
	menuDay = getMenuDay(meal,formDict['date'])
	school = formDict['school']

	if schoolDict[formDict['school']]['age'] == "912":
		mealRow = [today,mealDate,'20172018',
		school,meal,"0",formDict['reimbursable-meals'],
		formDict['adult-meals'],formDict['adult-earned-meals'],"",formDict['daily-notes']]

		PRMealsSpreadsheet.insert_row(mealRow, allMealsValuesLength+1)
	else:
		mealRow = [today,mealDate,'20172018',
		school,meal,formDict['reimbursable-meals'],"0",
		formDict['adult-meals'],formDict['adult-earned-meals'],"",formDict['daily-notes']]

		PRMealsSpreadsheet.insert_row(mealRow, allMealsValuesLength+1)



	rowAcc = []
	i = 1
	for form in formDict:
		if i > 10:
			ind = i % 7

			if ind == 4:
				rowAcc.extend([today,mealDate,school,meal,menuDay,form[8:],formDict[form]])	
			elif ind == 3:
				rowAcc.append(formDict[form])
				tableAcc.append(rowAcc)
				rowAcc = []
			else:
				rowAcc.append(formDict[form])			
		i+=1
	

	for x in range(0,len(tableAcc)):
		PRComponentsSpreadsheet.insert_row(tableAcc[x], allComponentValuesLength+x+1)
	

	
