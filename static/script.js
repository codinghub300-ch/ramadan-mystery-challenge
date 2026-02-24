async function submitKey() {
    const key = document.getElementById("keyInput").value;
    const msg = document.getElementById("message");
    const success = document.getElementById("successSound");
    const fail = document.getElementById("failSound");

    const res = await fetch("/submit", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({key})
    });

    const data = await res.json();

    if(data.success){
        success.play();
        msg.style.color="#00ffcc";
        msg.innerText="Access Granted...";
        localStorage.setItem("result", JSON.stringify(data));
        document.getElementById("accessOverlay").classList.add("active");

    setTimeout(()=>{
    window.location="/lantern";
        },1800);
    } 
    else {
        fail.play();
        msg.style.color="red";
        msg.innerText=data.message || "ACCESS DENIED";
    }
}