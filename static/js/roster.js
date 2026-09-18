
//Get the standings of the teams.
async function getRoster() {
  try{
    const response = await fetch("/get_roster");
    const roster = await response.json();
  }
  catch (error){
      console.log("Could not retrieve data");
  }
}


document.addEventListener("DOMContentLoaded", () => {
  //getRoster();
});