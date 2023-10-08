function password_show_hide() {
  var x = document.getElementById("password");
  var show_eye = document.getElementById("show_eye");
  var hide_eye = document.getElementById("hide_eye");
  hide_eye.classList.remove("d-none");

  if (x.type === "text") {
    if (x.value.trim() !== "") {
      x.type = "password";
      show_eye.style.display = "block";
      hide_eye.style.display = "none";
    } else {
      show_eye.style.display = "none";
      hide_eye.style.display = "block";
    }
  } else {
    x.type = "text";
    show_eye.style.display = "none";
    hide_eye.style.display = "block";
  }
}

const obeserver = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    console.log(entry);
    if (entry.isIntersecting) {
      entry.target.classList.add("show");
    } else {
      entry.target.classList.remove("show");
    }
  });
});

const hiddenElements = document.querySelectorAll(".hidden");
hiddenElements.forEach((el) => obeserver.observe(el));

function copy(that) {
  var inp = document.createElement("input");
  document.body.appendChild(inp);
  inp.value = that.textContent;
  inp.select();
  document.execCommand("copy", false);
  inp.remove();
}

const form = document.getElementById("arb-form");
const oddsContainer = document.getElementById("odds-container");
const oddsValues = []; // Array to store the values of the odds input fields

let oddsCount = 0; // Track the number of added odds containers

// Function to handle the "Add Odds" button click
function handleAddOddsClick() {
  if (oddsCount < 10) {
    oddsCount++;

    // Create a new input element for odds
    const oddsInput = document.createElement("input");
    oddsInput.type = "number";
    oddsInput.name = "odds" + oddsCount; // Set the name attribute with incrementing number
    oddsInput.id = "odds" + oddsCount; // Set the id attribute with incrementing number
    oddsInput.className =
      "form-control form-control-small justify-content-start"; // Set the class attribute as needed

    // Create a label for the odds input
    const oddsLabel = document.createElement("label");
    oddsLabel.htmlFor = "odds" + oddsCount; // Set the label's "for" attribute to match the input's id
    oddsLabel.textContent = "Odds " + oddsCount; // Set the label text
    oddsLabel.className = "form-label"; // Set the label's class attribute

    // Append the label and input elements to the oddsContainer
    oddsContainer.appendChild(oddsLabel);
    oddsContainer.appendChild(oddsInput);
  }
}

// Function to handle the "Calculate" button click
function handleCalculateClick() {
  // Clear the oddsValues array before populating it again
  oddsValues.length = 0;

  // Loop through the odds input fields and add their values to the array
  for (let i = 1; i <= oddsCount; i++) {
    const oddsInput = document.getElementById("odds" + i);
    const oddsValue = parseFloat(oddsInput.value); // Convert the input value to a number
    oddsValues.push(oddsValue);
  }
}

// Add an event listener to the "Add Odds" button
const addOddsButton = document.querySelector(".btn-standard");
addOddsButton.addEventListener("click", handleAddOddsClick);

// Add an event listener to the "Calculate" button
const calculateButton = document.querySelector(".btn-standard.calculate");
calculateButton.addEventListener("click", handleCalculateClick);

// Prevent the form submission when the main "Calculate" button is clicked
form.addEventListener("submit", function (event) {
  event.preventDefault();
  // Add your calculation logic here
});
