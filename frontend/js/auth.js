// auth.js
const API = "http://127.0.0.1:5000/api";

document.getElementById("loginForm").onsubmit = async e=>{
  e.preventDefault();
  const email = document.getElementById("email").value;
  const password = document.getElementById("password").value;

  const res = await fetch(API + "/login", {
    method:"POST",
    headers:{"Content-Type":"application/json"},
    body: JSON.stringify({email,password})
  });

  const data = await res.json();
  if(res.ok){
    localStorage.setItem("user", JSON.stringify(data));
    alert("Login successful!");
    window.location = "index.html";
  } else {
    alert(data.error || "Login failed");
  }
};
