// Sample products for testing
const products = [
    { title: "Vintage Chair", category: "Furniture", price: 50 },
    { title: "Retro Lamp", category: "Decor", price: 30 },
    { title: "Old Books", category: "Books", price: 15 }
];

const container = document.getElementById("product-feed");

// Render each product
products.forEach(p => {
    const div = document.createElement("div");
    div.classList.add("product-card"); // optional class for CSS styling
    div.innerHTML = `
        <h3>${p.title}</h3>
        <p>Category: ${p.category}</p>
        <p>Price: ₹${p.price}</p>
    `;
    container.appendChild(div);
});

