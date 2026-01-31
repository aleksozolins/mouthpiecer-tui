# Import needed modules
import os                         # for clearing the screen and other OS level commands
import requests                   # for communicating via API
import json                       # for handling JSON
import getpass                    # provides a password input without revealing text
from rich.console import Console  # rich terminal output
from rich.table import Table      # rich tables
from rich.panel import Panel      # rich panels for menus
import questionary                # interactive prompts with autocomplete


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
FIELD_NOTE = 'field_27'

# Cache for dynamically fetched makes
_makes_cache = None

def get_makes():
    """Fetch available mouthpiece makes from Knack (cached after first call)."""
    global _makes_cache
    if _makes_cache is not None:
        return _makes_cache

    try:
        url = "https://api.knack.com/v1/objects/object_4/fields"
        headers = {
            "X-Knack-Application-Id": KNACK_APP_ID,
            "X-Knack-REST-API-Key": KNACK_API_KEY
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            fields = response.json().get('fields', [])
            for field in fields:
                if field.get('key') == FIELD_MAKE:
                    _makes_cache = field.get('choices', [])
                    return _makes_cache
    except Exception:
        pass

    # Fallback if API fails
    _makes_cache = ["Unknown"]
    return _makes_cache


def validate_make(value):
    """Validate that make is in the allowed list."""
    makes = get_makes()
    if value in makes:
        return True
    return "Please select a make from the list"


# Knack field ID mappings (user object)
FIELD_USER_NAME = 'field_1'
FIELD_USER_EMAIL = 'field_2'
FIELD_USER_PASSWORD = 'field_3'
FIELD_USER_STATUS = 'field_4'
FIELD_USER_ROLE = 'field_5'

# Pagination settings
PAGE_SIZE = 10

# declare some vars
token = ""
with open('banner.txt', 'r') as bannerfile:
    banner = bannerfile.read()
mpcselect = 0
mouthpieces = []  # list of mouthpiece dicts from API
current_page = 0  # for pagination


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
    console.print(f"[yellow]{banner}[/yellow]")
    if token == "":
        menu_content = (
            "[dim]Not logged in[/dim]\n\n"
            "[dim][1][/dim] My mouthpieces\n"
            "[green][6][/green] Log in\n"
            "[dim][7][/dim] Log out\n"
            "[green][8][/green] Add a user\n"
            "[green][0][/green] Exit to shell"
        )
    else:
        menu_content = (
            f"Logged in as [blue]{logemail}[/blue]\n\n"
            "[green][1][/green] My mouthpieces\n"
            "[dim][6][/dim] Log in\n"
            "[green][7][/green] Log out\n"
            "[dim][8][/dim] Add a user\n"
            "[green][0][/green] Exit to shell"
        )
    console.print(Panel(menu_content, title="Main Menu", border_style="blue"))
    print()


# My Mouthpieces Menu
def mympcsmenu():
    global mpcselect
    clear_screen()
    console.print(f"[yellow]{banner}[/yellow]")
    if mpcselect == 0:
        menu_content = (
            "[green][1][/green] Add mouthpiece      [green][3][/green] Edit mouthpiece\n"
            "[green][2][/green] Delete mouthpiece   [green][4][/green] View details\n"
            "[green][0][/green] Back to main menu"
        )
    else:
        menu_content = (
            "[dim][1][/dim] Add mouthpiece      [dim][3][/dim] Edit mouthpiece\n"
            "[dim][2][/dim] Delete mouthpiece   [dim][4][/dim] View details\n"
            "[dim][0][/dim] Back to main menu"
        )
    console.print(Panel(menu_content, title=f"Mouthpieces for [blue]{logemail}[/blue]", border_style="blue"))
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
    newmake = questionary.autocomplete(
        "Make:",
        choices=get_makes(),
        validate=validate_make,
        style=questionary.Style([("answer", "fg:green")])
    ).ask()
    if newmake is None:  # User pressed Ctrl+C
        mympcs(refresh=False)
        return
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
    newnote = input("Note (optional): ")
    print()
    summary = (
        f"[bold]Make:[/bold] [green]{newmake}[/green]\n"
        f"[bold]Model:[/bold] [green]{newmodel}[/green]\n"
        f"[bold]Type:[/bold] [green]{newtype}[/green]\n"
    )
    if newtype != "one-piece":
        summary += f"[bold]Threads:[/bold] [green]{newthreads}[/green]\n"
    summary += f"[bold]Finish:[/bold] [green]{newfinish}[/green]"
    if newnote:
        summary += f"\n[bold]Note:[/bold] [green]{newnote}[/green]"
    console.print(Panel(summary, title="New Mouthpiece", border_style="green"))
    print()
    while True:
        console.print("Send to Knack? [green](Y/n):[/green] ", end="")
        conf = input().lower()
        if conf == "" or conf == "y":
            conf = "y"
            break
        if conf == "n":
            break
        console.print("[red]Invalid Option[/red]")
        print()
    if conf == "y":
        api_url = "https://api.knack.com/v1/pages/scene_18/views/view_18/records"
        mouthpiece = {FIELD_MAKE: newmake, FIELD_TYPE: newtype, FIELD_MODEL: newmodel, FIELD_THREADS: newthreads, FIELD_FINISH: newfinish, FIELD_NOTE: newnote}
        headers = {"content-type":"application/json", "X-Knack-Application-Id": KNACK_APP_ID, "X-Knack-REST-API-KEY":"knack", "Authorization":token}
        response = requests.post(api_url, data=json.dumps(mouthpiece), headers=headers)
        print()
        if response.status_code == 200:
            input("Success! Press Enter to continue...")
            mympcs()
        else:
            console.print("[red]Error! There was a problem with your request.[/red] ", end="")
            input("Press Enter to continue...")
            mympcs(refresh=False)
    else:
        mpcselect = 0
        mympcs(refresh=False)


# My mouthpieces process
def mympcs(refresh=True):
    global mouthpieces, current_page
    if token == "":
        input("Please log in first. Press Enter...")
    else:
        if refresh:
            fetchmpcs()
            current_page = 0
        mympcsmenu()
        listmpcs()

        total_pages = (len(mouthpieces) + PAGE_SIZE - 1) // PAGE_SIZE if mouthpieces else 1

        while True:
            selection = input("Make a menu selection: ")

            # Handle pagination
            if selection == "<":
                if current_page > 0:
                    current_page -= 1
                mympcsmenu()
                listmpcs()
                continue
            elif selection == ">":
                if current_page < total_pages - 1:
                    current_page += 1
                mympcsmenu()
                listmpcs()
                continue

            try:
                selection = (int(selection))
                if selection not in (1, 2, 3, 4, 0):
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
        elif selection == 4:
            viewmpc()
        elif selection == 0:
            mainmenu()


# Fetch mouthpieces from API (separate from display)
def fetchmpcs():
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
            'Note': record.get(FIELD_NOTE, ''),
        })


# Generate collection stats
def get_stats():
    if not mouthpieces:
        return "No mouthpieces yet"

    total = len(mouthpieces)
    unique_makes = len(set(mpc['Make'] for mpc in mouthpieces))

    # Count by type
    type_counts = {}
    for mpc in mouthpieces:
        t = mpc['Type']
        type_counts[t] = type_counts.get(t, 0) + 1

    type_str = ", ".join(f"{count} {typ}" for typ, count in type_counts.items())

    return f"[bold]{total}[/bold] mouthpieces | [bold]{unique_makes}[/bold] makes | {type_str}"


# List mouthpieces process (with pagination)
def listmpcs():
    global current_page

    total = len(mouthpieces)
    total_pages = (total + PAGE_SIZE - 1) // PAGE_SIZE if total > 0 else 1

    # Ensure current_page is valid
    if current_page >= total_pages:
        current_page = total_pages - 1
    if current_page < 0:
        current_page = 0

    # Show stats
    console.print(Panel(get_stats(), title="Collection Stats", border_style="magenta"))
    print()

    # Build rich table for current page
    table = Table()
    table.add_column("Index", style="dim")
    table.add_column("Make")
    table.add_column("Model")
    table.add_column("Type")
    table.add_column("Threads")
    table.add_column("Finish")
    table.add_column("Note", justify="center")

    start_idx = current_page * PAGE_SIZE
    end_idx = min(start_idx + PAGE_SIZE, total)

    style = "green" if mpcselect == 1 else None
    for mpc in mouthpieces[start_idx:end_idx]:
        has_note = "X" if mpc['Note'] else ""
        # Hide threads for one-piece mouthpieces
        threads_display = "-" if mpc['Type'] == "one-piece" else mpc['Threads']
        table.add_row(
            str(mpc['index']),
            mpc['Make'],
            mpc['Model'],
            mpc['Type'],
            threads_display,
            mpc['Finish'],
            has_note,
            style=style
        )

    console.print(table)

    # Show pagination info if more than one page
    if total_pages > 1:
        console.print(f"\n[dim]Page {current_page + 1} of {total_pages} | [/dim][green][<][/green][dim] prev [/dim][green][>][/green][dim] next[/dim]")
    print()


# Delete mouthpiece process
def delmpc():
    if len(mouthpieces) == 1:
        print()
        console.print("[red]Add another mouthpiece to delete.[/red] You need at least one in place. ", end="")
        input("Press Enter to continue...")
        mympcs(refresh=False)
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
            console.print(f"[red]Are you sure you want to delete this[/red] {mpc['Make']} {mpc['Model']}? [green](y/N):[/green] ", end="")
            conf = input().lower()
            if conf == "" or conf == "n":
                conf = "n"
                break
            if conf == "y":
                break
            console.print("[red]Invalid Option[/red]")
            print()
        if conf == "y":
            delid = mpc['id']
            api_url = "https://api.knack.com/v1/pages/scene_18/views/view_18/records/" + delid
            headers = {"content-type":"application/json", "X-Knack-Application-Id": KNACK_APP_ID, "X-Knack-REST-API-KEY":"knack", "Authorization":token}
            response = requests.delete(api_url, headers=headers)
            print()
            if response.status_code == 200:
                input("Success! Press Enter to continue...")
                mpcselect = 0
                mympcs()  # refresh=True to show updated list
            else:
                console.print("[red]Error! There was a problem with your request.[/red] ", end="")
                input("Press Enter to continue...")
                mpcselect = 0
                mympcs(refresh=False)
        else:
            mpcselect = 0
            mympcs(refresh=False)


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
    console.print("[dim]Press Enter to keep current value (for Make: start typing or press Enter)[/dim]")
    print()

    # Make (Enter keeps current, autocomplete from list)
    newmake = questionary.autocomplete(
        "Make:",
        choices=get_makes(),
        default=mpc['Make'],
        validate=validate_make,
        style=questionary.Style([("answer", "fg:green")])
    ).ask()
    if newmake is None:  # User pressed Ctrl+C
        mpcselect = 0
        mympcs(refresh=False)
        return
    print()

    # Model (Enter keeps current)
    newmodel = input(f"Model ({mpc['Model']}): ") or mpc['Model']

    # Type (Enter keeps current)
    type_map = {"one-piece": 1, "two-piece": 2, "cup": 3, "rim": 4}
    type_reverse = {1: "one-piece", 2: "two-piece", 3: "cup", 4: "rim"}
    mpctypemenu()
    while True:
        option = input(f"Type ({mpc['Type']}): ")
        if option == "":
            newtype = mpc['Type']
            break
        try:
            option = int(option)
            if option not in (1, 2, 3, 4):
                raise ValueError
            newtype = type_reverse[option]
            break
        except ValueError:
            console.print("[red]Invalid Option[/red]")
            print()

    # Threads (Enter keeps current, only for non one-piece)
    newthreads = ""
    if newtype != "one-piece":
        threads_reverse = {"1": "standard", "2": "metric", "3": "other"}
        mpcthreadsmenu()
        while True:
            option = input(f"Threads ({mpc['Threads']}): ")
            if option == "":
                newthreads = mpc['Threads']
                break
            if option in ("1", "2", "3"):
                newthreads = threads_reverse[option]
                break
            console.print("[red]Invalid Option[/red]")
            print()

    # Finish (Enter keeps current)
    finish_reverse = {1: "silver plated", 2: "gold plated", 3: "brass", 4: "nickel", 5: "stainless", 6: "bronze", 7: "plastic"}
    mpcfinishmenu()
    while True:
        option = input(f"Finish ({mpc['Finish']}): ")
        if option == "":
            newfinish = mpc['Finish']
            break
        try:
            option = int(option)
            if option not in (1, 2, 3, 4, 5, 6, 7):
                raise ValueError
            newfinish = finish_reverse[option]
            break
        except ValueError:
            console.print("[red]Invalid Option[/red]")
            print()

    # Note (Enter keeps current)
    print()
    current_note_display = mpc['Note'][:30] + "..." if len(mpc['Note']) > 30 else mpc['Note']
    newnote = input(f"Note ({current_note_display}): ") or mpc['Note']

    print()
    old_summary = (
        f"[bold]Make:[/bold] [red]{mpc['Make']}[/red]\n"
        f"[bold]Model:[/bold] [red]{mpc['Model']}[/red]\n"
        f"[bold]Type:[/bold] [red]{mpc['Type']}[/red]\n"
    )
    if mpc['Type'] != "one-piece":
        old_summary += f"[bold]Threads:[/bold] [red]{mpc['Threads']}[/red]\n"
    old_summary += f"[bold]Finish:[/bold] [red]{mpc['Finish']}[/red]"
    if mpc['Note']:
        old_summary += f"\n[bold]Note:[/bold] [red]{mpc['Note']}[/red]"
    console.print(Panel(old_summary, title="OLD", border_style="red"))

    print()
    new_summary = (
        f"[bold]Make:[/bold] [green]{newmake}[/green]\n"
        f"[bold]Model:[/bold] [green]{newmodel}[/green]\n"
        f"[bold]Type:[/bold] [green]{newtype}[/green]\n"
    )
    if newtype != "one-piece":
        new_summary += f"[bold]Threads:[/bold] [green]{newthreads}[/green]\n"
    new_summary += f"[bold]Finish:[/bold] [green]{newfinish}[/green]"
    if newnote:
        new_summary += f"\n[bold]Note:[/bold] [green]{newnote}[/green]"
    console.print(Panel(new_summary, title="NEW", border_style="green"))

    print()
    while True:
        console.print("Save changes? [green](Y/n):[/green] ", end="")
        conf = input().lower()
        if conf == "" or conf == "y":
            conf = "y"
            break
        if conf == "n":
            break
        console.print("[red]Invalid Option[/red]")
        print()
    if conf == "y":
        editid = mpc['id']
        api_url = "https://api.knack.com/v1/pages/scene_18/views/view_18/records/" + editid
        mouthpiece = {FIELD_MAKE: newmake, FIELD_TYPE: newtype, FIELD_MODEL: newmodel, FIELD_THREADS: newthreads, FIELD_FINISH: newfinish, FIELD_NOTE: newnote}
        headers = {"content-type":"application/json", "X-Knack-Application-Id": KNACK_APP_ID, "X-Knack-REST-API-KEY":"knack", "Authorization":token}
        response = requests.put(api_url, data=json.dumps(mouthpiece), headers=headers)
        print()
        if response.status_code == 200:
            input("Success! Press Enter to continue...")
            mpcselect = 0
            mympcs()  # refresh=True to show updated list
        else:
            console.print("[red]Error! There was a problem with your request.[/red] ", end="")
            input("Press Enter to continue...")
            mpcselect = 0
            mympcs(refresh=False)
    else:
        mpcselect = 0
        mympcs(refresh=False)

# View mouthpiece details
def viewmpc():
    global mpcselect
    mpcselect = 1
    mympcsmenu()
    listmpcs()
    print("Make a menu selection: 4")
    print()
    while True:
        selection = input("Select a mouthpiece by Index to view: ")
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
    details = (
        f"[bold]Make:[/bold]    [cyan]{mpc['Make']}[/cyan]\n"
        f"[bold]Model:[/bold]   [cyan]{mpc['Model']}[/cyan]\n"
        f"[bold]Type:[/bold]    [cyan]{mpc['Type']}[/cyan]\n"
    )
    if mpc['Type'] != "one-piece":
        details += f"[bold]Threads:[/bold] [cyan]{mpc['Threads']}[/cyan]\n"
    details += f"[bold]Finish:[/bold]  [cyan]{mpc['Finish']}[/cyan]"

    if mpc['Note']:
        details += f"\n\n[bold]Note:[/bold]\n[yellow]{mpc['Note']}[/yellow]"
    else:
        details += "\n\n[bold]Note:[/bold]\n[dim]No note[/dim]"

    console.print(Panel(details, title="Mouthpiece Details", border_style="cyan"))
    print()
    input("Press Enter to continue...")
    mpcselect = 0
    mympcs(refresh=False)


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
