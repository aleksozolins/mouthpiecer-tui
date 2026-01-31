# Import needed modules
import os                         # for clearing the screen and other OS level commands
import requests                   # for communicating via API
import json                       # for handling JSON
import getpass                    # provides a password input without revealing text
from rich.console import Console  # rich terminal output
from rich.table import Table      # rich tables


def clear_screen():
    """Clear the terminal screen (cross-platform)."""
    os.system('cls' if os.name == 'nt' else 'clear')


# Rich console for colored output
console = Console()

# Knack API configuration (load from environment variables)
KNACK_APP_ID = os.environ.get('KNACK_APP_ID', '60241522a16be4001b611249')
KNACK_API_KEY = os.environ.get('KNACK_API_KEY', '82d8170b-0661-4462-8dbb-3a589abdfc39')

# Knack field ID mappings (mouthpiece object)
FIELD_MAKE = 'field_17'
FIELD_MODEL = 'field_16'
FIELD_TYPE = 'field_24'
FIELD_THREADS = 'field_25'
FIELD_FINISH = 'field_26'

# Knack field ID mappings (user object)
FIELD_USER_NAME = 'field_1'
FIELD_USER_EMAIL = 'field_2'
FIELD_USER_PASSWORD = 'field_3'
FIELD_USER_STATUS = 'field_4'
FIELD_USER_ROLE = 'field_5'

# declare some vars
token = ""
with open('banner.txt', 'r') as bannerfile:
    banner = bannerfile.read()
mpcselect = 0
mouthpieces = []  # list of mouthpiece dicts from API


# Login process
def login():
    global token
    global logemail
    if token != "":
        input("Please log out first. Press Enter...")
    else:
        print("Please log in...")
        print()
        logemail = input("Email: ")
        passwd = getpass.getpass("Password: ")
        api_url = f"https://api.knack.com/v1/applications/{KNACK_APP_ID}/session"
        creds = {"email": logemail, "password": passwd}
        headers = {"content-type":"application/json", "X-Knack-REST-API-KEY": KNACK_API_KEY}
        response = requests.post(api_url, data=json.dumps(creds), headers=headers)
        jresponse = response.json()
        if response.status_code == 200:
            token = jresponse['session']['user']['token']
            print()
            input("You have been logged in. Press Enter to continue...")
        else:
            print()
            console.print("[red]Invalid credentials.[/red] ", end="")
            input("Press Enter to continue...")


# Login process for new users
def loginnewusr():
    global token
    api_url = f"https://api.knack.com/v1/applications/{KNACK_APP_ID}/session"
    creds = {"email": newusremail, "password": newusrpasswd1}
    headers = {"content-type":"application/json", "X-Knack-REST-API-KEY": KNACK_API_KEY}
    response = requests.post(api_url, data=json.dumps(creds), headers=headers)
    jresponse = response.json()
    token = jresponse['session']['user']['token']


# Logout process
def logout():
    global token
    if token == "":
        input("You aren't currently logged in. Press Enter...")
    else:
        input("You will be logged out. Press Enter...")
        token = ""


# Our Main Menu
def mainmenu():
    clear_screen()
    if token == "":
        print()
        print("You are not currently logged in...")
        console.print(f"[yellow]{banner}[/yellow]")
        print("[1] My mouthpieces")
        print("-----------------------")
        console.print("[green][6][/green] Log in")
        print("[7] Log out")
        console.print("[green][8][/green] Add a user")
        print("-----------------------")
        console.print("[green][0][/green] Exit to shell")
        print()
    else:
        print()
        console.print(f"You are logged in as [blue]{logemail}[/blue]")
        console.print(f"[yellow]{banner}[/yellow]")
        console.print("[green][1][/green] My mouthpieces")
        print("-----------------------")
        print("[6] Log in")
        console.print("[green][7][/green] Log out")
        print("[8] Add a user")
        print("-----------------------")
        console.print("[green][0][/green] Exit to shell")
        print()


# My Mouthpieces Menu
def mympcsmenu():
    global mpcselect
    clear_screen()
    print()
    console.print(f"You are logged in as [blue]{logemail}[/blue]")
    console.print(f"[yellow]{banner}[/yellow]")
    console.print(f"--- Mouthpieces for [blue]{logemail}[/blue] ---")
    print()
    if mpcselect == 0:
        console.print("[green][1][/green] Add mouthpiece               [green][3][/green] Edit mouthpiece")
        console.print("[green][2][/green] Delete mouthpiece            [green][0][/green] Back to main menu")
        print("------------------------------------------------------")
        print()
    if mpcselect == 1:
        print("[1] Add mouthpiece               [3] Edit mouthpiece")
        print("[2] Delete mouthpiece            [0] Back to main menu")
        print("------------------------------------------------------")
        print()


# Menu for selecting a mouthpiece type
def mpctypemenu():
    print()
    console.print("[green][1][/green] one-piece")
    console.print("[green][2][/green] two-piece")
    console.print("[green][3][/green] cup")
    console.print("[green][4][/green] rim")
    print()


# Menu for selecting mouthpiece threads
def mpcthreadsmenu():
    print()
    console.print("[green][1][/green] standard")
    console.print("[green][2][/green] metric")
    console.print("[green][3][/green] other")
    print()


# Menu for selecting a mouthpiece finish
def mpcfinishmenu():
    print()
    console.print("[green][1][/green] silver plated")
    console.print("[green][2][/green] gold plated")
    console.print("[green][3][/green] brass")
    console.print("[green][4][/green] nickel")
    console.print("[green][5][/green] stainless")
    console.print("[green][6][/green] bronze")
    console.print("[green][7][/green] plastic")
    print()


# Add mouthpiece process
def addmpc():
    print()
    newmake = input("Make: ")
    print()
    newmodel = input("Model: ")
    mpctypemenu()
    while True:
        option = input("Type: ")
        try:
            option = (int(option))
            if option not in (1, 2, 3, 4):
                raise ValueError
        except ValueError:
            console.print("[red]Invalid Option[/red]")
            print()
            continue
        break
    if option == 1:
        newtype = "one-piece"
    elif option == 2:
        newtype = "two-piece"
    elif option == 3:
        newtype = "cup"
    elif option == 4:
        newtype = "rim"
    newthreads = ""
    if newtype != "one-piece":
        mpcthreadsmenu()
        while True:
            option = input("Threads: ")
            try:
                if option not in ("1", "2", "3", ""):
                    raise ValueError
            except ValueError:
                console.print("[red]Invalid Option[/red]")
                print()
                continue
            break
        if option == "1":
            newthreads = "standard"
        elif option == "2":
            newthreads = "metric"
        elif option == "3":
            newthreads = "other"
        elif option == "":
            newthreads = ""
    mpcfinishmenu()
    while True:
        option = input("Finish: ")
        try:
            option = (int(option))
            if option not in (1, 2, 3, 4, 5, 6, 7):
                raise ValueError
        except ValueError:
            console.print("[red]Invalid Option[/red]")
            print()
            continue
        break
    if option == 1:
        newfinish = "silver plated"
    elif option == 2:
        newfinish = "gold plated"
    elif option == 3:
        newfinish = "brass"
    elif option == 4:
        newfinish = "nickel"
    elif option == 5:
        newfinish = "stainless"
    elif option == 6:
        newfinish = "bronze"
    elif option == 7:
        newfinish = "plastic"
    print()
    print("------------------------")
    console.print(f"Make: [green]{newmake}[/green]")
    console.print(f"Model: [green]{newmodel}[/green]")
    console.print(f"Type: [green]{newtype}[/green]")
    console.print(f"Threads: [green]{newthreads}[/green]")
    console.print(f"Finish: [green]{newfinish}[/green]")
    print("------------------------")
    print()
    while True:
        console.print("Send to Knack? [green][y] [n]:[/green] ", end="")
        conf = input()
        try:
            if conf not in ("y", "n"):
                raise ValueError
        except ValueError:
            console.print("[red]Invalid Option[/red]")
            print()
            continue
        break
    if conf == "y":
        api_url = "https://api.knack.com/v1/pages/scene_18/views/view_18/records"
        mouthpiece = {FIELD_MAKE: newmake, FIELD_TYPE: newtype, FIELD_MODEL: newmodel, FIELD_THREADS: newthreads, FIELD_FINISH: newfinish}
        headers = {"content-type":"application/json", "X-Knack-Application-Id": KNACK_APP_ID, "X-Knack-REST-API-KEY":"knack", "Authorization":token}
        response = requests.post(api_url, data=json.dumps(mouthpiece), headers=headers)
        print()
        if response.status_code == 200:
            input("Success! Press Enter to continue...")
            mympcs()
        else:
            console.print("[red]Error! There was a problem with your request.[/red] ", end="")
            input("Press Enter to continue...")
            mympcs()
    else:
        mpcselect = 0
        mympcs()


# My mouthpieces process
def mympcs():
    global mouthpieces
    if token == "":
        input("Please log in first. Press Enter...")
    else:
        mympcsmenu()
        listmpcs()
        while True:
            selection = input("Make a menu selection: ")
            try:
                selection = (int(selection))
                if selection not in (1, 2, 3, 0):
                    raise ValueError
            except ValueError:
                console.print("[red]Invalid Option[/red]")
                print()
                continue
            break
        if selection == 1:
            addmpc()
        elif selection == 2:
            delmpc()
        elif selection == 3:
            editmpc()
        elif selection == 0:
            mainmenu()


# List mouthpieces process
def listmpcs():
    global mouthpieces
    api_url = "https://api.knack.com/v1/pages/scene_18/views/view_18/records"
    headers = {"content-type":"application/json", "X-Knack-Application-Id": KNACK_APP_ID, "X-Knack-REST-API-KEY":"knack", "Authorization":token}
    response = requests.get(api_url, headers=headers)
    jresponse = response.json()

    # Store mouthpieces as list of dicts
    mouthpieces = []
    for idx, record in enumerate(jresponse.get('records', [])):
        mouthpieces.append({
            'index': idx,
            'id': record.get('id', ''),
            'Make': record.get(FIELD_MAKE, ''),
            'Model': record.get(FIELD_MODEL, ''),
            'Type': record.get(FIELD_TYPE, ''),
            'Threads': record.get(FIELD_THREADS, ''),
            'Finish': record.get(FIELD_FINISH, ''),
        })

    # Build rich table
    table = Table()
    table.add_column("Index", style="dim")
    table.add_column("Make")
    table.add_column("Model")
    table.add_column("Type")
    table.add_column("Threads")
    table.add_column("Finish")

    style = "green" if mpcselect == 1 else None
    for mpc in mouthpieces:
        table.add_row(
            str(mpc['index']),
            mpc['Make'],
            mpc['Model'],
            mpc['Type'],
            mpc['Threads'],
            mpc['Finish'],
            style=style
        )

    console.print(table)
    print()


# Delete mouthpiece process
def delmpc():
    if len(mouthpieces) == 1:
        print()
        console.print("[red]Add another mouthpiece to delete.[/red] You need at least one in place. ", end="")
        input("Press Enter to continue...")
        mympcs()
    else:
        global mpcselect
        mpcselect = 1
        mympcsmenu()
        listmpcs()
        print("Make a menu selection: 2")
        print()
        while True:
            selection = input("Select a mouthpiece by Index to delete: ")
            try:
                selection = (int(selection))
                if selection not in range(0, len(mouthpieces)):
                    raise ValueError
            except ValueError:
                console.print("[red]Invalid Option[/red]")
                print()
                continue
            break
        print()
        mpc = mouthpieces[selection]
        while True:
            console.print(f"[red]Are you sure you want to delete this[/red] {mpc['Make']} {mpc['Model']} [green][y] [n]:[/green] ", end="")
            conf = input()
            try:
                if conf not in ("y", "n"):
                    raise ValueError
            except ValueError:
                console.print("[red]Invalid Option[/red]")
                print()
                continue
            break
        if conf == "y":
            delid = mpc['id']
            api_url = "https://api.knack.com/v1/pages/scene_18/views/view_18/records/" + delid
            headers = {"content-type":"application/json", "X-Knack-Application-Id": KNACK_APP_ID, "X-Knack-REST-API-KEY":"knack", "Authorization":token}
            response = requests.delete(api_url, headers=headers)
            print()
            if response.status_code == 200:
                input("Success! Press Enter to continue...")
                mpcselect = 0
                mympcs()
            else:
                console.print("[red]Error! There was a problem with your request.[/red] ", end="")
                input("Press Enter to continue...")
                mpcselect = 0
                mympcs()
        else:
            mpcselect = 0
            mympcs()


# Edit mouthpiece process
def editmpc():
    global mpcselect
    mpcselect = 1
    mympcsmenu()
    listmpcs()
    print("Make a menu selection: 3")
    print()
    while True:
        selection = input("Select a mouthpiece by Index to edit: ")
        try:
            selection = (int(selection))
            if selection not in range(0, len(mouthpieces)):
                raise ValueError
        except ValueError:
            console.print("[red]Invalid Option[/red]")
            print()
            continue
        break
    print()
    mpc = mouthpieces[selection]
    newmake = input(f"Make ({mpc['Make']}): ")
    print()
    newmodel = input(f"Model ({mpc['Model']}): ")
    mpctypemenu()
    while True:
        option = input(f"Type ({mpc['Type']}): ")
        try:
            option = (int(option))
            if option not in (1, 2, 3, 4):
                raise ValueError
        except ValueError:
            console.print("[red]Invalid Option[/red]")
            print()
            continue
        break
    if option == 1:
        newtype = "one-piece"
    elif option == 2:
        newtype = "two-piece"
    elif option == 3:
        newtype = "cup"
    elif option == 4:
        newtype = "rim"
    newthreads = ""
    if newtype != "one-piece":
        mpcthreadsmenu()
        while True:
            option = input(f"Threads ({mpc['Threads']}): ")
            try:
                if option not in ("1", "2", "3", ""):
                    raise ValueError
            except ValueError:
                console.print("[red]Invalid Option[/red]")
                print()
                continue
            break
        if option == "1":
            newthreads = "standard"
        elif option == "2":
            newthreads = "metric"
        elif option == "3":
            newthreads = "other"
        elif option == "":
            newthreads = ""
    mpcfinishmenu()
    while True:
        option = input(f"Finish ({mpc['Finish']}): ")
        try:
            option = (int(option))
            if option not in (1, 2, 3, 4, 5, 6, 7):
                raise ValueError
        except ValueError:
            console.print("[red]Invalid Option[/red]")
            print()
            continue
        break
    if option == 1:
        newfinish = "silver plated"
    elif option == 2:
        newfinish = "gold plated"
    elif option == 3:
        newfinish = "brass"
    elif option == 4:
        newfinish = "nickel"
    elif option == 5:
        newfinish = "stainless"
    elif option == 6:
        newfinish = "bronze"
    elif option == 7:
        newfinish = "plastic"
    print()
    print("OLD---------------------")
    console.print(f"Make: [red]{mpc['Make']}[/red]")
    console.print(f"Model: [red]{mpc['Model']}[/red]")
    console.print(f"Type: [red]{mpc['Type']}[/red]")
    console.print(f"Threads: [red]{mpc['Threads']}[/red]")
    console.print(f"Finish: [red]{mpc['Finish']}[/red]")
    print("---------------------OLD")
    print()
    print("NEW---------------------")
    console.print(f"Make: [green]{newmake}[/green]")
    console.print(f"Model: [green]{newmodel}[/green]")
    console.print(f"Type: [green]{newtype}[/green]")
    console.print(f"Threads: [green]{newthreads}[/green]")
    console.print(f"Finish: [green]{newfinish}[/green]")
    print("---------------------NEW")
    print()
    while True:
        console.print("Save changes? [green][y] [n]:[/green] ", end="")
        conf = input()
        try:
            if conf not in ("y", "n"):
                raise ValueError
        except ValueError:
            console.print("[red]Invalid Option[/red]")
            print()
            continue
        break
    if conf == "y":
        editid = mpc['id']
        api_url = "https://api.knack.com/v1/pages/scene_18/views/view_18/records/" + editid
        mouthpiece = {FIELD_MAKE: newmake, FIELD_TYPE: newtype, FIELD_MODEL: newmodel, FIELD_THREADS: newthreads, FIELD_FINISH: newfinish}
        headers = {"content-type":"application/json", "X-Knack-Application-Id": KNACK_APP_ID, "X-Knack-REST-API-KEY":"knack", "Authorization":token}
        response = requests.put(api_url, data=json.dumps(mouthpiece), headers=headers)
        print()
        if response.status_code == 200:
            input("Success! Press Enter to continue...")
            mpcselect = 0
            mympcs()
        else:
            console.print("[red]Error! There was a problem with your request.[/red] ", end="")
            input("Press Enter to continue...")
            mpcselect = 0
            mympcs()
    else:
        mpcselect = 0
        mympcs()

# Add user process
# NOTE: Adding the connected Mouthpiecer in field_40 does not yet work. We may need to retrieve the ID of the new account and then add that value with an additional call.
def addusr():
    global newusremail
    global newusrpasswd1
    global logemail
    if token != "":
        input("Please log out before adding a user. Press Enter...")
    else:
        newusrfname = str(input("First name: "))
        print()
        newusrlname = str(input("Last name: "))
        newusrfullname = newusrfname + "" + newusrlname
        print()
        newusremail = str(input("Email: "))
        print()
        newusrpasswd1 = getpass.getpass("Password: ")
        newusrpasswd2 = getpass.getpass("Confirm: ")
        if newusrpasswd1 != newusrpasswd2:
            print()
            console.print("[red]Passwords do not match.[/red] Process aborted. ", end="")
            input("Press Enter to continue...")
        else:
            logemail = newusremail
            print()
            input("Press Enter to send to Knack...")
            api_url = "https://api.knack.com/v1/objects/object_1/records"
            newusr = {
                FIELD_USER_NAME: {"first": newusrfname, "last": newusrlname},
                FIELD_USER_EMAIL: newusremail,
                FIELD_USER_PASSWORD: newusrpasswd1,
                FIELD_USER_STATUS: "active",
                FIELD_USER_ROLE: "Mouthpiecer"
            }
            headers = {"content-type":"application/json", "X-Knack-Application-Id": KNACK_APP_ID, "X-Knack-REST-API-KEY": KNACK_API_KEY}
            response = requests.post(api_url, data=json.dumps(newusr), headers=headers)
            if response.status_code == 200:
                loginnewusr()
                print()
                input("Success! You have been added and logged in. Let's add your first mouthpiece. Press Enter to continue...")
                addmpc()
            else:
                print()
                console.print("[red]Error! There was a problem with your request.[/red] ", end="")
                input("Press Enter to continue...")
                mainmenu()


# Retrieve user process
def rusr():
    usrid = (input("Enter user ID:"))
    input("Press Enter to send to Knack...")
    api_url = "https://api.knack.com/v1/objects/object_1/records/" + usrid
    headers = {"content-type":"application/json", "X-Knack-Application-Id": KNACK_APP_ID, "X-Knack-REST-API-KEY": KNACK_API_KEY}
    response = requests.get(api_url, headers=headers)
    print(response.json())
    print(response.status_code)


# Here's where the program runs
mainmenu()
option = input("Enter your choice: ")

while option != "0":
    if option == "1":
        print()
        mympcs()
    elif option == "6":
        print()
        login()
    elif option == "7":
        print()
        logout()
    elif option == "8":
        print()
        addusr()
    else:
        print()
        console.print("[red]Invalid option selected.[/red] ", end="")
        input("Press Enter to continue...")

    print()
    mainmenu()
    option = input("Enter your choice: ")

print()
print("You've exited to shell")
print()
