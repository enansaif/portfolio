const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add("slidein");
    } else {
      entry.target.classList.remove("slidein");
    }
  });
});

const hiddenElement = document.querySelectorAll(".slidein-card");
hiddenElement.forEach((element) => {
  observer.observe(element);
});

var toggler = document.getElementById("dark-side-toggle");
toggler.onclick = () => {
  document.body.classList.toggle("dark-side");
  let togglerIcon = document.getElementById("toggler-icon");
  if (togglerIcon.classList.contains("bi-sun-fill")) {
    togglerIcon.classList.replace("bi-sun-fill", "bi-moon-fill");
  } else {
    togglerIcon.classList.replace("bi-moon-fill", "bi-sun-fill");
  }
};

function blurLoadProfileImage(){
  const blurDiv = document.querySelector(".blur-load");
  if (!blurDiv) {
    return;
  }
  const img = blurDiv.querySelector("img");
  if (img.complete) {
    loaded();
  } else {
    img.addEventListener("load", loaded);
  }
  function loaded() {
    blurDiv.classList.add("loaded");
  }
}

blurLoadProfileImage()
