// main.js
const BASE = "http://127.0.0.1:5000/api";  // backend must be running

async function fetchProducts(q="") {
  const url = BASE + "/products" + (q ? `?q=${encodeURIComponent(q)}` : "");
  const res = await fetch(url);
  return await res.json();
}

async function addProduct(payload) {
  await fetch(BASE + "/products", {
    method: "POST",
    headers: {"Content-Type":"application/json"},
    body: JSON.stringify(payload)
  });
}

async function load(q="") {
  const data = await fetchProducts(q);
  const list = document.getElementById("list");
  list.innerHTML = "";
  data.forEach(p => {
    const li = document.createElement("li");
    li.className = "list-group-item";
    li.innerHTML = `<strong>${p.title}</strong> — ₹${p.price} <br><small>${p.category}</small>`;
    li.onclick = ()=> window.location = `product.html?id=${p.id}`;
    list.appendChild(li);
  });
}

document.getElementById("addForm").onsubmit = async e=>{
  e.preventDefault();
  const title = document.getElementById("title").value.trim();
  const category = document.getElementById("category").value.trim();
  const price = Number(document.getElementById("price").value);
  if(!title || !category || !price){ alert("Fill all fields"); return; }
  await addProduct({ title, category, price });
  document.getElementById("addForm").reset();
  load();
};

document.getElementById("sbtn").onclick = ()=> load(document.getElementById("search").value);
load();
