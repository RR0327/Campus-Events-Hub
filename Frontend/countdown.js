// countdown.js

const eventDate = new Date("2025-06-11T10:00:00").getTime();

const countdown = setInterval(() => {
  const now = new Date().getTime();
  const distance = eventDate - now;

  if (distance < 0) {
    clearInterval(countdown);
    document.querySelector(".timer").innerHTML = "🎉 Event Started!";
    return;
  }

  const days = Math.floor(distance / (1000 * 60 * 60 * 24));
  const hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
  const minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
  const seconds = Math.floor((distance % (1000 * 60)) / 1000);

  document.getElementById("days").querySelector("span").textContent = days.toString().padStart(2, '0');
  document.getElementById("hours").querySelector("span").textContent = hours.toString().padStart(2, '0');
  document.getElementById("minutes").querySelector("span").textContent = minutes.toString().padStart(2, '0');
  document.getElementById("seconds").querySelector("span").textContent = seconds.toString().padStart(2, '0');
}, 1000);
