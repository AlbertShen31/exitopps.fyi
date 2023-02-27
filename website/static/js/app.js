const mobileMenuBtn = document.querySelector('.mobilenav-toggle');
const mobileNav = document.querySelector('.mobile-nav');

mobileMenuBtn.addEventListener('click', function () {
  mobileMenuBtn.classList.toggle('menu-open');
  mobileNav.classList.toggle('open');
});

// Hide menu on nav link click
document.addEventListener('click', function (e) {
  if (e.target.closest('.mobile-nav ul li .nav__menu--item')) {
    mobileNav.classList.toggle('open');
    mobileMenuBtn.classList.toggle('menu-open');
  }
});
