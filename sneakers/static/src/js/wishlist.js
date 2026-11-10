(function () {

if (window.snWishlistLoaded) {
    console.log("Wishlist JS already loaded");
    return;
}

window.snWishlistLoaded = true;


var wishlistSection = document.querySelector(".sn-wishlist");



// ============================
// REMOVE FROM WISHLIST
// ============================

if (wishlistSection) {


    wishlistSection.addEventListener("click", function (e) {


        var removeBtn = e.target.closest(
            ".sn-wishlist-remove, .sn-remove-wishlist"
        );


        if (!removeBtn) return;



        var wishlistItem = removeBtn.closest(
            ".sn-wishlist-item, .sn-product-card"
        );



        if (!wishlistItem) return;



        var wishId = wishlistItem.dataset.wishId;



        if (!wishId) {

            console.error(
                "Wishlist ID missing"
            );

            return;
        }



        fetch(
            "/shop/wishlist/remove/" + wishId,
            {

                method:"POST",

                headers:{
                    "Content-Type":"application/json",
                    "X-CSRFToken": odoo.csrf_token
                },


                body:JSON.stringify({

                    jsonrpc:"2.0",

                    method:"call",

                    params:{}

                })

            }
        )


        .then(response => response.json())


        .then(data => {


            console.log(
                "Remove wishlist:",
                data
            );



            if(data.result){
                // ponytail: sync localStorage so navbar dot updates
                var wishItemId = wishlistItem.dataset.wishId;
                var wishProductId = wishlistItem.dataset.productId;
                if (wishProductId) {
                    var wl = JSON.parse(localStorage.getItem("sn_wishlist") || "[]");
                    wl = wl.filter(function(id) { return id !== String(wishProductId); });
                    localStorage.setItem("sn_wishlist", JSON.stringify(wl));
                }
                updateWishlistBadge();
                window.location.reload();
            }


        });



    });



}



// ============================
// CHECK CART QUANTITY
// ============================


function checkCartQuantity(productId, callback){


    fetch(
        "/shop/cart/get_quantity",
        {

            method:"POST",


            headers:{
                "Content-Type":"application/json",
                "X-CSRFToken": odoo.csrf_token
            },


            body:JSON.stringify({

                jsonrpc:"2.0",

                method:"call",

                params:{

                    product_id: parseInt(productId)

                }

            })


        }
    )


    .then(response => response.json())


    .then(data => {


        console.log(
            "CURRENT ODOO CART QTY:",
            data
        );



        if(data.result !== undefined){


            callback(
                parseInt(data.result,10)
            );


        }
        else{


            callback(0);


        }


    })


    .catch(function(error){


        console.error(
            "CART QTY ERROR:",
            error
        );


        callback(0);


    });



}

// ============================
// ADD TO CART FROM WISHLIST
// ============================


if (wishlistSection) {


    wishlistSection.addEventListener("click", function(e){



        var addBtn = e.target.closest(
            ".sn-wishlist-item .sn-add-cart"
        );



        if(!addBtn)
            return;



        if(addBtn.dataset.processing === "true"){

            console.log(
                "BLOCK DOUBLE CLICK"
            );

            return;

        }



        addBtn.dataset.processing = "true";



        e.preventDefault();

        e.stopImmediatePropagation();



        var wishlistItem = addBtn.closest(
            ".sn-wishlist-item, .sn-product-card"
        );



        if(!wishlistItem){


            console.error(
                "Wishlist item missing"
            );


            addBtn.dataset.processing="false";


            return;

        }




        var productId =
            wishlistItem.dataset.productId;




        if(!productId){


            console.error(
                "Product ID missing"
            );


            addBtn.dataset.processing="false";


            return;

        }




        var maxStock = parseInt(
            addBtn.dataset.stock,
            10
        );



        if(isNaN(maxStock)){

            maxStock = null;

        }



        console.log(
            "PRODUCT:",
            productId,
            "STOCK:",
            maxStock
        );




        // Vérifier quantité actuelle panier

        checkCartQuantity(
            productId,

            function(currentCartQty){



                console.log(
                    "CURRENT CART:",
                    currentCartQty
                );




                if(
                    maxStock !== null &&
                    currentCartQty >= maxStock
                ){


                    addBtn.disabled=true;


                    addBtn.textContent =
                        "Maximum quantity reached";



                    addBtn.dataset.processing="false";



                    if(window.snShowToast){

                        window.snShowToast(
                            "Maximum quantity reached.",
                            "error"
                        );

                    }


                    return;

                }





                addProductToCart(
                    productId,
                    addBtn,
                    maxStock
                );



            }

        );



    });


}






// ============================
// FUNCTION ADD PRODUCT TO CART
// ============================



function addProductToCart(
    productId,
    addBtn,
    maxStock
){



    fetch(
        "/shop/cart/update_json",
        {


            method:"POST",


            headers:{

                "Content-Type":"application/json",

                "X-CSRFToken": odoo.csrf_token

            },


            body:JSON.stringify({

                jsonrpc:"2.0",

                method:"call",

                params:{


                    product_id:
                        parseInt(productId),


                    add_qty:1


                }


            })

        }

    )


    .then(response => response.json())


    .then(data => {



        console.log(
            "CART RESPONSE:",
            data
        );




        if(data.error){


            console.error(
                data.error
            );


            addBtn.dataset.processing="false";


            return;

        }





        if(data.result){



            var newQty =
                parseInt(
                    data.result.quantity,
                    10
                );



            addBtn.dataset.cartQty =
                newQty;




            if(
                maxStock !== null &&
                newQty >= maxStock
            ){


                addBtn.disabled=true;


                addBtn.textContent =
                    "Maximum quantity reached";


            }
            else{


                addBtn.disabled=false;


                addBtn.textContent =
                    "Added";



                setTimeout(function(){


                    if(!addBtn.disabled){


                        addBtn.textContent =
                            "Add to cart";


                    }


                },1500);



            }





            // Update panier badge


            var badge =
                document.querySelector(
                    ".sn-cart-count"
                );



            if(badge && data.result.cart_quantity !== undefined){


                badge.textContent =
                    data.result.cart_quantity;


                badge.style.display="flex";


            }





            if(window.snShowToast){


                window.snShowToast(
                    "Product added to cart!"
                );


            }



        }




        addBtn.dataset.processing="false";



    })



    .catch(function(error){



        console.error(
            "CART ERROR:",
            error
        );



        addBtn.dataset.processing="false";



    });



}

// ============================
// ADD TO WISHLIST
// ============================


document.addEventListener(
    "click",
    function(e){



        var heartBtn = e.target.closest(
            ".sn-product-wishlist, .sn-btn-heart"
        );



        if(!heartBtn)
            return;




        e.preventDefault();




        var productId =
            heartBtn.dataset.productId;




        if(!productId){


            console.error(
                "Product variant ID missing"
            );


            return;

        }




        fetch(
            "/shop/wishlist/add",
            {


                method:"POST",


                headers:{


                    "Content-Type":"application/json",

                    "X-CSRFToken": odoo.csrf_token


                },



                body:JSON.stringify({


                    jsonrpc:"2.0",


                    method:"call",



                    params:{


                        product_id:
                            parseInt(productId)


                    }



                })



            }

        )



        .then(response => response.json())



        .then(data => {



            console.log(
                "Wishlist response:",
                data
            );




            if(data.error){


                console.error(
                    data.error
                );


                return;


            }




            if(data.result){



                heartBtn.classList.add(

                    "active",

                    "sn-btn-heart--active"

                );



                heartBtn.setAttribute(

                    "aria-pressed",

                    "true"

                );





                if(window.snShowToast){


                    window.snShowToast(

                        "Added to wishlist !"

                    );


                }




                // ponytail: sync localStorage so navbar dot updates
                var wl = JSON.parse(localStorage.getItem("sn_wishlist") || "[]");
                if (wl.indexOf(String(productId)) === -1) {
                    wl.push(String(productId));
                    localStorage.setItem("sn_wishlist", JSON.stringify(wl));
                }
                updateWishlistBadge();



            }





        })



        .catch(function(error){


            console.error(

                "WISHLIST ERROR:",

                error

            );


        });



    }

);







// ============================
// UPDATE WISHLIST BADGE
// ============================

function updateWishlistBadge(){

        var wl = JSON.parse(
            localStorage.getItem("sn_wishlist") || "[]"
        );

        var badge = document.querySelector(
            ".sn-wishlist-count"
        );

        if (!badge) return;

        var quantity = wl.length || 0;

        console.log(
            "WISHLIST QUANTITY :",
            quantity
        );

        if(quantity > 0){

            badge.textContent = quantity;
            badge.style.display = "flex";

        }else{

            badge.style.display = "none";

        }

    }

// ============================
// EMPTY STATE
// ============================


function checkEmptyWishlist(){


    if(!wishlistSection)
        return;



    var items =
        wishlistSection.querySelectorAll(
            ".sn-wishlist-item, .sn-product-card"
        );

    var wishlistTop =
    wishlistSection.querySelector(
        ".sn-wishlist-top"
    );



    if(!items.length){

        if (wishlistTop) {
            wishlistTop.style.display = "none";
        }

        var grid =
            wishlistSection.querySelector(
                ".sn-products-grid"
            );



        if(grid){



            grid.innerHTML =
            `

            <div class="sn-empty-card">

                <div class="sn-empty-icon">

                    <i class="fa fa-heart-o" aria-hidden="true"></i>

                </div>


                <h3>
                    Your wishlist is empty
                </h3>



                <p>
                    You haven't added any sneakers to your wishlist yet.
                    Discover our latest collection and save your favorite pairs.
                </p>



                <a href="/shop-sneakers"
                   class="sn-btn-primary">

                    Explore collection

                </a>
                <a href="/" class="sn-btn-outline-wl sn-back-home-btn">

                    ← Back to Home

                </a>



            </div>

            `;


        }


    }


}






// ============================
// INITIALIZATION
// ============================


checkEmptyWishlist();

updateWishlistBadge();



})();