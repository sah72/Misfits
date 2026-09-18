#By Stephanie Harber
from flask import Flask, render_template,redirect, url_for,flash, request, jsonify
from dataclasses import dataclass
from flask import current_app, g, session
from werkzeug.utils import secure_filename
from pathlib import Path
from dotenv import load_dotenv
from functools import wraps
from flask_wtf.csrf import CSRFProtect
from datetime import datetime,timezone
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, Identity

from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename

from werkzeug.security import check_password_hash


from flask_login import (
    LoginManager,
    UserMixin,
    login_user,
    logout_user,
    login_required,
    current_user
)

from werkzeug.security import generate_password_hash, check_password_hash
from flask import request, redirect, url_for, flash, abort
from PIL import Image, UnidentifiedImageError

#Installation
# python -m venv venv
#source /venv/Scripts/activate
#pip install flask
#pip install psycopg2-binary
#pip install flask-sqlalchemy
#pip install flask-login
#pip install python-dotenv
#pip install Flask-WTF
#pip install Pillow

# Load environment variables from the project root.
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

app = Flask(__name__,
            template_folder="../templates",
            static_folder="../static",
            static_url_path=""
)


app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]

app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

#Constants
DEFAULT_TEAM_LOGO = "/images/TBD.png"
UPLOAD_FOLDER = os.path.join(
    "static",
    "/images")

#Login info
login_manager = LoginManager()
login_manager.init_app(app)

login_manager.login_view = "login"
app.config["SECRET_KEY"] = "your-secret-key"

#Define the Calendar table.
@dataclass
class Calendar(db.Model):
    __tablename__ ='Calendar'

    #Declare fields
    opp_logo:str
    game_type:str
    game_id:int
    title: str
    location: str  
    notes: str
    score_team: int
    score_opponent:int
    location_link:str
    Status:str
    opponent:str
    Result:str
    Time_: str
    home_away:str
    season_id: int

    season_id = db.Column(db.Integer())
    home_away= db.Column(db.String())
    game_type = db.Column(db.String(25))
    game_id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    notes = db.Column( db.String())
    opponent = db.Column(db.String())
    score_team = db.Column(db.Integer())
    score_opponent = db.Column(db.Integer())
    location_link = db.Column(db.String())
    Status = db.Column(db.String())
    date = db.Column(db.Date(), nullable=False)
    Time_= db.Column("Time_",db.Time(), nullable=False)
    title = db.Column( db.String() )
    location = db.Column( db.String() ) 
    opp_logo = db.Column( db.String())
    game_id = db.Column( db.Integer(), primary_key=True ) 
    Result = db.Column( db.String() ) 

    def to_dict(self):
        return {
            "game_id": self.game_id,
            "date": self.date.strftime("%B %d, %Y"),
            "oppo": self.opponent,
            "loc": self.location,
            "time_": self.Time_.strftime("%I:%M %p"),
            "result": self.Result or "",
            "status": self.Status,
            "oppo_logo":self.opp_logo
        }

#Define the Standings table
@dataclass
class Standings(db.Model):
    __tablename__ ='Standings'

    #Declare fields
    Team: str
    Wins: int  
    Team_id: int
    Loss: int
    Ties: int
    Points:int
    Points_Percent:float
    Games_Played:int
    Goals_For:int
    Goals_Against:int
    OT_Loss:int
    Pim:int
    Badges:str
    logo:str
    season_id:int
    standings_id :int


    standings_id = db.Column( db.Integer(),
        Identity(),
        primary_key=True)
    Team_id = db.Column(db.Integer, nullable=False)

    season_id = db.Column(db.Integer())
    Team = db.Column(db.String())
    logo = db.Column(db.String())
    Badges = db.Column(db.String())
    Wins= db.Column(db.Integer())  
    Team_id= db.Column(db.Integer(), primary_key=True )
    Loss= db.Column(db.Integer())
    Ties= db.Column(db.Integer())
    Points= db.Column(db.Integer())
    Points_Percent= db.Column(db.Integer())
    Games_Played= db.Column(db.Integer())
    Goals_For= db.Column(db.Integer())
    Goals_Against = db.Column(db.Integer())
    OT_Loss= db.Column(db.Integer())
    Pim = db.Column(db.Integer())
    
#Define the seaons table
@dataclass
class seasons(db.Model):
    __tablename__ ='seasons'

    #Declare fields
    id: int
    name: str
    is_active: bool
       
    
    id = db.Column(db.Integer(),primary_key=True)
    name = db.Column(db.String())
    is_active = db.Column(db.Boolean())
    start_date = db.Column(db.Date())
    end_date = db.Column(db.Date())

#Define the Roster table
@dataclass
class Roster(db.Model):
    __tablename__ ='Roster'

    #Declare fields
    First_Name: str
    Last_Name: str 
    Position: str
    Games_Played: int
    Points: int
    Number:int
    Goals:int
    Assists:int
    PIM:int
    Shutouts:int
    Wins: int
    Loss: int
    season_id:int
    player_id:int

    player_id = db.Column(db.Integer())
    season_id = db.Column(db.Integer())    
    First_Name= db.Column(db.String(), primary_key=True)
    Last_Name= db.Column(db.String())
    Position= db.Column(db.String())
    Games_Played=db.Column(db.Integer())
    Points = db.Column(db.Integer())
    Number = db.Column(db.Integer())
    Goals = db.Column(db.Integer())
    Assists = db.Column(db.Integer())
    PIM = db.Column(db.Integer())
    Shutouts = db.Column(db.Integer())
    Wins = db.Column(db.Integer())
    Loss = db.Column(db.Integer())

#Define the User table
@dataclass
class User(UserMixin, db.Model):
    __tablename__ ='User'

    id: int
    username: str
    password_hash:str
    is_admin: bool

    id = db.Column(db.Integer(), primary_key=True)
    username = db.Column(db.String())
    password_hash= db.Column(db.String())
    is_admin = db.Column(db.Boolean, default=False)

#Admin access
def admin_required(view):
    @wraps(view)
    @login_required
    def wrapped(*args, **kwargs):
        if not current_user.is_admin:
            abort(403)

        return view(*args, **kwargs)

    return wrapped



#Converts a date_time to a readable date(Ex. April 28 2026 8pm).
def convert_date_(date_, time_):
    result=""

    if ((date_ is not None) & (time_ is not None)):
        read_date_ = date_.strftime("%B %d %Y")
        read_time = time_.strftime("%I:%M %p EDT").lstrip("0")
        readable = read_time.replace(" 0", " ")  
        result = read_date_ +" "+ readable

    elif(date_ is not None):
        result = date_.strftime("%B %d %Y").lstrip("0")
    else:
        read_time = time_.strftime("%I:%M %p EDT").lstrip("0")
        readable = read_time.replace(" 0", " ")  
        result = readable

    return result


#Function to get the next game information
def get_next_game(games):
    next_game=""
    #When future games exists
    if isinstance(games, Calendar):
        curr_game=games
        fordate_ =convert_date_(curr_game.date, None)
        g_time =convert_date_(None,curr_game.Time_)
        next_game ={"game_id":curr_game.game_id,"oppon":curr_game.opponent, "date":fordate_, "og_date":curr_game.date,
                    "time_":curr_game.Time_.strftime("%I:%M").lstrip("0"),
                    "loc":curr_game.location,"loc_link":curr_game.location_link, 'status':curr_game.Status,
                   "oppo_logo":curr_game.opp_logo, "game_type":curr_game.game_type}

        #Update the status of a completed game.
        if curr_game.Status =="Final":
            next_game['result']= curr_game.Result
            next_game['oppo_score']= curr_game.score_opponent
            next_game['team_score'] = curr_game.score_team


        return next_game


    elif games:
        curr_game = games[0]

        g_time =convert_date_(None,curr_game.Time_)

        fordate_ =convert_date_(curr_game.date, curr_game.Time_)
        next_game ={"game_id":curr_game.game_id,"oppon":curr_game.opponent, "date":fordate_, 
                    "time_":curr_game.Time_.strftime("%I:%M").lstrip("0"),
                    "loc":curr_game.location,"loc_link":curr_game.location_link,
                   "oppo_logo":curr_game.opp_logo}
    
    #No future games exists
    else:
        next_game ={"oppon":"TBD", "date_":"TBD"
                   ,"loc":"TBD"}
    return next_game

#Returns the team record W-L-T
def get_records(team):
    record = db.session.query(Standings).where(Standings.Team==team,
                                                Standings.season_id==get_selected_season_id()).first()
    return record

#Login retrieve the user
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

#Login Route
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password_hash, password):

            login_user(user)
            next_page = request.args.get("next")

            if next_page and next_page.startswith("/"):
                return redirect(next_page)

            return redirect(url_for("login"))

        flash("Invalid username or password. Please try again.","error")
        return redirect(url_for("login"))

    #Get method called
    season_id = get_selected_season_id()

    roster_count = (
        db.session.query(func.count(Roster.player_id))
        .filter(Roster.season_id == season_id)
        .scalar()
    )

    misfits = (
        db.session.query(Standings)
        .filter(
            Standings.season_id == season_id,
            Standings.Team == "Misfits"
        )
        .first()
    )

    points = misfits.Points if misfits else 0


    return render_template(
        "login.html",
        roster_count=roster_count,
        points=points
    )

#Logout
@app.route("/logout")
@login_required
def logout():

    logout_user()

    return redirect(url_for("login"))



#Admin Route
@app.route("/admin")
@admin_required
def admin():

    if not current_user.is_admin:
        abort(403)

    return render_template("admin.html")

#Manage Games
@app.route("/manage_games")
@admin_required
def manage_games():
    all_games = ( db.session.query(Calendar).where(Calendar.season_id==get_selected_season_id())
                      .order_by(Calendar.date.asc()).all())

    all_teams = (db.session.query(Standings.Team)
                 .where(Standings.season_id==get_selected_season_id()).all())

    edit_id = request.args.get("edit", type=int)
    add_mode = request.args.get("add", type=int)

    selected_game = None

    if edit_id:
        selected_game = db.session.get(Calendar, edit_id)

    return render_template(
        "manage_games.html",
        games=all_games,
        selected_game=selected_game,
        add_mode=add_mode,
        teams= all_teams)

def get_opponent_logo(opponent, season_id):

    logo = (
        db.session.query(Standings.logo)
        .filter(
            Standings.Team == opponent,
            Standings.season_id == season_id
        )
        .limit(1)
        .scalar()
    )

    return logo or DEFAULT_TEAM_LOGO

con_location = "https://www.google.com/maps/place/Iceland+Mississauga/@43.6284022,-79.651944,16z/data=!3m2!4b1!5s0x882b38aadc9b364f:0xad4abf39fc057b18!4m6!3m5!1s0x882b38c00669de1b:0xf10cb79c1916ac61!8m2!3d43.6283983!4d-79.6493691!16s%2Fm%2F03ctgd2?entry=ttu&g_ep=EgoyMDI2MDQyMi4wIKXMDSoASAFQAw%3D%3D"
winter_loc ="https://www.google.com/maps/place/Sixteen+Mile+Sports+Complex/@43.4657261,-79.7521046,633m/data=!3m2!1e3!4b1!4m6!3m5!1s0x882b67f248a8a967:0x9a3d032afe1d5170!8m2!3d43.4657222!4d-79.7495297!16s%2Fg%2F1tj4c3jf?entry=ttu&g_ep=EgoyMDI2MDkxNC4wIKXMDSoASAFQAw%3D%3D"
#Manage (admin) - Add a game
@app.route("/manage_games/add", methods=["POST"])
@admin_required
def add_game():
    title ="Misfits VS "+request.form["opponent"]

    season_id = get_selected_season_id()
    opp_logo = get_opponent_logo(request.form["opponent"], season_id)
    max_id = db.session.query(func.max(Calendar.game_id)).scalar()

    next_id = (max_id or 0) + 1

    google_loc =""
    if season_id ==1:
        google_loc=con_location
    else:
        google_loc=winter_loc

    new_game = Calendar(date=request.form["date"], title= title,
                        opponent=request.form["opponent"],
                        location=request.form["location"],
                        notes="blank",
                        home_away="Home",
                        Time_=request.form["time"],
                        score_team=0,
                        score_opponent=0,
                        location_link=google_loc,
                        Status="Scheduled",
                        Result="TBD",
                        opp_logo=opp_logo,
                        game_id=next_id,
                        game_type=request.form["game-type"],
                        season_id =season_id
  
    )

    db.session.add(new_game)
    db.session.commit()

    return redirect(url_for("manage_games"))


#Save/update the game based on the form.
@app.route("/manage_games/<int:game_id>/edit", methods=["POST"])
@admin_required
def edit_game(game_id):

    game = db.session.query(Calendar).filter(Calendar.game_id == game_id,
                                             Calendar.season_id == get_selected_season_id()).first_or_404()

    if game is None:
        abort(404)

    game.date = datetime.strptime(
        request.form["game-date"],
        "%Y-%m-%d"
    ).date()

    game.Time_ = datetime.strptime(
        request.form["game-time"],
        "%H:%M"
    ).time()

    game.opponent = request.form["opponent"]
    game.location = request.form["location"]
    game.game_type = request.form["game-type"]

    game.score_team = int(request.form["score-team"])
    game.score_opponent = int(request.form["opponent-score"])

    game.Result = request.form["result"]
    if game.Result!="TBD":
        game.Status="Final"
    else:
        game.Status="Scheduled"

    #Get opponent logo
    game.opp_logo = get_opponent_logo( game.opponent, game.season_id)  

    db.session.commit()

    return redirect(url_for("manage_games"))

#Manage (admin) - delete game
@app.route("/admin/games/<int:game_id>/delete", methods=["POST"])
@admin_required
def delete_game(game_id):

    game = db.session.query(Calendar).filter(Calendar.game_id == game_id,
                                             Calendar.season_id == get_selected_season_id()).first_or_404()
    

    if game is None:
        abort(404)

    db.session.delete(game)
    db.session.commit()

    return redirect(url_for("manage_games"))

#Gets the standings
def get_standings_(season_id):
    return (
        db.session.query(Standings)
        .where(Standings.season_id == season_id)
        .order_by(Standings.Points.desc())
        .all()
    )

#Gets the next ID for the team_id
def get_next_team_id(season_id):

    max_team_id = (
        db.session.query(db.func.max(Standings.Team_id))
        .filter(Standings.season_id == season_id)
        .scalar()
    )

    return (max_team_id or 0) + 1

def save_team_logo(file_):

    logo = request.files.get(file_)

    # No file uploaded: use the default.
    if not logo or not logo.filename:
        return DEFAULT_TEAM_LOGO

    # Restrict filenames to supported extensions.
    allowed_extensions = {".png", ".jpg", ".jpeg", ".webp"}

    extension = Path(logo.filename).suffix.lower()

    if extension not in allowed_extensions:
        raise ValueError("Please upload a PNG, JPG, or WebP image.")

    try:
        with Image.open(logo.stream) as image:

            # Verify actual image content.
            if image.format not in {"PNG", "JPEG", "WEBP"}:
                abort(400, description="Unsupported image.")

            # Limit image dimensions.
            if image.width > 3000 or image.height > 3000:
                abort(400, description="Image dimensions too large.")

            image.load()

            # Normalize the output to PNG.
            processed_image = image.convert("RGBA")

    except (
        UnidentifiedImageError,
        Image.DecompressionBombError,
        OSError
    ):
        abort(400, description="Invalid image file.")

    # Generate our own filename.
    filename = f"{uuid.uuid4().hex}.png"

    upload_folder = Path(current_app.static_folder) / "images"

    upload_folder.mkdir(
        parents=True,
        exist_ok=True
    )

    save_path = upload_folder / filename

    processed_image.save(save_path, format="PNG")

    return f"images/{filename}"


# def save_team_logo(file_):

#     logo = request.files.get(file_)

#     # No image selected
#     if not logo or logo.filename == "":
#         return DEFAULT_TEAM_LOGO

#     filename = secure_filename(logo.filename)

#     # Make filename unique
#     unique_filename = f"{uuid.uuid4().hex}_{filename}"

#      # Get Flask's actual static folder
#     upload_folder = (
#         Path(current_app.static_folder)
#         / "images"
        
#     )

#     # Create folder if it doesn't exist
#     upload_folder.mkdir(
#         parents=True,
#         exist_ok=True
#     )

#     save_path = upload_folder / unique_filename

#     logo.save(save_path)

#     # Store this in PostgreSQL
#     return f"images/{unique_filename}"

#Adds the new team from the form in manage_standings.html.
def add_team(season_id):
    team_name = request.form.get("team_name", "").strip()

    wins = request.form.get("wins", type=int) or 0
    losses = request.form.get("losses", type=int) or 0
    ot_losses = request.form.get("ot_losses", type=int) or 0
    ties = request.form.get("ties", type=int) or 0
    points = request.form.get("points", type=int) or 0

    team_id = get_next_team_id(season_id)
    team_logo = save_team_logo("team_logo")
    

    new_team = Standings(
        Team_id=team_id,
        season_id=season_id,
        Games_Played=0,
        Goals_For=0,
        Goals_Against=0,
        Pim=0,
        Team=team_name,
        Wins=wins,
        Loss=losses,
        Ties=ties,
        OT_Loss=ot_losses,
        Points=points,
        logo=team_logo,
        Badges=team_name[0]
    )

    db.session.add(new_team)
    db.session.commit()

#Get the team based on the season_id and standings_id
def get_team(standings_id, season_id):

    if not standings_id:
        return None

    return (
        db.session.query(Standings)
        .where(
            Standings.standings_id == standings_id,
            Standings.season_id == season_id
        )
        .first()
    )

def update_standings_(standings):
    for team in standings:

        team.Wins = request.form.get(
            f"wins_{team.standings_id}",
            type=int
        ) or 0

        team.Games_Played = request.form.get(
            f"gp_{team.standings_id}",
            type=int
        ) or 0
        

        team.Loss = request.form.get(
            f"losses_{team.standings_id}",
            type=int
        ) or 0

        team.Ties = request.form.get(
                    f"ties_{team.standings_id}",
                    type=int
                ) or 0

        team.OT_Loss = request.form.get(
            f"ot_losses_{team.standings_id}",
            type=int
        ) or 0

        team.Goals_For = request.form.get(
            f"goals_for_{team.standings_id}",
            type=int
        ) or 0

        team.Goals_Against = request.form.get(
                    f"goals_against_{team.standings_id}",
                    type=int
                ) or 0

        team.Pim= request.form.get(
                    f"pim_{team.standings_id}",
                    type=int
                ) or 0

        team.Points = request.form.get(
            f"points_{team.standings_id}",
            type=int
        ) or 0

    db.session.commit()

#Manage Standings route
@app.route("/manage_standings", methods=["GET","POST"])
@login_required
def manage_standings():
    season_id = get_selected_season_id()

    standings = get_standings_(season_id)

    add_team_mode = request.args.get("add") == "1"

    if request.method == "POST":

        if add_team_mode:
            add_team(season_id)

            flash("Team added successfully.", "success")

        else:
            update_standings_(standings)

            flash("Standings updated successfully.", "success")

        return redirect(url_for("manage_standings"))

    edit_team =None
    edit_id = request.args.get("edit", type=int)

    if edit_id:
        edit_team = get_team(edit_id, season_id)

    return render_template(
        "manage_standings.html",
        standings=standings,
        edit_team=edit_team,
        add_team_mode=add_team_mode
    )

#Helper function to remove picture from the location
def delete_team_logo(logo_path):

    # No logo stored
    if not logo_path:
        return

    # Don't delete the shared default image
    if logo_path == DEFAULT_TEAM_LOGO:
        return

    # Remove leading slash if one exists
    clean_path = logo_path.lstrip("/")

    full_path = (
        Path(current_app.static_folder)
        / clean_path
    )

    # Only delete if the file actually exists
    if full_path.exists():
        full_path.unlink()

#Admin to delete team from standings
@app.route("/delete_team/<int:standings_id>", methods=["POST"])
@admin_required
def delete_team(standings_id):
   
    season_id = get_selected_season_id()

    team = (
        db.session.query(Standings)
        .where(
            Standings.standings_id == standings_id,
            Standings.season_id == season_id
        )
        .first()
    )
    # Save the logo location before deleting the database row
    logo_path = team.logo

    if not team:
        flash("Team could not be found.", "error")
        return redirect(url_for("manage_standings"))

    db.session.delete(team)
    db.session.commit()

    # Remove uploaded logo from static/images
    delete_team_logo(logo_path)

    flash("Team deleted successfully.", "success")

    return redirect(url_for("manage_standings"))

#Edit/update the standings.
@app.route(
    "/edit_team/<int:standings_id>",
    methods=["POST"]
)
@admin_required
def edit_team(standings_id):

    season_id = get_selected_season_id()

    #Get the team from the bd
    team = get_team(standings_id, season_id)

    if not team:
        flash("Team could not be found.", "error")
        return redirect(url_for("manage_standings"))

    team_name = request.form.get(
        "team_name",
        ""
    ).strip()

    if not team_name:
        flash("Team name is required.", "error")

        return redirect(
            url_for(
                "manage_standings",
                edit=standings_id
            )
        )

    team.Team = team_name

    team.Games_Played = (
        request.form.get("gp", type=int)
        or 0
    )
    team.Ties = (
            request.form.get("ties", type=int)
            or 0
        )

    team.Wins = (
        request.form.get("wins", type=int)
        or 0
    )

    team.Loss = (
        request.form.get("losses", type=int)
        or 0
    )

    team.OT_Loss = (
        request.form.get("ot_losses", type=int)
        or 0
    )
    team.Goals_For = (
            request.form.get("goals_for", type=int)
            or 0
        )
    team.Goals_Against= (
            request.form.get("goals_against", type=int)
            or 0
        )
    team.Pim = (
            request.form.get("pim", type=int)
            or 0
        )

    team.Points = (
        request.form.get("points", type=int)
        or 0
    )
    # Check whether a NEW logo was selected
    logo = request.files.get("team_logo_")

    if logo and logo.filename:
        team.logo = save_team_logo("team_logo_")

    db.session.commit()

    flash("Team updated successfully.", "success")

    return redirect(
        url_for("manage_standings")
    )


#Admin edit the standings
@app.route(
    "/admin/manage-standings/edit/<int:standings_id>",
    methods=["POST"]
)
@admin_required
def edit_team__(standings_id):

    season_id = get_selected_season_id()

    team = (
        db.session.query(Standings)
        .where(
            Standings.standings_id == standings_id,
            Standings.season_id == season_id
        )
        .first_or_404()
    )

    team.Team = request.form.get("team_name")

    db.session.commit()

    flash("Team updated successfully.", "success")

    return redirect(
        url_for("manage_standings")
    )


#Helper function to get season details
def get_season_data():

    today = datetime.today()

    all_seasons = db.session.scalars(
        select(seasons)
        .order_by(seasons.start_date.desc())
    ).all()

    # Season selected by user
    selected_id = session.get("season_id")

    selected_season = next(
        (
            season
            for season in all_seasons
            if season.id == selected_id
        ),
        None
    )

    # No user selection yet
    if selected_season is None:

        selected_season = next(
            (
                season
                for season in all_seasons
                if season.start_date.date()
                <= today
                <= season.end_date.date()
            ),
            None
        )

    # Between seasons -> most recent
    if selected_season is None:

        selected_season = next(
            (
                season
                for season in all_seasons
                if season.start_date.date() <= today
            ),
            None
        )

    return all_seasons, selected_season


#Load the season per request
@app.before_request
def load_season():
    today = datetime.today()

    # One query for all seasons
    all_seasons = db.session.scalars(
        select(seasons)
        .order_by(seasons.start_date.desc())
    ).all()

    # Find the actual current season
    current_season = next(
        (
            season
            for season in all_seasons
            if season.start_date <= today.date() <= season.end_date
        ),
        None
    )

    # If between seasons, use most recent completed/started season
    if current_season is None:
        current_season = next(
            (
                season
                for season in all_seasons
                if season.start_date <= today.date()
            ),
            None
        )

    # See whether the user previously selected another season
    selected_season = next(
        (
            season
            for season in all_seasons
            if season.id == session.get("season_id")
        ),
        None
    )

    # Default to current season
    if selected_season is None:
        selected_season = current_season

        # Fallback when every season is in the future.
        if selected_season is None and all_seasons:
            selected_season = all_seasons[0]

    g.all_seasons = all_seasons
    g.current_season = current_season
    g.selected_season = selected_season


#Returns seasons details
@app.context_processor
def season_context():
    return {
        "all_seasons": g.all_seasons,
        "current_season": g.current_season,
        "selected_season": g.selected_season
    }

#When the user changes seasons.
@app.route("/change-season/<int:season_id>")
def change_season(season_id):
    season = db.session.get(seasons, season_id)

    if season is None:
        abort(404)

    session["season_id"] = season.id

    next_page = request.args.get("next")

    if next_page and next_page.startswith("/"):
        return redirect(next_page)

    return redirect(url_for("schedule"))

#Home page decorator.
@app.route('/')
def home():
    
    #Get the most recent game based on timestamp.
    now = datetime.today().date()
    games = ( db.session.query(Calendar)
                  .filter(Calendar.date >= now, Calendar.season_id==get_selected_season_id())
                  .order_by(Calendar.date.asc()).limit(1).all())
 
    #Gets the next game details.
    next_game = get_next_game(games)

    #Get the current season
    all_seasons = db.session.scalars(select(seasons).order_by(seasons.start_date)).all()

    season_names = [season.name for season in all_seasons]

    current_season = next(
    (
        season for season in all_seasons
        if season.start_date <= now <= season.end_date
    ),
    None
)

    if current_season is None:
        current_season = next(
        (
            season for season in all_seasons
            if season.start_date <= now
        ),
        None
    )

    return render_template('index.html', page=next_game)

#Returns the season id (PK for databases)
def get_selected_season_id():

    if g.selected_season is None:
        return None
    return g.selected_season.id

#Gets the five latest game details.
@app.get("/api/get_first_five")
def get_first_five():
    now = datetime.today()

    games = ( db.session.query(Calendar)
                  .filter(Calendar.date >= now, Calendar.season_id==get_selected_season_id())
                  .order_by(Calendar.date.asc()).limit(5).all())
    five=[]
    for item in games:
                
        # Format date: Sep 22
        short_date = f"{item.date.strftime('%b')} {item.date.day}"
                      
        # Format time: 10:15 PM
        short_time = item.Time_.strftime("%I:%M %p").lstrip("0")        
        
        # Combine both
        date_time = f"{short_date} · {short_time}"
   
        next_game ={"oppon":item.opponent, "id":item.game_id,'short':date_time,
                    "logo":item.opp_logo,'loc':item.location}
        five.append(next_game)
   
    return jsonify({"games":five})


#Function to get the Misfits last few games streak.
def get_streak():
    #Get all the past games
    results = db.session.query(Calendar.Result, Calendar.date).filter(Calendar.date <datetime.today(), 
                                                                      Calendar.season_id==get_selected_season_id()).order_by(Calendar.date.desc()).all()

    counter = 0
    if len(results)>0:
        first_result =results[0]
               
        #Loop through the previous games and stop when the result is different.
        for status in results:
            if first_result.Result == status.Result:
                counter+=1
            else:
                return {"result":first_result.Result,"count":counter}

        return {"result":first_result.Result,"count":counter}
    return {"result":"","count":counter}

@app.get('/api/get_standings')
def get_standings():
    stand = (db.session.query(Standings)
             .where(Standings.season_id==get_selected_season_id())
             .order_by(Standings.Points.desc()).limit(4)).all()
        
    return jsonify({"standings": stand})
##End of routes for index page

###Routes for schedule page
@app.route('/schedule')
def schedule():
     now = datetime.today().date()

     games = ( db.session.query(Calendar)
                  .filter(Calendar.date >= now, Calendar.season_id==get_selected_season_id())
                  .order_by(Calendar.date.asc()).limit(1).all())
    
    #Gets the next game details.
     next_game = get_next_game(games)
     return render_template("schedule.html", page=next_game)


def get_final(game_info):
    if game_info.Result.startswith("L"):
        return f"L {game_info.score_team} - {game_info.score_opponent}"
    elif game_info.Result.startswith("W"):
        return f"W {game_info.score_team} - {game_info.score_opponent}"
    elif game_info.Result.startswith("TB"):
        return "TBD"
    else: 
        return f"T {game_info.score_team} - {game_info.score_opponent}"
    

#Get the Team's schedule
@app.get('/get_schedule')
def get_schedule():

    season_id = get_selected_season_id()

    #Get the sort date order and query the Calendar for all games
    sort_order = request.args.get("order", "desc")
    schedule_ = (db.session.query(Calendar).where(Calendar.season_id == season_id))

    if sort_order =="asc":
        schedule_ = schedule_.order_by(Calendar.date.desc())
    else:
        schedule_ = schedule_.order_by(Calendar.date.asc())

    all_schedule = schedule_.all()   
    all_games =[]

    for game in all_schedule:
        forDate = convert_date_(game.date, None)
        forTime = convert_date_(None,game.Time_)

        # Format date: Sep 22
        short_date = f"{game.date.strftime('%b')} {game.date.day}"

# Format time: 10:15 PM
        short_time = game.Time_.strftime("%I:%M %p").lstrip("0")

# Combine both
        date_time = f"{short_date} · {short_time}"

        score_result="-"
        if game.Result:
            score_result= get_final(game)


        game_info = {'id':game.game_id,'date':forDate, 'oppon':game.opponent, 'loc':game.location,
                     'time':forTime,'result':score_result,'stat':game.Status,'date':forDate, 'logo':game.opp_logo}
        all_games.append(game_info)
    
    return jsonify({'schedule': all_games})

@app.get('/get_nextGame')
def get_Nextgame():
    now = datetime.today().date()

    games = ( db.session.query(Calendar)
                  .filter(Calendar.date >= now)
                  .order_by(Calendar.date.asc()).limit(1).all())
    
    #Gets the next game details.
    next_game = get_next_game(games)

    return jsonify({'page': next_game})
    
##End of schedule page routes

#Change the date from numeric to actual
app.jinja_env.filters["convert_date"] = convert_date_

def get_leaders():
    roster = db.session.query(Roster).where(Roster.season_id==get_selected_season_id()).all()  

    if roster:
        leaders = {
            "points": max(roster, key=lambda p: p.Points or 0),
            "assists": max(roster, key=lambda p: p.Assists or 0),
            "goals": max(roster, key=lambda p: p.Goals or 0),
            "shutoouts": max(roster, key=lambda p: p.Shutouts or 0)
        }
        leader_data = {
            "points": {
                "name": leaders["points"].First_Name,
                "value": leaders["points"].Points
            },
            "assists": {
                "name": leaders["assists"].First_Name,
                "value": leaders["assists"].Assists
            },
            "goals": {
                "name": leaders["goals"].First_Name,
                "value": leaders["goals"].Goals
            },
            "shut": {
                "name": leaders["shutoouts"].First_Name,
                "value": leaders["shutoouts"].Shutouts
            }
        }

        return leader_data
    else: 
        return

#Sort the standings table by a particular column.
def sort_standings(query, sort_by, sort_order):

    sort_columns = {
        "wins": lambda team: team.Wins,
        "losses": lambda team: team.Loss,
        "points": lambda team: (team.Points,team.Wins),
        "otl": lambda team: team.OT_Loss,
        "tie": lambda team: team.Ties,
        "points": lambda team: team.Points,
        "team": lambda team: team.Team,
        "goals_for": lambda team:team.Goals_For,
        "goals_again": lambda team:team.Goals_Against,
        "pim": lambda team: team.Pim,
        "game_play": lambda team: team.Games_Played
    }

    # Default to points if an invalid sort value is given
    column = sort_columns.get(sort_by, lambda team: (team.Points, team.Wins))

    if not column:
        return query

    #Return the sorted list.
    return sorted(
        query,
        key=column,
        reverse=(sort_order == "desc"))

 

###Routes for standings page
@app.route('/standings')
def standings():
    stand = (db.session.query(Standings)
             .where(Standings.season_id == get_selected_season_id())
             .order_by(Standings.Points.desc(),Standings.Wins.desc()).all())

    # Assign official rank
    for rank, team in enumerate(stand, start=1):
        team.rank = rank

        #Update the team rank
        if team.Team=="Misfits":
            team_stand=team
  
    #Check sorted column the user picks
    sort_by = request.args.get("sort")
    sort_order = request.args.get("order","desc")

    stand = sort_standings(
         stand,
         sort_by,
         sort_order
    )

  
    games = ( db.session.query(Calendar).where(Calendar.season_id==get_selected_season_id())
             .order_by(Calendar.date.asc()).all())

    if not stand and not games:
        return render_template("standings.html",current_stand = None, page=None,
                                    team =None, curr_schd = None, lead = None, streak=None)
    # Create a lookup: Team name -> Badge
    badge_lookup = {
        team.Team: team.logo
        for team in stand
    }

    curr_streak = get_streak()

    next_game=None
    today = datetime.today().date()

    # Find the next scheduled game
    next_game_row = next(
    (
        game for game in games
        if game.date >= today
        and game.Status == "Scheduled"
    ),
    None
)

    next_game = (
        get_next_game(next_game_row)
        if next_game_row else None
    )

    # Find the three most recent completed games
    recent_games = [
        game for game in reversed(games)
        if game.Status == "Final"
        and game.date <= today
    ][:3]

    # Assign opponent logos
    for game in recent_games:
        game.opp_logo = badge_lookup.get(game.opponent)
      
    
    #Get Team leaders in points, goals, etc..
    team_lead = get_leaders()
     
    return render_template("standings.html",current_stand = stand, page=next_game,
                            team =team_stand, curr_schd = recent_games, lead = team_lead, 
                            streak=curr_streak,sort_order=sort_order, sort_by=sort_by)

###End of standings routes


###Routes for roster

@app.route('/roster')
def roster():
    team = ( db.session.query(Roster).where(Roster.season_id==get_selected_season_id())
            .order_by(Roster.Position, Roster.Last_Name).all())
    
    pos_group ={"forwards":[],"defense":[],"goalies":[]}

    for player in team:
        if player.Position in ["C","LW","RW","Center","Wing","Winger"]:
            pos_group["forwards"].append(player)
        elif player.Position in ["D","RD","LD","Defense"]:
            pos_group["defense"].append(player)
        elif player.Position in ["G","Goalie"]:
            pos_group["goalies"].append(player)

    section_info = {
        "forwards": {"title": "Forwards", "icon": "⌯"},
        "defense": {"title": "Defensemen", "icon": "🛡️"},
        "goalies": {"title": "Goalies", "icon": "🥅"}
    }

    player_count = {"total":len(team),
                    "forwards": len(pos_group["forwards"]),
                    "defense":len(pos_group["defense"]),
                    "goalies":len(pos_group["goalies"])}

    return render_template("roster.html",grouped_players=pos_group,
        section_info=section_info, player_count= player_count)



##End of roster route/methods


#Game Preview Route id is unique.
@app.route("/games/<int:game_id>")
def game_preview(game_id):
    games = ( db.session.query(Calendar)
            .filter(Calendar.game_id==game_id, Calendar.season_id == get_selected_season_id())
            .first_or_404())

    team_record = get_records("Misfits")
    opp_record = get_records(games.opponent)

    game_info = get_next_game(games)

    #Previous Matchup
    prev_game = ( db.session.query(Calendar)
                .filter(Calendar.game_id!=games.game_id,
                         Calendar.opponent == games.opponent,
                        Calendar.date<games.date, Calendar.season_id==get_selected_season_id())
                        .order_by(Calendar.date.desc()).first())
    
    
    return render_template("game_preview.html", game=game_info, 
                           team_rec = team_record, op_rec=opp_record,
                           prev = prev_game)






if __name__ =='__main__':
    app.run(debug=True)