const calendarButton = document.getElementById("add-calendar-btn");

  if (calendarButton) {
    calendarButton.addEventListener("click", () => {
      const opponent = calendarButton.dataset.opponent;
      const location = calendarButton.dataset.location;
      const date = calendarButton.dataset.date;
      const time = calendarButton.dataset.time;

      alert(`Calendar event placeholder:\nMisfits vs ${opponent}\n${date} at ${time}\n${location}`);
    });
  }
