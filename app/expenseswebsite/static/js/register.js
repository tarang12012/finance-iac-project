const usernameField = document.querySelector("#usernameField");
const feedBackArea = document.querySelector(".invalid_feedback");
const emailField = document.querySelector("#emailField");
const emailFeedBackArea = document.querySelector(".emailFeedBackArea");
const passwordField = document.querySelector("#passwordField");
const showPasswordToggle = document.querySelector(".showPasswordToggle");
const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

showPasswordToggle.addEventListener("click", () => {
  const type = passwordField.type === "password" ? "text" : "password";
  passwordField.type = type;
  confirmPasswordField.type = type;
  showPasswordToggle.textContent = type === "password" ? "SHOW" : "HIDE";
});

confirmPasswordField.addEventListener("keyup", () => {
  if (passwordField.value !== confirmPasswordField.value) {
    passwordMismatchMsg.style.display = "block";
  } else {
    passwordMismatchMsg.style.display = "none";
  }
});

usernameField.addEventListener("keyup", (e) => {
  const val = e.target.value.trim();
  feedBackArea.style.display = "none";
  usernameField.classList.remove("is-invalid");

  fetch("/authentication/validate-username", {
    method: "POST",
    body: JSON.stringify({ username: val }),
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.username_error) {
        usernameField.classList.add("is-invalid");
        feedBackArea.style.display = "block";
        feedBackArea.innerHTML = `<p>${data.username_error}</p>`;
      }
    });
});

emailField.addEventListener("keyup", (e) => {
  const val = e.target.value.trim();
  emailFeedBackArea.style.display = "none";
  emailField.classList.remove("is-invalid");

  fetch("/authentication/validate-email", {
    method: "POST",
    body: JSON.stringify({ email: val }),
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": csrfToken,
    },
  })
    .then((res) => res.json())
    .then((data) => {
      if (data.email_error) {
        emailField.classList.add("is-invalid");
        emailFeedBackArea.style.display = "block";
        emailFeedBackArea.innerHTML = `<p>${data.email_error}</p>`;
      }
    });
});
