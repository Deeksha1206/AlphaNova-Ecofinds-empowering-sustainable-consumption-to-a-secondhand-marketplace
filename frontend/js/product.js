// product.js
const q = new URLSearchParams(location.search);
const id = q.get("id");

fetch(`http://127.0.0.1:5000/api/products/${id}`)
  .then(res => res.json())
  .then(p => {
    document.getElementById("title").innerText = p.title;
    document.getElementById("category").innerText = "Category: " + p.category;
    document.getElementById("price").innerText = "Price: ₹" + p.price;
  });
