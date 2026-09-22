async function getWeather() {
  // Get city name from input
  const city = document.getElementById("cityInput").value.trim();

  // Get error message element
  const errorElement = document.getElementById("error");

  // Check if city input is empty
  if (!city) {
    errorElement.textContent = "Please enter a city name.";
    return;
  }

  // Clear previous error
  errorElement.textContent = "";

  try {
    // Send request to FastAPI backend
    const response = await fetch(`/weather/${encodeURIComponent(city)}`);

    // Convert response to JSON
    const data = await response.json();

    // Check if backend returned an error
    if (!response.ok) {
      throw new Error(data.detail?.message || "City not found");
    }

    // Update city name
    document.getElementById("city").textContent = data.city;

    // Update temperature
    document.getElementById("temperature").textContent = data.temperature;

    // Update temperature with °C
    document.getElementById("temperature2").textContent =
      data.temperature + "°C";

    // Update humidity
    document.getElementById("humidity").textContent = data.humidity + "%";

    // Update weather condition
    document.getElementById("condition").textContent = data.condition;
  } catch (err) {
    // Display error message
    errorElement.textContent = err.message;
  }
}
