let timeTracker = 0;
let minutes = 25;
let started = false;

const timer = () => {
  var start = Date.now();
  started = true;

  let inter = setInterval(() => {
    var delta = Date.now() - start; // milliseconds elapsed since start
    secondsElapsed = Math.floor(delta / 1000);

    timeTracker++;
    document.getElementById("currenttime").value = timeTracker;

    if (secondsElapsed >= minutes || !started) {
      clearInterval(inter); // stop the interval, and the timer.
    }

    // alternatively just show wall clock time:
    output(new Date().toUTCString());
  }, 1000); // update about every second
};

const reset = () => {
  started = false;
  timeTracker = 0;
  document.getElementById("currenttime").value = timeTracker;
  document.getElementById("currenttime").style.color = "black";
};
