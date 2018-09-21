import logging

from flask import Flask, render_template, request, redirect, flash, url_for
import datetime
from googleSheetsData import getMenuCalData,getSchoolData,getMenuData,getBaselineOptInData,sendToDatabase,getLiveSchools
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import datetime

scope = ['https://spreadsheets.google.com/feeds']
credentials = ServiceAccountCredentials.from_json_keyfile_name('./MWCapp-6ea127e5c10a.json', scope)
gc = gspread.authorize(credentials)



def getMenuDay(meal,dateStr):
    menuCalDict = getMenuCalData()

    if dateStr in menuCalDict.keys():
        if meal == 'Breakfast':
            return menuCalDict[dateStr]["breakfast"]
        else:
            return menuCalDict[dateStr]["lunch"]



def getGrabAndGo(school,menu,meal):
    menuSheetDict = getMenuData()
    if meal == "Lunch":
        if school == "East Boston HS":
            return menuSheetDict["gg-ebhs-"+menu]['components']
        if school == "Mckay K-8" or school == "Umana/Mario Academy K-8":
            return menuSheetDict["gg-mk&um-"+menu]['components']
    else:
        return []

def plannedDictBuilder(menuDayComponents,school,meal):
    schoolDict = getSchoolData()
    returnDict = {}
    baselineOptInDict = getBaselineOptInData()

    for component in menuDayComponents:
        try:
            attendance = schoolDict[school]['attendance']
            mealOptIn = schoolDict[school][meal]
            componentOptIn = baselineOptInDict[component][school]
            planned = attendance*mealOptIn*componentOptIn
            returnDict[component] = int(planned)
        except Exception as e:
            returnDict[component] = "Unknown"
    return returnDict

def getFruitArray(formData):
    fruits = ["Fruit 1","Fruit 2","Fruit 3"]
    output = []
    for fruit in fruits:
        if formData[fruit] != "None":
            output.append(formData[fruit])
    return output


app = Flask(__name__)
app.config['SECRET_KEY'] = '1234567890123456'



@app.route('/', methods = ['POST','GET'])
def enter_pr_data():
    menuSheetDict = getMenuData()
    menuCalDict = getMenuCalData()

    if request.method == 'POST':
        sendToDatabase(request.form)
        return render_template('home.html',schools=getLiveSchools(),
            fruits=menuSheetDict["am: fruit"]['components'],numFruits=["Fruit 1","Fruit 2","Fruit 3"],menuCalDict=menuCalDict)
    else:
        return render_template('home.html',schools=getLiveSchools(),
            fruits=menuSheetDict["am: fruit"]['components'],numFruits=["Fruit 1","Fruit 2","Fruit 3"],menuCalDict=menuCalDict)


@app.route('/generateTable', methods = ['POST'])
def signup():

    menuSheetDict = getMenuData()
    schoolDict = getSchoolData()
    menuCalDict = getMenuCalData()

    if request.method == 'POST':
      result = request.form
      meal = request.form['meal']
      date = request.form['date']
      fruits = getFruitArray(request.form)

    try:
        menuCalDict[date]
    except Exception as e:
        flash('Not a valid menu day')
        return redirect(url_for('enter_pr_data'))

    school = request.form['school']
    menuDay = getMenuDay(meal,date)

    try:
        menuSheetDict[menuDay]['components']
    except Exception as e:
        flash('Cannot find menu day componnets')
        return redirect(url_for('enter_pr_data'))

    menuDayComponents = menuSheetDict[menuDay]['components']
    saladComponents = menuSheetDict['al: salad bar']['components']
    isLunch = meal == "Lunch"
    isGrab = schoolDict[school]['grabAndGo'][0] == "TRUE"
    isExpanded = schoolDict[school]['expandedSalad'][0] == "TRUE"
    isHs = schoolDict[school]['age'][0] == "912"
    expandedComponents = menuSheetDict['hsl: salad bar add-ons']['components']
    grabAndGoBreakComponents = menuSheetDict['hsb: grab n go']['components']
    grabAndGoLunchComponents = getGrabAndGo(school,menuDay,meal)


    return render_template("result.html",
        result = result,
        menuDay = menuDay,
        drinks = plannedDictBuilder(menuSheetDict["am: drinks"]['components'],school,meal),
        components = plannedDictBuilder(menuDayComponents,school,meal),
        fruits = plannedDictBuilder(fruits,school,meal),
        saladComponents = plannedDictBuilder(saladComponents,school,meal),
        isLunch = isLunch,
        isGrab = isGrab,
        isExpanded = isExpanded,
        isHs = isHs,
        expandedComponents = plannedDictBuilder(expandedComponents,school,meal),
        grabAndGoBreakComponents = plannedDictBuilder(grabAndGoBreakComponents,school,meal),
        grabAndGoLunchComponents = plannedDictBuilder(grabAndGoLunchComponents,school,meal))





 
@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)



