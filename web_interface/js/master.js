let timeTracker = 0;
let minutes = 25;
let started = false;

const timer = () => {
    started = true;
    document.getElementById("currenttime").style.color = "red";

    let timer = setInterval(() => {
        document.getElementById("currenttime").value = timeTracker;
        timeTracker++;

        if(timeTracker > minutes || !started){
            clearInterval(timer);
        }
    }, 60*1000); // wait for a minute
}

const reset = () => {
    started = false;
    timeTracker = 0;
    document.getElementById("currenttime").value = timeTracker;
    document.getElementById("currenttime").style.color = "black";
};
