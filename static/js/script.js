//Function to retrieve the first 5 games of the schedule
async function getGames() {
  const response = await fetch("/api/get_first_five");
  const games = await response.json();

  //Get the table attribute to add to.
  const tableEle = document.querySelector("#sch-table tbody");

  //Add the game details to the table
  games.games.forEach((element) => {
    const row = document.createElement("tr");
    const date_ = document.createElement("td");
    const oppon = document.createElement("td");
    const team = document.createElement("td");
    const loc = document.createElement("td");

    // Create container for logo + team name
    const teamWrapper = document.createElement("div");
    teamWrapper.classList.add("mini-team");

    // Create team logo
    const teamImg = document.createElement("img");
    teamImg.src = element.logo;
    teamImg.alt = element.oppon;
    teamImg.classList.add("mini-team-logo");

    // Create team name
    const teamName = document.createElement("span");
    teamName.textContent = element.oppon;

    // Add logo and name together
    teamWrapper.append(teamImg, teamName);

    // Add container to team cell
    team.appendChild(teamWrapper);

    date_.textContent = element.short;
    oppon.textContent = element.oppon;
    loc.textContent = element.loc;

    row.appendChild(date_);
    row.appendChild(team);
    row.appendChild(loc);
    tableEle.appendChild(row);
  });

}

//Get the standings of the teams.
async function getStandings() {
  const response = await fetch("/api/get_standings");
  const teams = await response.json();

  //Get the table attribute to add to.
  const tableEl = document.querySelector("#standings-tab tbody");

  //Add the team details to the standings table
  teams.standings.forEach((value) => {
    const row = document.createElement("tr");
    const team = document.createElement("td");
    const played = document.createElement("td");
    const win = document.createElement("td");
    const loss = document.createElement("td");
    const points = document.createElement("td");

    // Create container for logo + team name
    const teamWrapper = document.createElement("div");
    teamWrapper.classList.add("mini-team");

    // Create team logo
    const teamImg = document.createElement("img");
    teamImg.src = value.logo;
    teamImg.alt = value.team;
    teamImg.classList.add("mini-team-logo");

    // Create team name
    const teamName = document.createElement("span");
    teamName.textContent = value.Team;

    // Add logo and name together
    teamWrapper.append(teamImg, teamName);

    // Add container to team cell
    team.appendChild(teamWrapper);

    // Other standings details
    played.textContent = value.Games_Played;
    win.textContent = value.Wins;
    loss.textContent = value.Loss;
    points.textContent = value.Points;

    // Add cells to row
    row.append(team,played, win, loss, points);

    // Add row to table
    tableEl.appendChild(row);

  });


}

//Add to Google Calendar
const addCalendarBtn = document.getElementById("addCalendar");
if (addCalendarBtn){
  addCalendarBtn.addEventListener("click", () => {
    addToGoogleCalendar()
});}

function addToGoogleCalendar(){
  const date = document.querySelector(".date-next").textContent.trim();
const opponent = document.querySelector(".opponent-next").textContent.trim();
const location_ = document.querySelector(".date-next").textContent.trim();
const locationLink = document.querySelector(".loca-next").href;
    const title = `Misfits vs ${opponent}`; 
    const details = `Misfits hockey game against ${opponent}.`;
    const location = location_;

    const startDate = new Date(`${date}`);//T${time_}`);

    const endDate = new Date(startDate);
    endDate.setHours(endDate.getHours() + 1);

    const formatDate = (date) => {
        return date.toISOString().replace(/[-:]|\.\d{3}/g, "");
    };

    const calendarUrl =
        `https://calendar.google.com/calendar/render?action=TEMPLATE` +
        `&text=${encodeURIComponent(title)}` +
        `&dates=${formatDate(startDate)}/${formatDate(endDate)}` +
        `&details=${encodeURIComponent(details)}` +
        `&location=${encodeURIComponent(location)}`;

    window.open(calendarUrl, "_blank");
}

document.addEventListener("DOMContentLoaded", function(){
  
  try{
    getGames();
    getStandings();}
  catch(error){
    console.log("Could not load data:", error);
  }
});
