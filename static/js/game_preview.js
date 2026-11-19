const calendarButton = document.getElementById("add-calendar-btn");

  if (calendarButton) {
    calendarButton.addEventListener("click", () => {
      const opponent = calendarButton.dataset.opponent;
      const location = calendarButton.dataset.location;
      const date = calendarButton.dataset.date;
      const time = calendarButton.dataset.time;

      const title = `Misfits vs ${opponent}`; 
    const details = `Misfits hockey game against ${opponent}.`;
    //const location = location_;

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



      //alert(`Calendar event placeholder:\nMisfits vs ${opponent}\n${date} at ${time}\n${location}`);
    });
  }
