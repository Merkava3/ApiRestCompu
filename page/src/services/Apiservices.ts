async function fetchApiData(url: string): Promise<void> {
  try {
    const response = await fetch(url);

    // Muestra el status code
    console.log("HTTP Status Code:", response.status);

    // Verifica si la respuesta fue exitosa (status 200-299)
    if (!response.ok) {
      throw new Error(`Error en la petición: ${response.status} ${response.statusText}`);
    }

    // Obtiene y muestra el contenido JSON
    const data = await response.json();
    console.log("Respuesta JSON:", data);
  } catch (error) {
    console.error("Ocurrió un error:", error);
  }
}

// Usamos una API pública de prueba
const apiUrl = "https://apirestcompu.onrender.com/api/v1/servicios";

// Ejecutamos la función
fetchApiData(apiUrl);