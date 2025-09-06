// Sample user data for testing
const users = [
    { username: "meghana", password: "1234" },
    { username: "teammate1", password: "abcd" }
];

document.getElementById("login-form").addEventListener("submit", function(e) {
    e.preventDefault();

    const username = document.getElementById("username").value;
    const password = document.getElementById("password").value;

    const user = users.find(u => u.username === username && u.password === password);

    if(user) {
        alert("Login successful!");
        // Redirect to index or product page
        window.location.href = "index.html";
    } else {
        alert("Invalid username or password");
    }
});
