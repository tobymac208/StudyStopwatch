let timeTracker = 0;
let minutes = 25;
let started = false;

const timer = () => {
    started = true;

    let timer = setInterval(() => {
        document.getElementById("currenttime").value = timeTracker;
        timeTracker++;

        if(timeTracker > minutes || !started){
            clearInterval(timer);
        }
    }, 1000);
}

const reset = () => {
    started = false;
    timeTracker = 0;
    document.getElementById("currenttime").value = timeTracker;
};
