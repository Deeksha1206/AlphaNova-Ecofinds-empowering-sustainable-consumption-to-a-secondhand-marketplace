// Sample product data
const products = [
    { title: "Vintage Chair", category: "Furniture", price: 50 },
    { title: "Retro Lamp", category: "Decor", price: 30 },
    { title: "Old Books", category: "Books", price: 15 }
];

// Render product
const container = document.getElementById("product-feed");
products.forEach(p => {
    const div = document.createElement("div");
    div.classList.add("product-card");
    div.innerHTML = `
        <h3>${p.title}</h3>
        <p>Category: ${p.category}</p>
        <p>Price: ₹${p.price}</p>
    `;
    container.appendChild(div);
});
