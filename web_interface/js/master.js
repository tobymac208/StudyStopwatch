let i = 0;
let minutes = 25;
let started = false;

const start = () => {
    setTimeout(() => {
       document.getElementById("currenttime").value = i;

       if(i >= minutes) return; // Don't let the user cause the number to exceed the amount.

       i++; // Add one to the count.

       if(i <= minutes){
        start();
       }
    }, 1000); // Wait for 1 minute.

    for(let i = 0; i <= minutes; i++){
        
    }
};

const timer = () => {
    document.getElementById("currenttime").style.color = "red";

    // Ensure the user can't press the button quickly to mess with the timer.
    start();
};
