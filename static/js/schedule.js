let scheduleSortOrder = "desc";

//Get the standings of the teams.
async function getSchedule() {
  try{
   
  const response = await fetch(`/get_schedule?order=${scheduleSortOrder}`);
  const teams = await response.json();


   //Get the table attribute to add to and reset.
   const tableEl = document.querySelector("#sched_table tbody");
   tableEl.innerHTML = "";

   //Add the team details to the standings table
  teams.schedule.forEach((value) => {
     const row = document.createElement("tr");
     const date_ = document.createElement("td");
     const opponent = document.createElement("td");

    const opponentWrapper = document.createElement("div");
    opponentWrapper.classList.add("opponent-cell"); 

     const location = document.createElement("td");
     const time = document.createElement("td");
     const result = document.createElement("td");
     const status = document.createElement("td");

     // Add class to the details cell
     const details = document.createElement("td");
    details.classList.add("details-cell");

    const logoImg = document.createElement("img");
    logoImg.src = `${value.logo}`;
    logoImg.alt = `${value.oppon} logo`;
    logoImg.classList.add("schedule-team-logo");

    const opponentName = document.createElement("span");
    opponentName.textContent = value.oppon;

    opponentWrapper.append(logoImg, opponentName);
    opponent.appendChild(opponentWrapper);



     date_.textContent = value.date;
     location.textContent = value.loc;
     time.textContent = value.time;
     status.textContent= value.stat;
     result.textContent = value.result;

     const statusText = value.stat.trim().toLowerCase();

      //Preview the next game
    const previewButton = document.createElement("button");
    previewButton.textContent = "Preview";
   
    //Used to filter based on final and scheduled games.
    if (statusText === "final") {
      row.dataset.status = "final";
       previewButton.textContent = "Recap";
    } else {
     row.dataset.status = "scheduled";
    }

    previewButton.classList.add("preview-btn");
    
    const resultText = value.result.trim();
    const firstLetter = resultText.charAt(0).toUpperCase();

    if (firstLetter === "W") {
      result.classList.add("result-win");
    } else if (firstLetter === "L") {
      result.classList.add("result-loss");
    }  


   

    previewButton.addEventListener("click", () => {
    window.location.href = `/games/${value.id}`;
  });
    

     row.appendChild(date_);
     row.appendChild(opponent);
     //row.appendChild(opponent_img);
     row.appendChild(location);
     row.appendChild(time);
     row.appendChild(result); 
     row.appendChild(status);
     

     //Put the preview details in a cell and add to a row.
     details.appendChild(previewButton);
     row.appendChild(details);

     tableEl.appendChild(row);});}
     catch (error){
      console.log("Could not retrieve data");
     }
   
}


document.addEventListener("DOMContentLoaded", () => {
  getSchedule();

  // Sort based on the date field in the table
  const dateSort = document.getElementById("date-sort");

  dateSort.addEventListener("click", function () {

  const arrow = document.getElementById("date-sort-arrow");

  // Change to the corresponding opposite.
  if (scheduleSortOrder === "desc") {
    scheduleSortOrder = "asc";
    arrow.textContent = "↑";
  } else {
      scheduleSortOrder = "desc";
      arrow.textContent = "↓";
  }

  getSchedule();
  });
});

//Filter the games based on all, upcoming and final.
const filterButtons = document.querySelectorAll(".filter-buttons button");

filterButtons.forEach(button => {
    button.addEventListener("click", () => {
        const filter = button.dataset.filter;

        // update active button style
        filterButtons.forEach(btn => btn.classList.remove("active"));
        button.classList.add("active");

        // filter table rows
        const rows = document.querySelectorAll("tbody tr");

        rows.forEach(row => {
            const rowStatus = row.dataset.status;

            if (filter === "all" || rowStatus === filter) {
                row.style.display = "";
            } else {
                row.style.display = "none";
            }
        });
    });
});

//Add to Google Calendar
const addCalendarBtn = document.getElementById("add-calendar-btn");
if (addCalendarBtn){
  addCalendarBtn.addEventListener("click", () => {
    addToGoogleCalendar()
});}

function addToGoogleCalendar(){
  const date = document.querySelector(".next-date").textContent.trim();
const opponent = document.querySelector(".next-opponent").textContent.trim();
const location_ = document.querySelector(".next-location a").textContent.trim();
const locationLink = document.querySelector(".next-location a").href;
//const time_ = document.querySelector(".next-time_").trim();
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

