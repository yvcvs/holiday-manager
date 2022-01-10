from datetime import datetime, time, date, timedelta

import json
from os import makedirs
from typing import _SpecialForm
from bs4 import BeautifulSoup
import requests

from dataclasses import dataclass
import attr
import pprint
from dateutil.parser import parse

@dataclass
class Holiday:
    name: str
    date: datetime

    def __str__ (self):
        return f"{self.name} ({self.date})"

class HolidayList:
    def __init__(self):
        self.innerHolidays = []

    def addHoliday(self, holidayObj):
        # Make sure holidayObj is a Holiday Object by checking the type
        try:
            if isinstance(holidayObj, Holiday) == True:
                # if holiday is in innerHolidays, don't add
                if holidayObj in self.innerHolidays:
                    print("That's already in the list of holidays!")
                # Use innerHolidays.append(holidayObj) to add holiday
                else:
                    holidayObj = holidayObj.__dict__
                    self.innerHolidays.append(holidayObj)
        except:
            print("That's not a holiday.")
        return print("The holiday list has been updated.")

    def findHoliday(self, chosenHoliday):
        try:
            # Find Holiday in innerHolidays
            if chosenHoliday not in self.innerHolidays:
                print(f'{chosenHoliday} is not found.')
            else:
            # Return Holiday
                return chosenHoliday
        except:
            print(f'Error:\n{chosenHoliday} not found.')

    def removeHoliday(self, chosenHoliday):
        try:
            # Find Holiday in innerHolidays by searching
            foundHoliday = self.findHoliday(chosenHoliday)
            name = foundHoliday['name']
            # remove the Holiday from innerHolidays
            self.innerHolidays.remove(foundHoliday)
            # inform user you deleted the holiday
            print(f'Success:\n{name} has been removed from the holiday list.')
        except:
            print(f'Error:\n{chosenHoliday} not found.')

    def read_json(self, filelocation):
        # Read in things from json file location
        filelocation =  open('holidays.json')
        data = json.load(filelocation)
        for i in data['holidays']:
            date = parse(i['date'])
            date = date.strptime(i['date'], '%Y-%m-%d')
            holidayObj = Holiday(i['name'], i['date'])
            # Use addHoliday function to add holidays to inner list.
            self.addHoliday(holidayObj)

    def save_to_json(self):
        print("Saving Holiday List\n====================")
        save = str(input("Are you sure you want to save your changes? [y/n]: "))
        if save == 'y':
            double_check = str(input("Are you sure you want to save your changes?\nAnswering y will override the holidays [y/n]: "))
            if double_check == 'y':
                # Write out json file to selected file.
                with open('holidays.json', 'w') as holidays:
                    json.dump({'holidays': self.innerHolidays}, holidays, indent=4)
                print("Success:\nThe holiday list file has been saved.")
            if double_check == 'n':
                print("Canceled\nHoliday list file save canceled.")
        elif save == 'n':
            print("Canceled\nHoliday list file save canceled.")

    def scrapeHolidays(self, current_year):
        years = [current_year-2, current_year-1, current_year, current_year+1, current_year+2]
        for x in years:
            try:
                # Scrape Holidays
                html = getHTML(f'https://www.timeanddate.com/holidays/us/{x}')
                soup = BeautifulSoup(html, 'html.parser')
                body = soup.find('tbody')
                for row in body:
                    #gets rid of None values in tags that separate months
                    if len(row.get_text (strip=True)) == 0:
                        row.extract()
                    else:
                        name = row.find('a').string
                        hd = row.find('th').string
                        hd_updated = f'{hd}, {x}'
                        hd_string = parse(hd_updated)
                        date = hd_string.strftime('%Y-%m-%d')
                        holidayEntry = Holiday(name, date).__dict__
                        # Check to see if name and date of holiday is in innerHolidays array
                        # Add non-duplicates to innerHolidays
                        if holidayEntry not in self.innerHolidays:
                            self.innerHolidays.append(holidayEntry)
                        else:
                            continue
            except:
                # Handle any exceptions.
                print("Please input a year in the format 'YYYY'.")

    def numHolidays(self):
        # Return the total number of holidays in innerHolidays
        total_holidays = len(self.innerHolidays)
        print(f'There are {total_holidays} holidays stored in the system.')

    def filter_holidays_by_week(self, year, weekNum):
        #use weekNum to find first and last day
        firstDay = datetime.strptime(f'{year}-W{int(weekNum)-1}-1', '%Y-W%W-%w').date()
        lastDay = firstDay + timedelta(days=6.9)
        delta = lastDay - firstDay
        #find dates in the weekNum
        dates = []
        for i in range(delta.days + 1):
            day = firstDay + timedelta(days = i)
            dates.append(day.strftime('%Y-%m-%d'))
        # Use a Lambda function to filter by week number and save this as holidays, use the filter on innerHolidays
        # Cast filter results as list
        results = filter(lambda x: x['date'] in dates, self.innerHolidays)
        weekHolidays = list(results)
        # return your holidays
        return weekHolidays

    def displayHolidaysInWeek(self, pickedYear, pickedWeek):
        # Use your filter_holidays_by_week to get list of holidays within a week as a parameter
        output = self.filter_holidays_by_week(pickedYear, pickedWeek)
        # Output formated holidays in the week.
        print(f'These are the holidays for week {pickedWeek}:')
        for x in (output):
            print(Holiday(x['name'], x['date']))

    def getWeather(self, year, weekNum):
        # Convert weekNum to range between two days
        firstDay = datetime.strptime(f'{year}-W{int(weekNum)-1}-1', '%Y-W%W-%w').date()
        lastDay = firstDay + datetime.timedelta(days=6.9)
        # Use Try / Except to catch problems
        # Query API for weather in that week range
        # Format weather information and return weather string.

    def viewCurrentWeek(self): #needs to return week and weather
        # Use the Datetime Module to look up current week and year
        today = datetime.today()
        year, weekNum, day_of_week = today.isocalendar()
        # Ask user if they want to get the weather
        try:
            forecast = str(input("Would you like to see this week's weather? [y/n]: "))
            # If yes, use your getWeather function and display results
            if forecast == 'y':
                print("Get weather API here.")
                pass
            elif forecast == 'n':
                # Use your displayHolidaysInWeek function to display the holidays in the week
                # filter_holidays_by_week function is called inside display function
                self.displayHolidaysInWeek(year, weekNum)
        except:
            print("Please enter y or n.")

# 1. Initialize HolidayList Object
listObj = HolidayList() #the actual thing that yyou change

#get HTML for web scraping
def getHTML(fullURL):
    response = requests.get(fullURL)
    return response.text

# 6. Run appropriate method from the HolidayList object depending on what the user input is
def addMenuOption():
    print('Add a Holiday\n=============')
    name = str(input('Holiday: '))
    date = str(input('Date [YYYY-MM-DD format]: '))
    date = parse(date)
    date = date.strftime('%Y-%m-%d')
    holidayObj = Holiday(name, date)
    listObj.addHoliday(holidayObj)

def removeHoliday():
    print('Remove a Holiday\n================')
    holidayName = str(input("Holiday Name: "))
    date = str(input("Holiday Date [YYYY-MM-DD format]: "))
    date = parse(date)
    holidayDate = date.strftime('%Y-%m-%d')
    chosenHoliday = Holiday(holidayName, holidayDate).__dict__
    listObj.removeHoliday(chosenHoliday)

def save():
    listObj.save_to_json()

def viewHolidays():
    print("View Holidays\n=================")
    pickedYear = str(input("Which year? "))
    pickedWeek = input("Which week? [1-52, Leave blank for current week]: ")
    try:
        if pickedWeek == '':
            listObj.viewCurrentWeek()
        elif pickedWeek < 53 and pickedWeek > 0:
            print("test")
            listObj.displayHolidaysInWeek(pickedYear, pickedWeek)
        else:
            print("Pick a number from 1 to 52.")
    except:
        print("Error:\nWas not able to display the week's holidays.")

#main menu
def main():
    # 2. Load JSON file via HolidayList read_json function
    filename = 'holidays.json'
    listObj.read_json(filename)

    # 3. Scrape additional holidays using your HolidayList scrapeHolidays function.
    current_date = date.today()
    current_year = current_date.year
    listObj.scrapeHolidays(current_year)

    #insert start up message
    print("Holiday Management\n===================")
    listObj.numHolidays()

    # 3. Create while loop for user to keep adding or working with the Calender
    run = str(input("Want to continue? [y/n]: "))
    while run == 'y':
        # 4. Display User Menu (Print the menu)
        print ('''Holiday Menu
        ================
        1. Add a Holiday
        2. Remove a Holiday
        3. Save Holiday List
        4. View Holidays
        5. Exit''')
        # 5. Take user input for their action based on Menu and check the user input for errors
        menuChoice = int(input("Choose a menu number: "))
        if menuChoice == 1:
            addMenuOption()
        elif menuChoice == 2:
            removeHoliday()
        elif menuChoice == 3:
            save()
        elif menuChoice == 4:
            viewHolidays()
        elif menuChoice == 5:
            exit()
        else:
            print("Please select a number 1 through 5.")
    # 7. Ask the User if they would like to Continue, if not, end the while loop, ending the program.  If they do wish to continue, keep the program going.        
    if run == 'n':
        exit()
    else:
        print("Please select y or n.")


if __name__ == "__main__":
    main();


# Questions:
# ---------------------------------------------
# How do helper functions differ? I thought they all technically "helped"

# The example below doesn't make sense, but I want to know how to do it

# You can store your raw menu text, and other blocks of texts as raw text files 
# and use placeholder values with the format option.
# Example:
# In the file test.txt is "My name is {fname}, I'm {age}"
# Then you later can read the file into a string "filetxt"
# and substitute the placeholders 
# for example: filetxt.format(fname = "John", age = 36)
# This will make your code far more readable, by seperating text from code.