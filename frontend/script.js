async function getWeather() {
  // Get city name from input
  const city = document.getElementById("cityInput").value.trim();

  // Get error element
  const errorElement = document.getElementById("error");

  // Check if city is empty
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

    // Check for backend error
    if (!response.ok) {
      throw new Error(data.detail?.message || "City not found");
    }

    // Display city
    document.getElementById("city").textContent = data.city;

    // Display temperature
    document.getElementById("temperature").textContent = data.temperature;

    // Display temperature with Celsius
    document.getElementById("temperature2").textContent =
      `${data.temperature}°C`;

    // Display humidity
    document.getElementById("humidity").textContent = `${data.humidity}%`;

    // Display weather condition
    document.getElementById("condition").textContent = data.condition;
  } catch (err) {
    // Display error
    errorElement.textContent = err.message;
  }
}
