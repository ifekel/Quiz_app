(function () {
    "use strict"


    new Swiper('.img-div', {
        speed: 1000,
        loop: true,
        autoplay: {
            delay: 3000,
            disableOnInteraction: false
        },
        slidesPerView: 'auto',
        pagination: {
            el: '.swiper-pagination',
            type: 'bullets',
            clickable: true
        }
    });


    window.addEventListener('load', () => {
        AOS.init({
            duration: 1000,
            easing: 'ease-in-out',
            once: true,
            mirror: false
        })
    });


    // new PureCounter();

    const fa_bars = document.querySelector('.fa-bars');
    const responsive_nav_bar = document.querySelector('.responsive-nav-bar');
    const close = document.querySelector('.close');

    fa_bars.addEventListener('click', (e) => {
        responsive_nav_bar.style.left = '0';
        close.style.display = 'block';
        fa_bars.style.display = 'none';
    })

    close.addEventListener('click', (e) => {
        responsive_nav_bar.style.left = '-200%';
        close.style.display = 'none';
        fa_bars.style.display = 'block';
    })
})()