import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('./MWCapp-6ea127e5c10a.json', scope)
gc = gspread.authorize(credentials)


mainDatabaseKey = '1SHD8PpHVwbqErSb98IUfSCvPmtuBuoharKSvHHW3Snw'
orderingToolKey = '1ZbMTvlplLRQZYawlHr2ptkaubn_iukXVQZD0uDRsFTo'
mainDatabaseSpreadsheet = gc.open_by_key(mainDatabaseKey)
orderingToolSpreadsheet = gc.open_by_key(orderingToolKey)

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


def sendToDatabase(formDict):
	test = mainDatabaseSpreadsheet.worksheet("Sheet33")
	#testLength = len(test.get_all_values)
	i = 1
	for form in formDict:
		test.update_cell(i, 1, form)
		test.update_cell(i, 2, formDict[form])
		i+=1
	'''
	row=[]
	i=0
	for key in formDict:
		if i == 0 or i % 6 == 1
		test.insert_row(row, index)

	#Update in batch
	test.update_cells(cell_list)
	'''