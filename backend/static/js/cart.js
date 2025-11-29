// static/js/cart.js

async function apiPost(url, data) {
    const res = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    });

    if (!res.ok) {
        throw new Error("Request failed");
    }
    return await res.json();
}

// ---------- Product page: Add to cart ----------

function setupAddToCartFromProductPage() {
    const btn = document.getElementById("btn-add-to-cart");
    if (!btn) return;

    btn.addEventListener("click", async () => {
        const productId = parseInt(btn.dataset.productId);
        const qtyInput = document.getElementById("product-qty");
        const quantity = parseInt(qtyInput.value || "1");

        try {
            await apiPost("/api/cart/add", {
                product_id: productId,
                quantity: quantity,
            });
            alert("Added to cart!");
        } catch (err) {
            alert("Error adding to cart. Maybe you are not logged in.");
        }
    });
}

// ---------- Cart page: quantities & remove ----------

function setupCartPage() {
    const tbody = document.getElementById("cart-items-body");
    if (!tbody) return;

    function recalcSubtotal() {
        let subtotal = 0;
        tbody.querySelectorAll("tr").forEach((row) => {
            const totalCell = row.querySelector(".line-total");
            if (!totalCell) return;
            const text = totalCell.textContent.replace("$", "").trim();
            const value = parseFloat(text) || 0;
            subtotal += value;
        });
        const subtotalSpan = document.getElementById("cart-subtotal");
        if (subtotalSpan) {
            subtotalSpan.textContent = "$" + subtotal.toFixed(2);
        }
    }

    tbody.addEventListener("click", async (e) => {
        const target = e.target;
        const row = target.closest("tr[data-cart-item-id]");
        if (!row) return;

        const cartItemId = parseInt(row.dataset.cartItemId);
        const qtyInput = row.querySelector(".qty-input");
        const priceCell = row.querySelector("td:nth-child(2)");
        const lineTotalCell = row.querySelector(".line-total");

        if (target.classList.contains("btn-remove-item")) {
            // Remove item
            try {
                await apiPost("/api/cart/remove", {
                    cart_item_id: cartItemId,
                });
                row.remove();
                recalcSubtotal();
            } catch (err) {
                alert("Error removing item.");
            }
            return;
        }

        if (target.classList.contains("minus") || target.classList.contains("plus")) {
            let quantity = parseInt(qtyInput.value || "1");
            if (target.classList.contains("minus")) {
                quantity = Math.max(1, quantity - 1);
            } else {
                quantity = quantity + 1;
            }
            qtyInput.value = quantity;

            try {
                const updated = await apiPost("/api/cart/update", {
                    cart_item_id: cartItemId,
                    quantity: quantity,
                });
                const price = parseFloat(priceCell.textContent.replace("$", "").trim()) || 0;
                const lineTotal = price * updated.quantity;
                lineTotalCell.textContent = "$" + lineTotal.toFixed(2);
                recalcSubtotal();
            } catch (err) {
                alert("Error updating quantity.");
            }
        }
    });

    // Manual change in qty input
    tbody.addEventListener("change", async (e) => {
        const target = e.target;
        if (!target.classList.contains("qty-input")) return;

        const row = target.closest("tr[data-cart-item-id]");
        if (!row) return;
        const cartItemId = parseInt(row.dataset.cartItemId);
        const priceCell = row.querySelector("td:nth-child(2)");
        const lineTotalCell = row.querySelector(".line-total");

        let quantity = parseInt(target.value || "1");
        quantity = Math.max(1, quantity);
        target.value = quantity;

        try {
            const updated = await apiPost("/api/cart/update", {
                cart_item_id: cartItemId,
                quantity: quantity,
            });
            const price = parseFloat(priceCell.textContent.replace("$", "").trim()) || 0;
            const lineTotal = price * updated.quantity;
            lineTotalCell.textContent = "$" + lineTotal.toFixed(2);
            recalcSubtotal();
        } catch (err) {
            alert("Error updating quantity.");
        }
    });
}
