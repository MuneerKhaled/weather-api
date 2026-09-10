async function getWeather() {
  const city = document.getElementById("cityInput").value.trim();

  const error = document.getElementById("error");

  if (!city) {
    error.textContent = "Please enter a city name.";
    return;
  }

  error.textContent = "";

  try {
    const response = await fetch(`/weather/${encodeURIComponent(city)}`);

    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.detail?.message || "City not found");
    }

    document.getElementById("city").textContent = data.city;

    document.getElementById("temperature").textContent = data.temperature;

    document.getElementById("temperature2").textContent =
      data.temperature + "°C";

    document.getElementById("humidity").textContent = data.humidity + "%";

    document.getElementById("condition").textContent = data.condition;
  } catch (error) {
    error.textContent = error.message;
  }
}
