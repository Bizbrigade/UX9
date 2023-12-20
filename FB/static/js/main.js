// Sticky Navber Function =====================
let navbar = document.getElementById('navigation');
window.addEventListener('scroll', () => {
  if (window.scrollY >= 355) {
    // scrollPopup.style.display = "block";
    navbar.classList.add("navScroll");
    speed = 2.05;
  } else if (window.scrollY <= 10) {
    // scrollPopup.style.display = "block";
    navbar.classList.remove("navScroll");
  }
});

// adviceForm onscroll js
function scrollPopover() {
    //   let scrollPopup = document.getElementById('adviceForm');
    let scrollPopup = document.querySelector('#adviceForm');
    window.onscroll = function () {
        let scrollPop = document.documentElement.scrollTop;
        if (scrollPop >= 355) {
            scrollPopup.style.display = "block";
        } else {
            scrollPopup.style.display = "none";
        }
    };
};
scrollPopover();

// Index Page Banner Slider =========
$('.banner-slider').slick({
    dots: false,
    arrows: false,
    infinite: true,
    autoplay: true,
    autoplaySpeed: 3000,
    slidesToShow: 1,
    slidesToScroll: 1,
});

// Index Page Testimonial Slider =========
$('.single-slider').slick({
    dots: false,
    arrows: true,
    infinite: false,
    autoplay: true,
    autoplaySpeed: 3000,
    slidesToShow: 1,
    slidesToScroll: 1,
    prevArrow: '<button class="fa-solid fa-angle-left"></button>',
    nextArrow: '<button class="fa-solid fa-angle-right""></button>',
});

// Index Page Testimonial Slider =========
$('.testimonial-slider').slick({
    dots: true,
    arrows: false,
    infinite: true,
    // autoplay: true,
    speed: 300,
    slidesToShow: 1,
    slidesToScroll: 1,
});

//  Exclusive Brands Slider 
$('.brands-slider').slick({
    dots: false,
    arrows: true,
    autoplay: true,
    autoplaySpeed: 3000,
    infinite: true,
    speed: 300,
    slidesToShow: 4,
    slidesToScroll: 1,
    settings: "unslick",
    prevArrow: '<button class="fa-solid fa-angle-left"></button>',
    nextArrow: '<button class="fa-solid fa-angle-right""></button>',
    responsive: [
        {
            breakpoint: 991,
            settings: {
                slidesToShow: 3,
                slidesToScroll: 1,
                arrows: true,
                mobileFirst: true
            }
        },
        {
            breakpoint: 767,
            settings: {
                slidesToShow: 2,
                slidesToScroll: 1,
                arrows: true
            }
        },
        {
            breakpoint: 576,
            settings: {
                slidesToShow: 1,
                slidesToScroll: 1,
                arrows: true
            }
        }
    ]
});

//  Endex page previous-event Slider 
$('.previous-event-slider').slick({
    dots: false,
    arrows: true,
    autoplay: true,
    infinite: true,
    speed: 300,
    slidesToShow: 4,
    slidesToScroll: 1,
    settings: "unslick",
    prevArrow: '<button class="fa-solid fa-angle-left"></button>',
    nextArrow: '<button class="fa-solid fa-angle-right""></button>',
    responsive: [
        {
            breakpoint: 991,
            settings: {
                slidesToShow: 3,
                slidesToScroll: 1,
                arrows: true,
                mobileFirst: true
            }
        },
        {
            breakpoint: 767,
            settings: {
                slidesToShow: 2,
                slidesToScroll: 1,
                arrows: true
            }
        },
        {
            breakpoint: 576,
            settings: {
                slidesToShow: 1,
                slidesToScroll: 1,
                arrows: true
            }
        }
    ]
});

//  Endex page only upcoming event Slider 
$('.only-upcoming-event-slider').slick({
    dots: false,
    arrows: true,
    autoplay: true,
    infinite: false,
    speed: 300,
    slidesToShow: 2,
    slidesToScroll: 1,
    settings: "unslick",
    prevArrow: '<button class="fa-solid fa-angle-left"></button>',
    nextArrow: '<button class="fa-solid fa-angle-right""></button>',
    responsive: [
        {
            breakpoint: 991,
            settings: {
                slidesToShow: 1,
                slidesToScroll: 1,
                arrows: true
            }
        }
    ]
});


//  featured-franchise Slider 
$('.featured-franchise-slider').slick({
    dots: false,
    arrows: true, 
    autoplay: true,
    autoplaySpeed: 3000,
    speed: 300,
    slidesToShow: 3,
    slidesToScroll: 1,
    settings: "unslick",
    prevArrow: '<button class="fa-solid fa-angle-left"></button>',
    nextArrow: '<button class="fa-solid fa-angle-right""></button>',
    responsive: [
        {
            breakpoint: 991,
            settings: {
                slidesToShow: 2
            }
        },
        {
            breakpoint: 767,
            settings: {
                slidesToShow: 1
            }
        }
    ]
});

//  Upcoming Events and Blogs Slider
$('.blog-event-slider').slick({
    dots: false,
    arrows: false,
    infinite: true,
    speed: 300,
    slidesToShow: 2,
    slidesToScroll: 1,
    autoplay: true,
});

// Previous Event Page Synsing Slider =========
$('.img-slider').slick({
    slidesToShow: 2,
    slidesToScroll: 1,
    arrows: false,
    fade: false,
    adaptiveHeight: true,
    infinite: true,
    useTransform: true,
    speed: 400,
    cssEase: 'cubic-bezier(0.77, 0, 0.18, 1)',
    responsive: [{
        breakpoint: 767,
        settings: {
            slidesToShow: 1,
        }
    }]
});
$('.img-single')
    .on('init', function (event, slick) {
        $('.img-single .slick-slide.slick-current').addClass('is-active');
    })
    .slick({
        slidesToShow: 7,
        slidesToScroll: 1,
        dots: false,
        focusOnSelect: false,
        infinite: false,
        prevArrow: '<button class="fa-solid fa-angle-left"></button>',
        nextArrow: '<button class="fa-solid fa-angle-right""></button>',
        responsive: [{
            breakpoint: 991,
            settings: {
                slidesToShow: 5,
                slidesToScroll: 5,
            }
        }, {
            breakpoint: 767,
            settings: {
                slidesToShow: 4,
                slidesToScroll: 4,
            }
        }, {
            breakpoint: 576,
            settings: {
                slidesToShow: 3,
                slidesToScroll: 3,
            }
        }]
    });

$('.img-slider').on('afterChange', function (event, slick, currentSlide) {
    $('.img-single').slick('slickGoTo', currentSlide);
    var currrentNavSlideElem = '.img-single .slick-slide[data-slick-index="' + currentSlide + '"]';
    $('.img-single .slick-slide.is-active').removeClass('is-active');
    $(currrentNavSlideElem).addClass('is-active');
});

$('.img-single').on('click', '.slick-slide', function (event) {
    event.preventDefault();
    var goToSingleSlide = $(this).data('slick-index');
    $('.img-slider').slick('slickGoTo', goToSingleSlide);
});

// brand-img-slider ===
$('.brand-img-slider').slick({
    dots: false,
    arrows: true,
    autoplay: false,
    infinite: true,
    speed: 300,
    slidesToShow: 4,
    slidesToScroll: 1,
    prevArrow: '<button class="fa-solid fa-angle-left"></button>',
    nextArrow: '<button class="fa-solid fa-angle-right""></button>',
    responsive: [
        {
            breakpoint: 991,
            settings: {
                slidesToShow: 3
            }
        },
        {
            breakpoint: 767,
            settings: {
                slidesToShow: 2
            }
        }
    ]
});

// Same Height function 
function sameHeight(parent_class, child_child) {
    $(parent_class).each(function () {
        // Cache the highest
        var highestBox = 0;
        // Select and loop the elements you want to equalis
        $(child_child, this).each(function () {
            // If this box is higher than the cached highest then store it
            if ($(this).height() > highestBox) {
                highestBox = $(this).height();
            }
        });
        // Set the height of all those children to whichever was highest
        $(child_child, this).height(highestBox);

    });
};
sameHeight('.sm-height-parent', '.sm-height');
    // if ($(window).width() > 768) {
    // } 

