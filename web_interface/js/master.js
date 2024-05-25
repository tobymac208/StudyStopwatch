let timeTracker = 0;
let minutes = 25;
let started = false;

const timer = () => {
  var start = Date.now();
  started = true;
  document.getElementById("currenttime").style.color = "red";

  let inter = setInterval(() => {
    var delta = Date.now() - start; // milliseconds elapsed since start
    secondsElapsed = Math.floor(delta / 1000);

    // check if a minute has passed
    if (secondsElapsed >= 60) {
      document.getElementById("currenttime").value = ++timeTracker;
    }

    if (timeTracker >= minutes || !started) {
      stop();
      clearInterval(inter); // stop the interval, and the timer.
    }

    // alternatively just show wall clock time:
    output(new Date().toUTCString());
  }, 1000); // update about every second
};

const stop = () => {
    started = false;
    document.getElementById("currenttime").style.color = "black";
};

const reset = () => {
  stop();
  timeTracker = 0;
  document.getElementById("currenttime").value = timeTracker;
};
