document.getElementById("ping-btn").addEventListener("click", async () => {
    const result = document.getElementById("ping-result");
    try {
        const res = await fetch("/api/ping");
        const data = await res.json();
        result.textContent = JSON.stringify(data, null, 2);
    } catch (err) {
        result.textContent = "Error: " + err.message;
    }
});

document.getElementById("echo-btn").addEventListener("click", async () => {
    const input = document.getElementById("echo-input").value;
    const result = document.getElementById("echo-result");
    try {
        const res = await fetch("/api/echo", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: input }),
        });
        const data = await res.json();
        result.textContent = JSON.stringify(data, null, 2);
    } catch (err) {
        result.textContent = "Error: " + err.message;
    }
});
